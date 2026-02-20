"""Smart Suggestions module.

Provides intelligent analysis and recommendations for financial data.

Example:
    from modules.ai.suggestions.engine import SuggestionEngine
    from modules.ai.suggestions.analyzers.categories import UncategorizedAnalyzer
    
    engine = SuggestionEngine(df)
    suggestions = engine.analyze_all()
"""

from modules.ai.suggestions.base import BaseAnalyzer, Suggestion
from modules.ai.suggestions.engine import SuggestionEngine
from modules.ai.suggestions.models import SuggestionType, Priority

__all__ = [
    "BaseAnalyzer",
    "Suggestion",
    "SuggestionEngine",
    "SuggestionType",
    "Priority",
]
