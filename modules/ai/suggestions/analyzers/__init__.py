"""Analyzers for smart suggestions.

Each analyzer focuses on a specific aspect of financial data analysis.
"""

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
from modules.ai.suggestions.analyzers.members import (
    BeneficiaryAnalyzer,
    UnknownMemberAnalyzer,
)
from modules.ai.suggestions.analyzers.patterns import (
    DuplicateAnalyzer,
    LargeAmountAnalyzer,
    RecurringPatternAnalyzer,
    SpendingAnomalyAnalyzer,
    SubscriptionAnalyzer,
)
from modules.ai.suggestions.analyzers.tags import MissingTagAnalyzer

__all__ = [
    # Categories
    "UncategorizedAnalyzer",
    "FrequentPatternAnalyzer",
    "MissingRuleAnalyzer",
    "CategoryConsolidationAnalyzer",
    # Budgets
    "BudgetOverrunAnalyzer",
    "EmptyBudgetAnalyzer",
    "SavingsOpportunityAnalyzer",
    # Members
    "UnknownMemberAnalyzer",
    "BeneficiaryAnalyzer",
    # Patterns
    "DuplicateAnalyzer",
    "SpendingAnomalyAnalyzer",
    "SubscriptionAnalyzer",
    "LargeAmountAnalyzer",
    "RecurringPatternAnalyzer",
    # Income
    "IncomeVariationAnalyzer",
    # Tags
    "MissingTagAnalyzer",
]
