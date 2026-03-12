"""
Pydantic schemas for API request/response validation
Mirrors shared/schemas.ts for type consistency
"""

from .base import PaginatedResponse, SuccessResponse
from .category import (
    Category,
    CategoryCreate,
    CategoryResponse,
    CategoryTree,
    CategoryUpdate,
    CategoryWithStats,
)
from .account import (
    Account,
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    AccountWithStats,
)
from .transaction import (
    Transaction,
    TransactionBulkUpdate,
    TransactionCreate,
    TransactionFilters,
    TransactionImport,
    TransactionResponse,
    TransactionUpdate,
    TransactionValidation,
)
from .member import Member, MemberCreate, MemberResponse, MemberUpdate
from .budget import (
    Budget,
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
    BudgetWithSpending,
)
from .dashboard import (
    CashflowForecast,
    DashboardStats,
    MonthlyTrend,
    SpendingByCategory,
)

__all__ = [
    # Base
    "PaginatedResponse",
    "SuccessResponse",
    # Category
    "Category",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryTree",
    "CategoryWithStats",
    # Account
    "Account",
    "AccountCreate",
    "AccountUpdate",
    "AccountResponse",
    "AccountWithStats",
    # Transaction
    "Transaction",
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionFilters",
    "TransactionBulkUpdate",
    "TransactionImport",
    "TransactionValidation",
    # Member
    "Member",
    "MemberCreate",
    "MemberUpdate",
    "MemberResponse",
    # Budget
    "Budget",
    "BudgetCreate",
    "BudgetUpdate",
    "BudgetResponse",
    "BudgetWithSpending",
    # Dashboard
    "DashboardStats",
    "SpendingByCategory",
    "MonthlyTrend",
    "CashflowForecast",
]
