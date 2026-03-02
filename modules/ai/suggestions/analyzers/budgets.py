"""Budget-related analyzers."""

from datetime import datetime

import pandas as pd

from modules.ai.suggestions.base import BaseAnalyzer
from modules.ai.suggestions.models import AnalysisContext, Priority, Suggestion, SuggestionType


class BudgetOverrunAnalyzer(BaseAnalyzer):
    """Analyze budget overruns and suggest adjustments."""

    def __init__(self):
        super().__init__("BudgetOverrunAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_budgets() or not context.has_transactions():
            return suggestions

        # Calculate spending per category for current month
        current_month = datetime.now().strftime("%Y-%m")
        month_df = context.transactions[
            (context.transactions["date"].str.startswith(current_month))
            & (context.transactions["amount"] < 0)  # Expenses only
        ]

        spending_by_cat = month_df.groupby("category_validated")["amount"].sum().abs()

        for _, budget_row in context.budgets.iterrows():
            category = budget_row["category"]
            budget_amount = budget_row["amount"]
            spent = spending_by_cat.get(category, 0)

            if spent > budget_amount * 1.1:  # Over budget by 10%
                overspend_pct = int((spent / budget_amount - 1) * 100)
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("budget", hash(category) % 10000),
                        type=SuggestionType.BUDGET.value,
                        priority=(
                            Priority.HIGH.value if overspend_pct > 50 else Priority.MEDIUM.value
                        ),
                        title=f"💰 Dépassement budget : {category}",
                        description=f"Dépensé : {spent:.0f}€ / Budget : {budget_amount:.0f}€ (+{overspend_pct}%). Ajustez votre budget ou surveillez vos dépenses.",
                        action_label="Ajuster le budget",
                        action_data={
                            "category": category,
                            "current_budget": budget_amount,
                            "suggested_budget": int(spent * 1.1),
                            "type": "adjust_budget",
                        },
                        impact_score=min(overspend_pct, 100),
                        auto_fixable=False,
                    )
                )
            elif spent < budget_amount * 0.5:  # Under budget by 50%
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("budget_under", hash(category) % 10000),
                        type=SuggestionType.BUDGET.value,
                        priority=Priority.LOW.value,
                        title=f"💡 Budget surévalué : {category}",
                        description=f"Vous n'utilisez que {spent:.0f}€ sur {budget_amount:.0f}€. Envisagez de réduire ce budget.",
                        action_label="Voir détails",
                        action_data={"category": category, "type": "view_budget"},
                        impact_score=30,
                        auto_fixable=False,
                    )
                )

        return suggestions


class EmptyBudgetAnalyzer(BaseAnalyzer):
    """Find budget categories with no transactions."""

    def __init__(self):
        super().__init__("EmptyBudgetAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_budgets():
            return suggestions

        current_month = datetime.now().strftime("%Y-%m")
        month_df = context.transactions[
            (context.transactions["date"].str.startswith(current_month))
            & (context.transactions["amount"] < 0)
        ]

        used_categories = set(month_df["category_validated"].unique())

        for _, budget in context.budgets.iterrows():
            category = budget["category"]
            if category not in used_categories and category != "Inconnu":
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("empty_budget", hash(category) % 10000),
                        type=SuggestionType.BUDGET.value,
                        priority=Priority.LOW.value,
                        title=f"💤 Catégorie inactive : {category}",
                        description=f"Budget défini ({budget['amount']:.0f}€) mais aucune dépense ce mois. Surveillez ou ajustez le budget.",
                        action_label="Voir budget",
                        action_data={"category": category, "type": "view_budget"},
                        impact_score=25,
                        auto_fixable=False,
                    )
                )

        return suggestions


class SavingsOpportunityAnalyzer(BaseAnalyzer):
    """Detect potential savings opportunities."""

    def __init__(self):
        super().__init__("SavingsOpportunityAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        # Analyze recurring expenses to find savings opportunities
        expenses = self._get_expenses(context.transactions)

        if expenses.empty:
            return suggestions

        # Find subscriptions (regular monthly payments)
        recurring = self._find_recurring_payments(expenses)

        for label, monthly_amount in recurring.items():
            if monthly_amount > 50:  # Significant amount
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("savings", hash(label) % 10000),
                        type=SuggestionType.SAVINGS.value,
                        priority=Priority.MEDIUM.value,
                        title=f"💸 Dépense récurrente : '{label[:30]}...' ({monthly_amount:.0f}€/mois)",
                        description=f"Cette dépense revient tous les mois. Vérifiez si vous pouvez la réduire ou la supprimer.",
                        action_label="Analyser",
                        action_data={
                            "label": label,
                            "amount": monthly_amount,
                            "type": "analyze_recurring",
                        },
                        impact_score=min(int(monthly_amount), 80),
                        auto_fixable=False,
                    )
                )

        # Check for duplicate subscriptions
        subscription_keywords = ["netflix", "spotify", "amazon", "disney", "canal", "bein"]
        found_subscriptions = []

        for keyword in subscription_keywords:
            matching = expenses[expenses["label"].str.lower().str.contains(keyword, na=False)]
            if not matching.empty:
                total = matching["amount"].sum()
                found_subscriptions.append((keyword, total))

        # If multiple streaming services, suggest review
        streaming_count = sum(
            1 for k, _ in found_subscriptions if k in ["netflix", "spotify", "disney", "amazon"]
        )
        if streaming_count >= 3:
            total_streaming = sum(
                v for k, v in found_subscriptions if k in ["netflix", "spotify", "disney", "amazon"]
            )
            suggestions.append(
                Suggestion(
                    id="savings_multiple_streaming",
                    type=SuggestionType.SAVINGS.value,
                    priority=Priority.MEDIUM.value,
                    title=f"📺 Multiples abonnements streaming ({streaming_count})",
                    description=f"Vous avez {streaming_count} abonnements streaming pour un total de {abs(total_streaming):.0f}€. Envisagez de les rationaliser.",
                    action_label="Voir détails",
                    action_data={"type": "view_subscriptions"},
                    impact_score=60,
                    auto_fixable=False,
                )
            )

        return suggestions[:3]  # Limit to top 3

    def _find_recurring_payments(self, expenses: pd.DataFrame) -> dict[str, float]:
        """Find recurring monthly payments.

        Args:
            expenses: Expenses DataFrame

        Returns:
            Dictionary of label -> monthly_amount
        """
        if expenses.empty or "date" not in expenses.columns:
            return {}

        # Group by label and count occurrences in recent months
        recent = expenses.copy()
        recent["month"] = pd.to_datetime(recent["date"]).dt.to_period("M")

        # Count months with this label
        label_months = recent.groupby("label")["month"].nunique()
        recurring_labels = label_months[label_months >= 3].index

        result = {}
        for label in recurring_labels:
            label_tx = recent[recent["label"] == label]
            # Average monthly amount
            monthly_avg = abs(label_tx["amount"].sum()) / label_months[label]
            if monthly_avg > 10:  # Not too small
                result[label] = monthly_avg

        return result
