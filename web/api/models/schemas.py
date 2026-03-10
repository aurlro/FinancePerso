"""
Pydantic models for API request/response validation.
"""

from datetime import date
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
