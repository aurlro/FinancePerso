"""
Budget model for spending limits by category
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .category import Category


class Budget(Base, TimestampMixin):
    """
    Budget allocation for a specific category.
    Tracks spending limits and alerts.
    """

    __tablename__ = "budgets"

    # Period
    period: Mapped[str] = mapped_column(
        String(20),
        default="monthly",
        nullable=False,  # monthly, yearly
    )
    year: Mapped[Optional[int]] = mapped_column(
        nullable=True,  # NULL for recurring budgets
    )
    month: Mapped[Optional[int]] = mapped_column(
        nullable=True,  # NULL for yearly/recurring budgets
    )

    # Amount
    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Alert configuration
    alert_threshold: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=80.0,
        nullable=False,  # Percentage (e.g., 80 for 80%)
    )
    alert_sent: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # Relationship
    category_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("categories.id"),
        nullable=False,
    )
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="budgets",
    )

    def __str__(self) -> str:
        period_label = f"{self.month}/{self.year}" if self.month and self.year else self.period
        return f"Budget {self.category.name}: {self.amount:.2f}€ ({period_label})"
