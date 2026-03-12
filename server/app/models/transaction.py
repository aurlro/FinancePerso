"""
Transaction model - Core of the application
"""

from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .account import Account
    from .category import Category


class TransactionType(str, PyEnum):
    """Types of transactions."""

    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class TransactionStatus(str, PyEnum):
    """Status of transaction processing."""

    PENDING = "pending"  # Imported but not reviewed
    VALIDATED = "validated"  # Reviewed and confirmed
    IMPORTED = "imported"  # Just imported


class Transaction(Base, TimestampMixin):
    """
    Financial transaction - the core entity of FinancePerso.
    Represents a single debit or credit operation.
    """

    __tablename__ = "transactions"

    # Date and amount
    date: Mapped[Date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Description and classification
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    type: Mapped[TransactionType] = mapped_column(
        String(20),
        default=TransactionType.EXPENSE,
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[TransactionStatus] = mapped_column(
        String(20),
        default=TransactionStatus.PENDING,
        nullable=False,
        index=True,
    )
    is_validated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    category_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("categories.id"),
        nullable=True,
        index=True,
    )
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="transactions",
    )

    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("accounts.id"),
        nullable=False,
        index=True,
    )
    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="transactions",
    )

    # Transfer link (for transfer transactions)
    transfer_pair_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("transactions.id"),
        nullable=True,
    )

    # Additional info
    beneficiary: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    tags: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,  # JSON array as string
    )

    # Recurring
    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    recurring_pattern: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,  # monthly, weekly, yearly
    )

    # Import metadata
    hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    import_source: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    import_batch_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    # AI/ML metadata
    ai_confidence: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2),
        nullable=True,  # 0.0 to 1.0
    )
    ai_model: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[Optional[Date]] = mapped_column(
        Date,
        nullable=True,
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_transactions_date_type", "date", "type"),
        Index("ix_transactions_account_date", "account_id", "date"),
        Index("ix_transactions_category_date", "category_id", "date"),
    )

    def __str__(self) -> str:
        sign = "+" if self.type == TransactionType.INCOME else "-"
        return f"{self.date} {sign}{self.amount:.2f}€ {self.description[:30]}"

    @property
    def signed_amount(self) -> float:
        """Return amount with sign based on type."""
        if self.type == TransactionType.EXPENSE:
            return -abs(self.amount)
        return abs(self.amount)

    @property
    def tag_list(self) -> list[str]:
        """Parse tags JSON string to list."""
        import json

        if not self.tags:
            return []
        try:
            return json.loads(self.tags)
        except json.JSONDecodeError:
            return []

    def set_tags(self, tags: list[str]) -> None:
        """Set tags from list to JSON string."""
        import json

        self.tags = json.dumps(tags) if tags else None
