"""Smart Suggestion Engine.

Orchestrates multiple analyzers to generate intelligent suggestions.
"""

import pandas as pd

from modules.ai.suggestions.analyzers.budgets import (
    BudgetOverrunAnalyzer,
    EmptyBudgetAnalyzer,
    SavingsOpportunityAnalyzer,
)
from modules.ai.suggestions.analyzers.categories import (
    CategoryConsolidationAnalyzer,
    FrequentPatternAnalyzer,
    MissingRuleAnalyzer,
    UncategorizedAnalyzer,
)
from modules.ai.suggestions.analyzers.income import IncomeVariationAnalyzer
from modules.ai.suggestions.analyzers.members import BeneficiaryAnalyzer, UnknownMemberAnalyzer
from modules.ai.suggestions.analyzers.patterns import (
    DuplicateAnalyzer,
    LargeAmountAnalyzer,
    RecurringPatternAnalyzer,
    SpendingAnomalyAnalyzer,
    SubscriptionAnalyzer,
)
from modules.ai.suggestions.analyzers.tags import MissingTagAnalyzer
from modules.ai.suggestions.base import Suggestion
from modules.ai.suggestions.models import AnalysisContext


class SuggestionEngine:
    """Engine for generating intelligent suggestions based on data analysis.

    This class orchestrates multiple analyzers to provide comprehensive
    recommendations for financial optimization.

    Example:
        engine = SuggestionEngine(transactions_df, rules_df, budgets_df, members_df)
        suggestions = engine.analyze_all()

        # Or analyze specific areas
        category_suggestions = engine.analyze_categories()
        budget_suggestions = engine.analyze_budgets()
    """

    def __init__(
        self,
        transactions_df: pd.DataFrame,
        rules_df: pd.DataFrame,
        budgets_df: pd.DataFrame,
        members_df: pd.DataFrame,
    ):
        """Initialize suggestion engine.

        Args:
            transactions_df: All transactions
            rules_df: Learning rules
            budgets_df: Budget definitions
            members_df: Members list
        """
        self.context = AnalysisContext(
            transactions=transactions_df,
            rules=rules_df,
            budgets=budgets_df,
            members=members_df,
        )

        # Initialize all analyzers
        self._analyzers = {
            "categories": [
                UncategorizedAnalyzer(),
                FrequentPatternAnalyzer(),
                MissingRuleAnalyzer(),
                CategoryConsolidationAnalyzer(),
            ],
            "budgets": [
                BudgetOverrunAnalyzer(),
                EmptyBudgetAnalyzer(),
                SavingsOpportunityAnalyzer(),
            ],
            "members": [
                UnknownMemberAnalyzer(),
                BeneficiaryAnalyzer(),
            ],
            "patterns": [
                DuplicateAnalyzer(),
                SpendingAnomalyAnalyzer(),
                SubscriptionAnalyzer(),
                LargeAmountAnalyzer(),
                RecurringPatternAnalyzer(),
            ],
            "income": [
                IncomeVariationAnalyzer(),
            ],
            "tags": [
                MissingTagAnalyzer(),
            ],
        }

    def analyze_all(self) -> list[Suggestion]:
        """Run all analyzers and return combined suggestions.

        Returns:
            List of suggestions sorted by impact score (descending)
        """
        all_suggestions: list[Suggestion] = []

        if not self.context.has_transactions():
            return all_suggestions

        # Run all analyzer groups
        for group_name, analyzers in self._analyzers.items():
            for analyzer in analyzers:
                suggestions = analyzer.run(self.context)
                all_suggestions.extend(suggestions)

        # Sort by impact score (descending)
        all_suggestions.sort(key=lambda x: x.impact_score, reverse=True)

        return all_suggestions

    def analyze_categories(self) -> list[Suggestion]:
        """Run only category-related analyzers.

        Returns:
            List of category suggestions
        """
        return self._run_analyzer_group("categories")

    def analyze_budgets(self) -> list[Suggestion]:
        """Run only budget-related analyzers.

        Returns:
            List of budget suggestions
        """
        return self._run_analyzer_group("budgets")

    def analyze_members(self) -> list[Suggestion]:
        """Run only member-related analyzers.

        Returns:
            List of member suggestions
        """
        return self._run_analyzer_group("members")

    def analyze_patterns(self) -> list[Suggestion]:
        """Run only pattern detection analyzers.

        Returns:
            List of pattern suggestions
        """
        return self._run_analyzer_group("patterns")

    def analyze_income(self) -> list[Suggestion]:
        """Run only income-related analyzers.

        Returns:
            List of income suggestions
        """
        return self._run_analyzer_group("income")

    def analyze_tags(self) -> list[Suggestion]:
        """Run only tag-related analyzers.

        Returns:
            List of tag suggestions
        """
        return self._run_analyzer_group("tags")

    def _run_analyzer_group(self, group_name: str) -> list[Suggestion]:
        """Run a specific group of analyzers.

        Args:
            group_name: Name of the analyzer group

        Returns:
            List of suggestions from that group
        """
        suggestions: list[Suggestion] = []

        analyzers = self._analyzers.get(group_name, [])
        for analyzer in analyzers:
            suggestions.extend(analyzer.run(self.context))

        # Sort by impact score
        suggestions.sort(key=lambda x: x.impact_score, reverse=True)

        return suggestions

    def get_analyzer_names(self) -> dict[str, list[str]]:
        """Get names of all registered analyzers.

        Returns:
            Dictionary mapping group names to analyzer names
        """
        return {
            group: [a.name for a in analyzers] for group, analyzers in self._analyzers.items()
        }


# Backward compatibility alias
SmartSuggestionEngine = SuggestionEngine


# Convenience functions for backward compatibility
def get_smart_suggestions(
    transactions_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    budgets_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> list[Suggestion]:
    """Get intelligent suggestions based on data analysis.

    Args:
        transactions_df: All transactions
        rules_df: Learning rules
        budgets_df: Budget definitions
        members_df: Members list

    Returns:
        List of Suggestion objects sorted by impact
    """
    engine = SuggestionEngine(transactions_df, rules_df, budgets_df, members_df)
    return engine.analyze_all()


def get_suggestions_by_type(suggestions: list[Suggestion], suggestion_type: str) -> list[Suggestion]:
    """Filter suggestions by type.

    Args:
        suggestions: List of suggestions
        suggestion_type: Type to filter by

    Returns:
        Filtered list of suggestions
    """
    return [s for s in suggestions if s.type == suggestion_type]
