"""
Account schemas
"""

from typing import Optional

from pydantic import Field, field_validator

from .base import BaseSchema, TimestampedSchema


class AccountBase(BaseSchema):
    """Base account fields."""

    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(
        default="checking",
        pattern=r"^(checking|savings|credit|cash|investment)$",
    )
    balance: float = Field(default=0.0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    bank_name: Optional[str] = Field(default=None, max_length=100)
    account_number: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    color: str = Field(default="#10B981", pattern=r"^#[0-9A-Fa-f]{6}$")
    emoji: str = Field(default="💳", max_length=10)


class AccountCreate(AccountBase):
    """Schema for creating an account."""

    pass


class AccountUpdate(BaseSchema):
    """Schema for updating an account."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    type: Optional[str] = Field(
        default=None,
        pattern=r"^(checking|savings|credit|cash|investment)$",
    )
    balance: Optional[float] = None
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    bank_name: Optional[str] = Field(default=None, max_length=100)
    account_number: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    emoji: Optional[str] = Field(default=None, max_length=10)


class Account(TimestampedSchema, AccountBase):
    """Full account schema."""

    pass


class AccountResponse(BaseSchema):
    """Account API response."""

    data: Account


class AccountStats(BaseSchema):
    """Statistics for an account."""

    transaction_count: int
    income_this_month: float
    expenses_this_month: float
    balance_change_this_month: float


class AccountWithStats(Account):
    """Account with statistics."""

    stats: AccountStats

    @field_validator("stats", mode="before")
    @classmethod
    def validate_stats(cls, v):
        if v is None:
            return AccountStats(
                transaction_count=0,
                income_this_month=0.0,
                expenses_this_month=0.0,
                balance_change_this_month=0.0,
            )
        return v
