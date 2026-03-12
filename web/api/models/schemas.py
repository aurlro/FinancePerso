"""
Pydantic models for API request/response validation.
"""

from datetime import date
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Dashboard Models
# =============================================================================


class DashboardStatsResponse(BaseModel):
    """Response model for dashboard statistics."""

    reste_a_vivre: float = Field(..., description="Remaining money after expenses")
    total_expenses: float = Field(..., description="Total expenses for the period")
    total_income: float = Field(..., description="Total income for the period")
    epargne_nette: float = Field(..., description="Net savings (income - expenses)")
    period: str = Field(..., description="Period in YYYY-MM format")

    class Config:
        json_schema_extra = {
            "example": {
                "reste_a_vivre": 2500.50,
                "total_expenses": 1800.00,
                "total_income": 4300.50,
                "epargne_nette": 700.50,
                "period": "2024-03",
            }
        }


class CategoryBreakdownItem(BaseModel):
    """Single category breakdown item."""

    name: str = Field(..., description="Category name")
    amount: float = Field(..., description="Total amount for this category")
    percentage: float = Field(..., description="Percentage of total expenses")
    emoji: Optional[str] = Field(None, description="Category emoji")


class DashboardBreakdownResponse(BaseModel):
    """Response model for category breakdown."""

    categories: list[CategoryBreakdownItem] = Field(
        ..., description="List of categories with amounts and percentages"
    )
    total: float = Field(..., description="Total of all categories")

    class Config:
        json_schema_extra = {
            "example": {
                "categories": [
                    {"name": "Alimentation", "amount": 450.00, "percentage": 25.0, "emoji": "🛒"},
                    {"name": "Transport", "amount": 200.00, "percentage": 11.1, "emoji": "🚗"},
                ],
                "total": 1800.0,
            }
        }


class DashboardEvolutionResponse(BaseModel):
    """Response model for 12-month evolution."""

    months: list[str] = Field(..., description="List of months in YYYY-MM format")
    expenses: list[float] = Field(..., description="Total expenses per month")
    income: list[float] = Field(..., description="Total income per month")
    savings: list[float] = Field(..., description="Net savings per month")

    class Config:
        json_schema_extra = {
            "example": {
                "months": ["2024-01", "2024-02", "2024-03"],
                "expenses": [2000.0, 1800.0, 1900.0],
                "income": [4000.0, 4200.0, 4300.0],
                "savings": [2000.0, 2400.0, 2400.0],
            }
        }


# =============================================================================
# Transaction Models
# =============================================================================


class TransactionResponse(BaseModel):
    """Response model for a single transaction."""

    id: int = Field(..., description="Transaction ID")
    date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    label: str = Field(..., description="Transaction label/description")
    amount: float = Field(..., description="Transaction amount")
    category_validated: Optional[str] = Field(None, description="Validated category")
    category: Optional[str] = Field(None, description="Original category from import")
    status: str = Field(..., description="Transaction status (pending/validated)")
    member: Optional[str] = Field(None, description="Associated member")
    account_label: Optional[str] = Field(None, description="Account label")
    beneficiary: Optional[str] = Field(None, description="Beneficiary")
    notes: Optional[str] = Field(None, description="Notes")
    tags: Optional[str] = Field(None, description="Tags")
    card_suffix: Optional[str] = Field(None, description="Card suffix")
    ai_confidence: Optional[float] = Field(None, description="AI confidence score")
    tx_hash: Optional[str] = Field(None, description="Transaction hash")
    import_date: Optional[str] = Field(None, description="Import timestamp")

    class Config:
        from_attributes = True


class TransactionsListResponse(BaseModel):
    """Response model for paginated transaction list."""

    items: list[TransactionResponse] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions matching filters")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Offset for pagination")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "limit": 50,
                "offset": 0,
            }
        }


