"""
Smart Suggestions module (compatibility layer).

Redirects to the new suggestions engine.
"""

from modules.ai.suggestions import Suggestion, SuggestionEngine
from modules.ai.suggestions.models import Priority, SuggestionType

__all__ = ["Suggestion", "SuggestionEngine", "SuggestionType", "Priority", "get_smart_suggestions"]


def get_smart_suggestions(df, rules_df=None, budgets_df=None, members_df=None, max_suggestions=10):
    """
    Get smart suggestions for the given data.

    Args:
        df: Transactions DataFrame
        rules_df: Rules DataFrame (optional)
        budgets_df: Budgets DataFrame (optional)
        members_df: Members DataFrame (optional)
        max_suggestions: Maximum number of suggestions to return

    Returns:
        List of Suggestion objects
    """
    if df is None or df.empty:
        return []

    engine = SuggestionEngine(df, rules_df, budgets_df, members_df)
    suggestions = engine.analyze_all()

    # Sort by priority and limit results
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: priority_order.get(x.priority, 3))

    return suggestions[:max_suggestions]
