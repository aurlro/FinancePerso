"""
Budget schemas
"""

from typing import Optional

from pydantic import Field, model_validator

from .base import BaseSchema, TimestampedSchema


class BudgetBase(BaseSchema):
    """Base budget fields."""

    category_id: str = Field(..., description="Category ID")
    amount: float = Field(..., gt=0, description="Budget amount")
    period: str = Field(default="monthly", pattern=r"^(monthly|yearly)$")
    alert_threshold: float = Field(default=80.0, ge=0, le=100)


class BudgetCreate(BudgetBase):
    """Schema for creating a budget."""

    year: Optional[int] = None
    month: Optional[int] = Field(default=None, ge=1, le=12)


class BudgetUpdate(BaseSchema):
    """Schema for updating a budget."""

    amount: Optional[float] = Field(default=None, gt=0)
    alert_threshold: Optional[float] = Field(default=None, ge=0, le=100)
    period: Optional[str] = Field(default=None, pattern=r"^(monthly|yearly)$")


class Budget(TimestampedSchema, BudgetBase):
    """Full budget schema."""

    year: Optional[int] = None
    month: Optional[int] = None
    alert_sent: bool = False


class BudgetResponse(BaseSchema):
    """Budget API response."""

    data: Budget


class BudgetWithSpending(Budget):
    """Budget with actual spending data."""

    spent: float = 0.0
    remaining: float = 0.0
    percentage_used: float = 0.0
    is_over_budget: bool = False
    category_name: str = ""
    category_emoji: str = ""
    category_color: str = ""

    @model_validator(mode="after")
    def calculate_derived_fields(self):
        """Calculate remaining and percentage."""
        if self.amount > 0:
            self.remaining = self.amount - self.spent
            self.percentage_used = (self.spent / self.amount) * 100
            self.is_over_budget = self.spent > self.amount
        return self


class BudgetAlert(BaseSchema):
    """Budget alert notification."""

    budget_id: str
    category_name: str
    percentage_used: float
    amount_spent: float
    budget_limit: float
    message: str