class TransactionFilters(BaseModel):
    """Query parameters for transaction filtering."""

    limit: int = Field(50, ge=1, le=1000, description="Number of items per page")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    category: Optional[str] = Field(None, description="Filter by category")
    month: Optional[str] = Field(
        None, pattern=r"^\d{4}-\d{2}$", description="Filter by month (YYYY-MM)"
    )
    status: Optional[Literal["pending", "validated"]] = Field(
        None, description="Filter by status"
    )
    member: Optional[str] = Field(None, description="Filter by member")
    search: Optional[str] = Field(None, description="Search in label/beneficiary")


# =============================================================================
# Error Models
# =============================================================================


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")

    class Config:
        json_schema_extra = {"example": {"detail": "Invalid month format", "code": "INVALID_MONTH"}}


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")
    timestamp: str = Field(..., description="Current timestamp")


# =============================================================================
# Account Models
# =============================================================================


class AccountType(str, Enum):
    """Account type enumeration."""
    PERSO_A = "perso_a"
    PERSO_B = "perso_b"
    JOINT = "joint"


class AccountCreateRequest(BaseModel):
    """Request model for creating a bank account."""

    name: str = Field(..., min_length=1, description="Account name")
    bank_name: Optional[str] = Field(None, description="Bank name")
    account_type: AccountType = Field(..., description="Account type")
    balance: float = Field(default=0.0, description="Initial balance")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Compte courant",
                "bank_name": "BNP Paribas",
                "account_type": "joint",
                "balance": 0.0,
            }
        }


class AccountUpdateRequest(BaseModel):
    """Request model for updating a bank account."""

    name: Optional[str] = Field(None, min_length=1, description="Account name")
    bank_name: Optional[str] = Field(None, description="Bank name")
    account_type: Optional[AccountType] = Field(None, description="Account type")
    balance: Optional[float] = Field(None, description="Current balance")


class AccountResponse(BaseModel):
    """Response model for a bank account."""

    id: int = Field(..., description="Account ID")
    name: str = Field(..., description="Account name")
    bank_name: Optional[str] = Field(None, description="Bank name")
    account_type: str = Field(..., description="Account type")
    balance: float = Field(..., description="Current balance")
    household_id: Optional[int] = Field(None, description="Associated household ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Compte courant",
                "bank_name": "BNP Paribas",
                "account_type": "joint",
                "balance": 1500.50,
                "household_id": 1,
                "created_at": "2024-03-15T10:30:00",
                "updated_at": "2024-03-15T10:30:00",
            }
        }


class AccountsListResponse(BaseModel):
    """Response model for list of accounts."""

    items: list[AccountResponse] = Field(..., description="List of accounts")
    total: int = Field(..., description="Total number of accounts")


# =============================================================================
# Authentication Models
# =============================================================================


class UserRegisterRequest(BaseModel):
    """Request model for user registration."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    name: str = Field(..., min_length=2, description="User display name")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "name": "John Doe",
            }
        }


class UserLoginRequest(BaseModel):
    """Request model for user login."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
            }
        }


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User display name")
    household_id: Optional[int] = Field(None, description="Associated household ID")
    created_at: str = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "John Doe",
                "household_id": None,
                "created_at": "2024-03-15T10:30:00",
            }
        }


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "name": "John Doe",
                    "household_id": None,
                    "created_at": "2024-03-15T10:30:00",
                },
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""

    refresh_token: str = Field(..., description="Valid refresh token")


