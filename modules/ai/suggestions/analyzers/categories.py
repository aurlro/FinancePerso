"""Category-related analyzers."""

import pandas as pd

from modules.ai.suggestions.base import BaseAnalyzer
from modules.ai.suggestions.models import AnalysisContext, Priority, Suggestion, SuggestionType


class UncategorizedAnalyzer(BaseAnalyzer):
    """Suggest creating rules for frequently uncategorized transactions."""

    def __init__(self):
        super().__init__("UncategorizedAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []
        pending = self._get_pending_transactions(context.transactions)

        if pending.empty:
            return suggestions

        # Group by label and count
        label_counts = pending["label"].value_counts().head(5)

        for label, count in label_counts.items():
            if count >= 3:  # Only suggest if appears multiple times
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("uncat", hash(label) % 10000),
                        type=SuggestionType.RULE.value,
                        priority=Priority.HIGH.value,
                        title=(
                            f"📋 {count} transactions non catégorisées : '{label[:40]}...'"
                            if len(label) > 40
                            else f"📋 {count} transactions non catégorisées : '{label}'"
                        ),
                        description=(
                            f"Cette transaction apparaît {count} fois sans catégorie. "
                            f"Créez une règle pour la catégoriser automatiquement."
                        ),
                        action_label="Créer une règle",
                        action_data={
                            "pattern": label[:30],
                            "type": "create_rule",
                            "suggested_category": self._guess_category(label),
                        },
                        impact_score=min(count * 10, 100),
                        auto_fixable=False,
                    )
                )

        return suggestions

    def _guess_category(self, label: str) -> str:
        """Guess category from label (simple heuristic)."""
        label_lower = label.lower()
        keywords = {
            "restaurant": "Restaurants",
            "supermarche": "Alimentation",
            "supermarket": "Alimentation",
            "carburant": "Transport",
            "essence": "Transport",
            "pharmacie": "Santé",
            "docteur": "Santé",
            "cinema": "Loisirs",
            "netflix": "Abonnements",
            "spotify": "Abonnements",
        }
        for keyword, category in keywords.items():
            if keyword in label_lower:
                return category
        return "Inconnu"


class FrequentPatternAnalyzer(BaseAnalyzer):
    """Analyze frequent transaction patterns for rule creation."""

    def __init__(self):
        super().__init__("FrequentPatternAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []
        validated = self._get_validated_transactions(context.transactions)

        if validated.empty:
            return suggestions

        # Find merchants/labels that appear frequently with same category
        grouped = (
            validated.groupby(["label", "category_validated"]).size().reset_index(name="count")
        )
        frequent = grouped[grouped["count"] >= 5].sort_values("count", ascending=False).head(5)

        # Check if these already have rules
        existing_patterns = (
            set(context.rules["pattern"].str.lower().tolist())
            if not context.rules.empty
            else set()
        )

        for _, row in frequent.iterrows():
            pattern_lower = row["label"].lower()
            if pattern_lower not in existing_patterns and len(row["label"]) > 5:
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("freq", hash(row["label"]) % 10000),
                        type=SuggestionType.RULE.value,
                        priority=Priority.MEDIUM.value,
                        title=(
                            f"🔄 Pattern fréquent détecté : '{row['label'][:40]}...'"
                            if len(row["label"]) > 40
                            else f"🔄 Pattern fréquent : '{row['label']}'"
                        ),
                        description=(
                            f"{row['count']} transactions avec la catégorie "
                            f"'{row['category_validated']}'. Une règle permettrait d'automatiser."
                        ),
                        action_label="Créer règle auto",
                        action_data={
                            "pattern": row["label"][:30],
                            "category": row["category_validated"],
                            "type": "create_rule",
                        },
                        impact_score=min(row["count"] * 5, 80),
                        auto_fixable=True,
                    )
                )

        return suggestions


class MissingRuleAnalyzer(BaseAnalyzer):
    """Analyze transactions that could benefit from new rules."""

    def __init__(self):
        super().__init__("MissingRuleAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []
        validated = self._get_validated_transactions(context.transactions)

        if validated.empty or context.rules.empty:
            return suggestions

        # Find labels that are manually categorized but have no rule
        existing_patterns = set(context.rules["pattern"].str.lower().tolist())

        # Get top manually categorized labels
        manual_cats = validated[validated["category_validated"] != "Inconnu"]
        if manual_cats.empty:
            return suggestions

        label_cat_pairs = (
            manual_cats.groupby(["label", "category_validated"]).size().reset_index(name="count")
        )

        for _, row in label_cat_pairs.head(10).iterrows():
            pattern = row["label"][:20]  # Use prefix as pattern
            if pattern.lower() not in existing_patterns and row["count"] >= 3:
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("missing_rule", hash(row["label"]) % 10000),
                        type=SuggestionType.RULE.value,
                        priority=Priority.MEDIUM.value,
                        title=f"📝 Règle manquante : '{pattern}...' → {row['category_validated']}",
                        description=f"{row['count']} transactions manuellement catégorisées. Une règle automatiserait cela.",
                        action_label="Créer règle",
                        action_data={
                            "pattern": pattern,
                            "category": row["category_validated"],
                            "type": "create_rule",
                        },
                        impact_score=min(row["count"] * 8, 75),
                        auto_fixable=True,
                    )
                )
                break  # Only suggest one to avoid overwhelming

        return suggestions


class CategoryConsolidationAnalyzer(BaseAnalyzer):
    """Suggest consolidating similar categories."""

    def __init__(self):
        super().__init__("CategoryConsolidationAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        categories = context.transactions["category_validated"].unique()

        # Find similar category names
        similar_pairs = []
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i + 1 :]:
                if self._categories_similar(cat1, cat2):
                    similar_pairs.append((cat1, cat2))

        for cat1, cat2 in similar_pairs[:2]:
            count1 = len(context.transactions[context.transactions["category_validated"] == cat1])
            count2 = len(context.transactions[context.transactions["category_validated"] == cat2])

            suggestions.append(
                Suggestion(
                    id=self._generate_id("consolidate", hash(cat1 + cat2) % 10000),
                    type=SuggestionType.CATEGORY.value,
                    priority=Priority.LOW.value,
                    title=f"🏷️ Catégories similaires : '{cat1}' et '{cat2}'",
                    description=f"Ces catégories ont des noms similaires ({count1} et {count2} transactions). Envisagez de les fusionner.",
                    action_label="Fusionner",
                    action_data={"source": cat1, "target": cat2, "type": "merge_categories"},
                    impact_score=40,
                    auto_fixable=False,
                )
            )

        return suggestions

    def _categories_similar(self, cat1: str, cat2: str) -> bool:
        """Check if two category names are similar.

        Args:
            cat1: First category name
            cat2: Second category name

        Returns:
            True if categories are similar
        """
        if cat1 == cat2:
            return False

        # Simple similarity: check if one is substring of other
        # or if they share common prefix
        c1, c2 = cat1.lower(), cat2.lower()

        if len(c1) > 3 and len(c2) > 3:
            # Check common prefix (first 4 chars)
            if c1[:4] == c2[:4]:
                return True

            # Check if one contains the other
            if c1 in c2 or c2 in c1:
                return True

        return False
