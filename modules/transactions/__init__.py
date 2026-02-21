"""
Package modules.transactions - Gestion des transactions.
========================================================

Ce package fournit les outils pour la gestion et la catégorisation
des transactions financières.

Usage:
    from modules.transactions import categorize_transaction
    from modules.transactions.constants import PFCV2_CATEGORIES
    from modules.transactions.services import CategorizationService
"""

from modules.transactions.constants import (
    PFCV2_CATEGORIES,
    CategorizationMethod,
    CategoryType,
    HEURISTIC_PATTERNS,
    get_category_type,
    is_expense_category,
    is_income_category,
    format_category,
    parse_category,
)

from modules.transactions.services import (
    CategorizationService,
    CategorizationServiceResult,
    categorize_transaction,
    get_categorization_service,
)

__all__ = [
    # Constants
    "PFCV2_CATEGORIES",
    "CategorizationMethod",
    "CategoryType",
    "HEURISTIC_PATTERNS",
    "get_category_type",
    "is_expense_category",
    "is_income_category",
    "format_category",
    "parse_category",
    # Services
    "CategorizationService",
    "CategorizationServiceResult",
    "categorize_transaction",
    "get_categorization_service",
]
