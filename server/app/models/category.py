"""
Category model for transaction categorization
"""

from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .budget import Budget
    from .transaction import Transaction


class CategoryType(str, PyEnum):
    """Category types for classification."""

    FIXED = "fixed"
    VARIABLE = "variable"
    INCOME = "income"
    SAVINGS = "savings"


class Category(Base, TimestampMixin):
    """
    Category for grouping transactions.
    Supports hierarchical structure with parent-child relationships.
    """

    __tablename__ = "categories"

    # Basic info
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    emoji: Mapped[str] = mapped_column(
        String(10),
        default="📁",
        nullable=False,
    )
    color: Mapped[str] = mapped_column(
        String(7),  # Hex color (#RRGGBB)
        default="#3B82F6",
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Classification
    type: Mapped[CategoryType] = mapped_column(
        String(20),
        default=CategoryType.VARIABLE,
        nullable=False,
        index=True,
    )
    is_fixed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Budgeting
    budget_limit: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # Hierarchy
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("categories.id"),
        nullable=True,
        index=True,
    )

    # Relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children",
    )
    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="category",
    )
    budgets: Mapped[list["Budget"]] = relationship(
        "Budget",
        back_populates="category",
    )

    def __str__(self) -> str:
        return f"{self.emoji} {self.name}"

    @property
    def full_path(self) -> str:
        """Get full category path including parents."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
