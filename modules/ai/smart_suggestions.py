"""Smart Suggestions Engine for FinancePerso.

DEPRECATED: This module has been restructured into a package.
Please use modules.ai.suggestions instead.

Old import:
    from modules.ai.smart_suggestions import SmartSuggestionEngine, Suggestion

New import:
    from modules.ai.suggestions import SuggestionEngine, Suggestion
    from modules.ai.suggestions.analyzers.categories import UncategorizedAnalyzer
"""

import warnings

# Import from new modular structure for backward compatibility
from modules.ai.suggestions import Suggestion, SuggestionEngine
from modules.ai.suggestions.engine import get_smart_suggestions, get_suggestions_by_type
from modules.ai.suggestions.models import AnalysisContext, Priority, SuggestionType

# Issue deprecation warning
warnings.warn(
    "modules.ai.smart_suggestions is deprecated. Use modules.ai.suggestions instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Backward compatibility alias
SmartSuggestionEngine = SuggestionEngine

__all__ = [
    "SmartSuggestionEngine",
    "SuggestionEngine",
    "Suggestion",
    "SuggestionType",
    "Priority",
    "AnalysisContext",
    "get_smart_suggestions",
    "get_suggestions_by_type",
]
