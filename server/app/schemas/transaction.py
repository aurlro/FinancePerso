"""
Transaction schemas
"""

from datetime import date
from typing import Optional

from pydantic import Field, model_validator

from .base import BaseSchema, TimestampedSchema


class TransactionBase(BaseSchema):
    """Base transaction fields."""

    date: date = Field(..., description="Transaction date")
    amount: float = Field(..., gt=0, description="Transaction amount (always positive)")
    description: str = Field(..., min_length=1, max_length=500)
    type: str = Field(
        default="expense",
        pattern=r"^(income|expense|transfer)$",
    )
    category_id: Optional[str] = None
    account_id: str = Field(..., description="Account ID")
    beneficiary: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=2000)
    tags: list[str] = Field(default_factory=list)
    is_recurring: bool = Field(default=False)


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""

    pass


class TransactionUpdate(BaseSchema):
    """Schema for updating a transaction."""

    date: Optional[date] = None
    amount: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = Field(default=None, min_length=1, max_length=500)
    type: Optional[str] = Field(default=None, pattern=r"^(income|expense|transfer)$")
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    beneficiary: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=2000)
    tags: Optional[list[str]] = None
    is_recurring: Optional[bool] = None


class TransactionValidation(BaseSchema):
    """Schema for validating a transaction."""

    category_id: str = Field(..., description="Validated category ID")
    is_recurring: Optional[bool] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None


class TransactionBulkUpdate(BaseSchema):
    """Schema for bulk updating transactions."""

    ids: list[str] = Field(..., min_length=1)
    category_id: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern=r"^(pending|validated|imported)$")
    tags: Optional[list[str]] = None


class CategoryBrief(BaseSchema):
    """Brief category info for nested responses."""

    id: str
    name: str
    emoji: str
    color: str


class AccountBrief(BaseSchema):
    """Brief account info for nested responses."""

    id: str
    name: str
    emoji: str
    color: str
    type: str


class Transaction(TimestampedSchema, TransactionBase):
    """Full transaction schema."""

    status: str = Field(default="pending", pattern=r"^(pending|validated|imported)$")
    is_validated: bool = Field(default=False)
    hash: str = Field(..., description="Unique hash for deduplication")
    ai_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    category: Optional[CategoryBrief] = None
    account: AccountBrief


class TransactionResponse(BaseSchema):
    """Transaction API response."""

    data: Transaction


class TransactionImport(BaseSchema):
    """Schema for importing transactions from CSV."""

    date: str = Field(..., description="Date string (will be parsed)")
    amount: float = Field(..., description="Amount (negative for expenses)")
    description: str = Field(...)
    beneficiary: Optional[str] = None

    @model_validator(mode="after")
    def set_type_from_amount(self):
        """Auto-set transaction type from amount sign."""
        if not hasattr(self, "type"):
            self.type = "income" if self.amount >= 0 else "expense"
        return self


class TransactionFilters(BaseSchema):
    """Filters for transaction queries."""

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    type: Optional[str] = Field(default=None, pattern=r"^(income|expense|transfer)$")
    status: Optional[str] = Field(default=None, pattern=r"^(pending|validated|imported)$")
    min_amount: Optional[float] = Field(default=None, ge=0)
    max_amount: Optional[float] = Field(default=None, ge=0)
    search: Optional[str] = Field(default=None, max_length=100)
    tags: Optional[list[str]] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
