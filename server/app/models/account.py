"""
Account model for bank accounts and wallets
"""

from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .transaction import Transaction


class AccountType(str, PyEnum):
    """Types of financial accounts."""

    CHECKING = "checking"  # Compte courant
    SAVINGS = "savings"  # Livret d'épargne
    CREDIT = "credit"  # Carte de crédit
    CASH = "cash"  # Espèces
    INVESTMENT = "investment"  # Compte titre / PEA


class Account(Base, TimestampMixin):
    """
    Bank account or wallet for tracking transactions.
    """

    __tablename__ = "accounts"

    # Basic info
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    type: Mapped[AccountType] = mapped_column(
        String(20),
        default=AccountType.CHECKING,
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Financial details
    balance: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0.0,
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="EUR",
        nullable=False,
    )

    # Bank details (optional)
    bank_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    account_number: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    iban: Mapped[Optional[str]] = mapped_column(
        String(34),
        nullable=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Display
    color: Mapped[str] = mapped_column(
        String(7),
        default="#10B981",
        nullable=False,
    )
    emoji: Mapped[str] = mapped_column(
        String(10),
        default="💳",
        nullable=False,
    )

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return f"{self.emoji} {self.name}"

    @property
    def masked_number(self) -> Optional[str]:
        """Return masked account number for display."""
        if not self.account_number:
            return None
        if len(self.account_number) <= 4:
            return f"****{self.account_number}"
        return f"****{self.account_number[-4:]}"
