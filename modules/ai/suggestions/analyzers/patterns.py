"""Pattern detection analyzers."""

from datetime import datetime

import pandas as pd

from modules.ai.suggestions.base import BaseAnalyzer
from modules.ai.suggestions.models import AnalysisContext, Priority, Suggestion, SuggestionType


class DuplicateAnalyzer(BaseAnalyzer):
    """Detect potential duplicate transactions."""

    def __init__(self):
        super().__init__("DuplicateAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        # Group by date, label, amount
        grouped = (
            context.transactions.groupby(["date", "label", "amount"])
            .size()
            .reset_index(name="count")
        )
        duplicates = grouped[grouped["count"] > 1]

        if not duplicates.empty:
            total_duplicates = int(duplicates["count"].sum() - len(duplicates))
            suggestions.append(
                Suggestion(
                    id="potential_duplicates",
                    type=SuggestionType.DUPLICATE.value,
                    priority=Priority.HIGH.value if total_duplicates > 5 else Priority.MEDIUM.value,
                    title=f"⚠️ {total_duplicates} transaction(s) potentiellement en double",
                    description="Certaines transactions apparaissent plusieurs fois avec la même date, libellé et montant. Vérifiez s'il s'agit de vrais doublons.",
                    action_label="Voir les doublons",
                    action_data={"type": "view_duplicates", "count": total_duplicates},
                    impact_score=min(total_duplicates * 15, 100),
                    auto_fixable=False,
                )
            )

        return suggestions


class SpendingAnomalyAnalyzer(BaseAnalyzer):
    """Detect unusual spending patterns."""

    def __init__(self):
        super().__init__("SpendingAnomalyAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        expenses = self._get_expenses(context.transactions)

        if expenses.empty:
            return suggestions

        # Find categories with sudden spike compared to average
        expenses = expenses.copy()
        expenses["month"] = expenses["date"].str[:7]
        current_month = datetime.now().strftime("%Y-%m")

        current_expenses = expenses[expenses["month"] == current_month]

        if len(current_expenses) < 5:
            return suggestions

        # Calculate category averages (excluding current month)
        historical = expenses[expenses["month"] != current_month]

        if historical.empty:
            return suggestions

        cat_averages = historical.groupby("category_validated")["amount"].mean().abs()
        current_totals = current_expenses.groupby("category_validated")["amount"].sum().abs()

        for category, current_total in current_totals.items():
            avg_monthly = cat_averages.get(category, 0)

            if avg_monthly > 0 and current_total > avg_monthly * 2:
                spike_pct = int((current_total / avg_monthly - 1) * 100)

                suggestions.append(
                    Suggestion(
                        id=self._generate_id("spike", hash(category) % 10000),
                        type=SuggestionType.PATTERN.value,
                        priority=Priority.MEDIUM.value,
                        title=f"📈 Pic de dépenses : {category} (+{spike_pct}%)",
                        description=f"Ce mois : {current_total:.0f}€ vs moyenne : {avg_monthly:.0f}€. Vérifiez s'il s'agit de dépenses exceptionnelles.",
                        action_label="Explorer",
                        action_data={"category": category, "type": "explore_category"},
                        impact_score=min(spike_pct, 100),
                        auto_fixable=False,
                    )
                )
                break  # Only one spike suggestion

        return suggestions


class SubscriptionAnalyzer(BaseAnalyzer):
    """Detect subscription price increases."""

    def __init__(self):
        super().__init__("SubscriptionAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        # Find recurring transactions (same label, monthly, similar amount)
        expenses = self._get_expenses(context.transactions).copy()

        if len(expenses) < 10:
            return suggestions

        # Group by label and analyze price evolution
        expenses["month"] = expenses["date"].str[:7]
        expenses["amount_abs"] = expenses["amount"].abs()

        # Find labels with multiple months
        label_months = expenses.groupby("label")["month"].nunique()
        recurring_labels = label_months[label_months >= 3].index

        for label in recurring_labels[:3]:  # Limit to 3
            label_df = expenses[expenses["label"] == label]
            monthly_avg = label_df.groupby("month")["amount_abs"].mean()

            if len(monthly_avg) >= 3:
                # Check for increasing trend
                first_avg = monthly_avg.iloc[0]
                last_avg = monthly_avg.iloc[-1]

                if last_avg > first_avg * 1.15:  # 15% increase
                    increase_pct = int((last_avg / first_avg - 1) * 100)

                    suggestions.append(
                        Suggestion(
                            id=self._generate_id("sub_inc", hash(label) % 10000),
                            type=SuggestionType.PATTERN.value,
                            priority=Priority.HIGH.value,
                            title=(
                                f"💳 Augmentation d'abonnement : {label[:40]}..."
                                if len(label) > 40
                                else f"💳 Augmentation : {label}"
                            ),
                            description=f"L'abonnement a augmenté de {increase_pct}% ({first_avg:.0f}€ → {last_avg:.0f}€). Vérifiez si c'est justifié ou négociez.",
                            action_label="Voir l'évolution",
                            action_data={"label": label, "type": "view_subscription"},
                            impact_score=min(increase_pct, 100),
                            auto_fixable=False,
                        )
                    )

        return suggestions


class LargeAmountAnalyzer(BaseAnalyzer):
    """Detect unusually large transactions."""

    def __init__(self):
        super().__init__("LargeAmountAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        expenses = self._get_expenses(context.transactions)

        if len(expenses) < 10:
            return suggestions

        # Calculate percentiles per category
        for category in expenses["category_validated"].unique():
            if category == "Inconnu":
                continue

            cat_expenses = expenses[expenses["category_validated"] == category]["amount"].abs()

            if len(cat_expenses) < 5:
                continue

            q90 = cat_expenses.quantile(0.90)
            q50 = cat_expenses.median()

            # Find transactions above 90th percentile
            large_txns = expenses[
                (expenses["category_validated"] == category)
                & (expenses["amount"].abs() > q90 * 1.5)
                & (expenses["amount"].abs() > q50 * 3)  # At least 3x median
            ]

            if not large_txns.empty:
                txn = large_txns.iloc[0]  # Take the most recent
                amount = abs(txn["amount"])

                suggestions.append(
                    Suggestion(
                        id=self._generate_id("large", hash(str(txn["id"])) % 10000),
                        type=SuggestionType.PATTERN.value,
                        priority=Priority.MEDIUM.value,
                        title=f"💰 Montant inhabituel : {amount:.0f}€ ({category})",
                        description=f"Cette transaction est anormalement élevée pour la catégorie '{category}'. Vérifiez qu'elle est correctement catégorisée.",
                        action_label="Vérifier",
                        action_data={"transaction_id": txn["id"], "type": "view_transaction"},
                        impact_score=min(int(amount / q50), 100),
                        auto_fixable=False,
                    )
                )
                break  # Only one suggestion of this type

        return suggestions


class RecurringPatternAnalyzer(BaseAnalyzer):
    """Detect recurring monthly patterns that aren't tracked."""

    def __init__(self):
        super().__init__("RecurringPatternAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        expenses = self._get_expenses(context.transactions).copy()

        if len(expenses) < 20:
            return suggestions

        expenses["month"] = expenses["date"].str[:7]

        # Group by label and check monthly recurrence
        label_analysis = (
            expenses.groupby("label")
            .agg({"month": "nunique", "amount": ["mean", "std"], "date": "count"})
            .reset_index()
        )

        label_analysis.columns = ["label", "unique_months", "avg_amount", "amount_std", "count"]

        # Find labels that appear regularly with similar amounts
        recurring = label_analysis[
            (label_analysis["unique_months"] >= 3)
            & (label_analysis["count"] >= 3)
            & (label_analysis["amount_std"] < abs(label_analysis["avg_amount"]) * 0.2)
        ]

        for _, row in recurring.head(2).iterrows():
            label = row["label"]
            avg_amount = abs(row["avg_amount"])

            # Check if already has a rule
            has_rule = False
            if context.has_rules():
                has_rule = any(label.lower() in str(p).lower() for p in context.rules["pattern"])

            if not has_rule and len(label) > 5:
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("recurring", hash(label) % 10000),
                        type=SuggestionType.RULE.value,
                        priority=Priority.MEDIUM.value,
                        title=(
                            f"🔄 Dépense récurrente détectée : {label[:40]}..."
                            if len(label) > 40
                            else f"🔄 Récurrente : {label}"
                        ),
                        description=f"Environ {avg_amount:.0f}€/mois sur {int(row['unique_months'])} mois. Créez une règle pour suivre automatiquement.",
                        action_label="Créer règle",
                        action_data={
                            "pattern": label[:25],
                            "type": "create_rule",
                        },
                        impact_score=min(int(row["unique_months"]) * 15, 85),
                        auto_fixable=True,
                    )
                )

        return suggestions
