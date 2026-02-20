"""Tag-related analyzers."""

from modules.ai.suggestions.base import BaseAnalyzer
from modules.ai.suggestions.models import AnalysisContext, Priority, Suggestion, SuggestionType


class MissingTagAnalyzer(BaseAnalyzer):
    """Suggest adding tags to untagged transactions."""

    def __init__(self):
        super().__init__("MissingTagAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        # Check if tags column exists
        if "tags" not in context.transactions.columns:
            return suggestions

        untagged = context.transactions[
            (context.transactions["tags"].isna()) | (context.transactions["tags"] == "")
        ]

        if len(untagged) < 10:
            return suggestions

        # Group by category
        untagged_by_cat = untagged.groupby("category_validated").size().sort_values(ascending=False)

        for category, count in untagged_by_cat.head(2).items():
            if category == "Inconnu":
                continue

            suggestions.append(
                Suggestion(
                    id=self._generate_id("tags", hash(category) % 10000),
                    type=SuggestionType.CATEGORY.value,
                    priority=Priority.LOW.value,
                    title=f"🏷️ Transactions sans tags : {category} ({count})",
                    description=f"{count} transactions dans '{category}' n'ont pas de tags. Les tags améliorent l'analyse.",
                    action_label="Ajouter tags",
                    action_data={"category": category, "type": "add_tags"},
                    impact_score=min(count * 2, 40),
                    auto_fixable=False,
                )
            )

        return suggestions
