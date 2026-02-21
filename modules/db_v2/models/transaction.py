"""
Transaction Entity Model
========================
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pandas as pd


@dataclass
class Transaction:
    """
    Transaction entity representing a financial transaction.

    Attributes:
        id: Primary key (auto-generated)
        date: Transaction date (YYYY-MM-DD)
        label: Transaction description/label
        amount: Transaction amount (positive for income, negative for expense)
        category: Assigned category
        category_validated: Validated category (may differ from auto-categorized)
        status: Transaction status (pending, validated)
        member: Associated member/entity
        tags: Comma-separated tags
        tx_hash: Unique hash for deduplication
        account_label: Source account identifier
        beneficiary: Transaction beneficiary
        notes: Additional notes
        is_grouped: Whether part of a transaction group
        group_id: Group identifier if grouped
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: Optional[int] = None
    date: str = ""
    label: str = ""
    amount: float = 0.0
    category: Optional[str] = None
    category_validated: Optional[str] = None
    status: str = "pending"
    member: Optional[str] = None
    tags: Optional[str] = None
    tx_hash: Optional[str] = None
    account_label: str = "Unknown"
    beneficiary: Optional[str] = None
    notes: Optional[str] = None
    is_grouped: bool = False
    group_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Set default timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            "id": self.id,
            "date": self.date,
            "label": self.label,
            "amount": self.amount,
            "category": self.category,
            "category_validated": self.category_validated,
            "status": self.status,
            "member": self.member,
            "tags": self.tags,
            "tx_hash": self.tx_hash,
            "account_label": self.account_label,
            "beneficiary": self.beneficiary,
            "notes": self.notes,
            "is_grouped": self.is_grouped,
            "group_id": self.group_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_series(cls, series: pd.Series) -> "Transaction":
        """Create Transaction from DataFrame row."""
        return cls(
            id=series.get("id"),
            date=series.get("date", ""),
            label=series.get("label", ""),
            amount=series.get("amount", 0.0),
            category=series.get("category"),
            category_validated=series.get("category_validated"),
            status=series.get("status", "pending"),
            member=series.get("member"),
            tags=series.get("tags"),
            tx_hash=series.get("tx_hash"),
            account_label=series.get("account_label", "Unknown"),
            beneficiary=series.get("beneficiary"),
            notes=series.get("notes"),
            is_grouped=series.get("is_grouped", False),
            group_id=series.get("group_id"),
            created_at=cls._parse_datetime(series.get("created_at")),
            updated_at=cls._parse_datetime(series.get("updated_at")),
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create Transaction from dictionary."""
        return cls(
            id=data.get("id"),
            date=data.get("date", ""),
            label=data.get("label", ""),
            amount=data.get("amount", 0.0),
            category=data.get("category"),
            category_validated=data.get("category_validated"),
            status=data.get("status", "pending"),
            member=data.get("member"),
            tags=data.get("tags"),
            tx_hash=data.get("tx_hash"),
            account_label=data.get("account_label", "Unknown"),
            beneficiary=data.get("beneficiary"),
            notes=data.get("notes"),
            is_grouped=data.get("is_grouped", False),
            group_id=data.get("group_id"),
            created_at=cls._parse_datetime(data.get("created_at")),
            updated_at=cls._parse_datetime(data.get("updated_at")),
        )

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        """Parse datetime from various formats."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

    def is_expense(self) -> bool:
        """Check if transaction is an expense."""
        return self.amount < 0

    def is_income(self) -> bool:
        """Check if transaction is income."""
        return self.amount > 0

    def get_display_category(self) -> str:
        """Get category to display (validated or auto)."""
        return self.category_validated or self.category or "Non catégorisé"