class ChangePasswordRequest(BaseModel):
    """Request model for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


# =============================================================================
# Import Models
# =============================================================================


class CsvMapping(BaseModel):
    """CSV column mapping configuration."""

    date_column: str = Field(..., description="Column name for date")
    label_column: str = Field(..., description="Column name for label/description")
    amount_column: Optional[str] = Field(None, description="Column name for amount (if single column)")
    debit_column: Optional[str] = Field(None, description="Column name for debit amounts")
    credit_column: Optional[str] = Field(None, description="Column name for credit amounts")
    use_debit_credit: bool = Field(False, description="Whether to use separate debit/credit columns")


class ImportTransactionItem(BaseModel):
    """Single transaction data for import."""

    date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    label: str = Field(..., description="Transaction label")
    amount: float = Field(..., description="Transaction amount (negative for expenses)")
    raw_data: Optional[dict] = Field(None, description="Original CSV row data")


class ImportRequest(BaseModel):
    """Request model for CSV import."""

    account_id: int = Field(..., description="Target bank account ID")
    csv_content: str = Field(..., description="Raw CSV file content")
    mapping: CsvMapping = Field(..., description="Column mapping configuration")
    skip_duplicates: bool = Field(True, description="Skip transactions that already exist")

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": 1,
                "csv_content": "Date;Libellé;Montant\n2024-03-15;Supermarché;-45.20\n2024-03-16;Salaire;2500.00",
                "mapping": {
                    "date_column": "Date",
                    "label_column": "Libellé",
                    "amount_column": "Montant",
                    "use_debit_credit": False,
                },
                "skip_duplicates": True,
            }
        }


class ImportResultItem(BaseModel):
    """Result for a single imported transaction."""

    row_index: int = Field(..., description="Row index in CSV")
    status: Literal["imported", "duplicate", "error"] = Field(..., description="Import status")
    transaction_id: Optional[int] = Field(None, description="Created transaction ID (if imported)")
    error_message: Optional[str] = Field(None, description="Error message (if failed)")
    label: str = Field(..., description="Transaction label")
    amount: float = Field(..., description="Transaction amount")


class ImportResponse(BaseModel):
    """Response model for CSV import."""

    total_rows: int = Field(..., description="Total rows processed")
    imported: int = Field(..., description="Number of transactions imported")
    duplicates: int = Field(..., description="Number of duplicates skipped")
    errors: int = Field(..., description="Number of errors")
    transactions: list[ImportResultItem] = Field(..., description="Details for each row")
    transfer_detected_count: int = Field(0, description="Number of internal transfers detected")
    attributed_count: int = Field(0, description="Number of transactions auto-attributed")

    class Config:
        json_schema_extra = {
            "example": {
                "total_rows": 10,
                "imported": 8,
                "duplicates": 1,
                "errors": 1,
                "transactions": [],
                "transfer_detected_count": 2,
                "attributed_count": 5,
            }
        }


# =============================================================================
# Category Models
# =============================================================================


class CategoryResponse(BaseModel):
    """Response model for a category."""

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    emoji: str = Field(..., description="Category emoji")
    is_fixed: int = Field(..., description="Whether this is a fixed expense category")
    suggested_tags: Optional[str] = Field(None, description="Suggested tags for this category")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class CategoryCreateRequest(BaseModel):
    """Request model for creating a category."""

    name: str = Field(..., min_length=1, description="Category name")
    emoji: str = Field(default="🏷️", description="Category emoji")
    is_fixed: int = Field(default=0, description="Whether this is a fixed expense category")
    suggested_tags: Optional[str] = Field(None, description="Suggested tags")


class CategoryUpdateRequest(BaseModel):
    """Request model for updating a category."""

    name: Optional[str] = Field(None, min_length=1, description="Category name")
    emoji: Optional[str] = Field(None, description="Category emoji")
    is_fixed: Optional[int] = Field(None, description="Whether this is a fixed expense category")
    suggested_tags: Optional[str] = Field(None, description="Suggested tags")


class CategoriesListResponse(BaseModel):
    """Response model for list of categories."""

    items: list[CategoryResponse] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of categories")


# =============================================================================
# Budget Models
# =============================================================================


class BudgetResponse(BaseModel):
    """Response model for a budget."""

    category: str = Field(..., description="Category name")
    amount: float = Field(..., description="Budget amount")
    updated_at: str = Field(..., description="Last update timestamp")
    spent: Optional[float] = Field(None, description="Amount spent this month")
    remaining: Optional[float] = Field(None, description="Remaining budget")

    class Config:
        from_attributes = True


class BudgetCreateRequest(BaseModel):
    """Request model for creating a budget."""

    category: str = Field(..., description="Category name")
    amount: float = Field(..., ge=0, description="Budget amount")


class BudgetUpdateRequest(BaseModel):
    """Request model for updating a budget."""

    amount: float = Field(..., ge=0, description="Budget amount")


class BudgetsListResponse(BaseModel):
    """Response model for list of budgets."""

    items: list[BudgetResponse] = Field(..., description="List of budgets")
    total: int = Field(..., description="Total number of budgets")


# =============================================================================
# Member Models
# =============================================================================


class MemberResponse(BaseModel):
    """Response model for a household member."""

    id: int = Field(..., description="Member ID")
    name: str = Field(..., description="Member name")
    member_type: str = Field(..., description="Member type (HOUSEHOLD, etc.)")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class MemberCreateRequest(BaseModel):
    """Request model for creating a member."""

    name: str = Field(..., min_length=1, description="Member name")
    member_type: str = Field(default="HOUSEHOLD", description="Member type")


class MemberUpdateRequest(BaseModel):
    """Request model for updating a member."""

    name: Optional[str] = Field(None, min_length=1, description="Member name")
    member_type: Optional[str] = Field(None, description="Member type")


class MembersListResponse(BaseModel):
    """Response model for list of members."""

    items: list[MemberResponse] = Field(..., description="List of members")
    total: int = Field(..., description="Total number of members")


# =============================================================================
# Rule Models
# =============================================================================


class RuleResponse(BaseModel):
    """Response model for a learning rule."""

    id: int = Field(..., description="Rule ID")
    pattern: str = Field(..., description="Pattern to match")
    category: str = Field(..., description="Target category")
    priority: int = Field(..., description="Rule priority (higher = first)")
    created_at: str = Field(..., description="Creation timestamp")
    match_count: Optional[int] = Field(None, description="Number of matches")

    class Config:
        from_attributes = True


class RuleCreateRequest(BaseModel):
    """Request model for creating a rule."""

    pattern: str = Field(..., min_length=1, description="Pattern to match")
    category: str = Field(..., description="Target category")
    priority: int = Field(default=1, ge=1, description="Rule priority")


class RuleUpdateRequest(BaseModel):
    """Request model for updating a rule."""

    pattern: Optional[str] = Field(None, min_length=1, description="Pattern to match")
    category: Optional[str] = Field(None, description="Target category")
    priority: Optional[int] = Field(None, ge=1, description="Rule priority")


class RulesListResponse(BaseModel):
    """Response model for list of rules."""

    items: list[RuleResponse] = Field(..., description="List of rules")
    total: int = Field(..., description="Total number of rules")


class RuleTestRequest(BaseModel):
    """Request model for testing a rule pattern."""

    pattern: str = Field(..., description="Pattern to test")
    test_labels: list[str] = Field(default=[], description="Labels to test against")


class RuleTestResponse(BaseModel):
    """Response model for rule test."""

    pattern: str = Field(..., description="Tested pattern")
    matches: list[str] = Field(..., description="Labels that matched")
    match_count: int = Field(..., description="Number of matches")
    total_tested: int = Field(..., description="Total labels tested")


# =============================================================================
# Notification Models (PR #6)
# =============================================================================


class NotificationResponse(BaseModel):
    """Response model for a notification."""

    id: int = Field(..., description="Notification ID")
    user_id: int = Field(..., description="User ID")
    type: str = Field(..., description="Notification type (info, warning, success, error)")
    category: str = Field(..., description="Category (transaction, budget, invitation, system)")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Optional[dict] = Field(None, description="Additional data")
    is_read: bool = Field(False, description="Whether notification is read")
    read_at: Optional[str] = Field(None, description="Read timestamp")
    created_at: str = Field(..., description="Creation timestamp")


class NotificationCreateRequest(BaseModel):
    """Request model for creating a notification."""

    user_id: int = Field(..., description="Target user ID")
    type: str = Field(default="info", description="Notification type")
    category: str = Field(..., description="Category")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Optional[dict] = Field(None, description="Additional data")


class NotificationsListResponse(BaseModel):
    """Response model for list of notifications."""

    items: list[NotificationResponse] = Field(..., description="List of notifications")
    total: int = Field(..., description="Total number of notifications")
    unread_count: int = Field(..., description="Number of unread notifications")
