"""
Category schemas
"""

from typing import Optional

from pydantic import Field

from .base import BaseSchema, TimestampedSchema


class CategoryBase(BaseSchema):
    """Base category fields."""

    name: str = Field(..., min_length=1, max_length=100)
    emoji: str = Field(default="📁", max_length=10)
    color: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = Field(default=None, max_length=500)
    type: str = Field(default="variable", pattern=r"^(fixed|variable|income|savings)$")
    is_fixed: bool = Field(default=False)
    budget_limit: Optional[float] = Field(default=None, ge=0)
    parent_id: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    pass


class CategoryUpdate(BaseSchema):
    """Schema for updating a category."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    emoji: Optional[str] = Field(default=None, max_length=10)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = Field(default=None, max_length=500)
    type: Optional[str] = Field(default=None, pattern=r"^(fixed|variable|income|savings)$")
    is_fixed: Optional[bool] = None
    budget_limit: Optional[float] = Field(default=None, ge=0)
    parent_id: Optional[str] = None


class Category(TimestampedSchema, CategoryBase):
    """Full category schema."""

    pass


class CategoryResponse(BaseSchema):
    """Category API response."""

    data: Category


class CategoryTree(BaseSchema):
    """Category with nested children."""

    id: str
    name: str
    emoji: str
    color: str
    children: list["CategoryTree"] = []


class CategoryStats(BaseSchema):
    """Statistics for a category."""

    transaction_count: int
    total_amount: float
    monthly_average: float
    percentage_of_total: float


class CategoryWithStats(Category):
    """Category with statistics."""

    stats: CategoryStats
    children: list["CategoryWithStats"] = []
