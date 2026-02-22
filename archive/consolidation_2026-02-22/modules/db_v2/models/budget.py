"""
Budget Entity Model
===================
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd


@dataclass
class Budget:
    """
    Budget entity for spending limits.

    Attributes:
        id: Primary key
        category: Category name (unique)
        amount: Budget amount limit
        period: Budget period (monthly, yearly)
        alert_threshold: Percentage threshold for alerts (0-100)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: Optional[int] = None
    category: str = ""
    amount: float = 0.0
    period: str = "monthly"
    alert_threshold: float = 80.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Set default timestamps."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "category": self.category,
            "amount": self.amount,
            "period": self.period,
            "alert_threshold": self.alert_threshold,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_series(cls, series: pd.Series) -> "Budget":
        """Create Budget from DataFrame row."""
        created_at = series.get("created_at")
        updated_at = series.get("updated_at")

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

        return cls(
            id=series.get("id"),
            category=series.get("category", ""),
            amount=series.get("amount", 0.0),
            period=series.get("period", "monthly"),
            alert_threshold=series.get("alert_threshold", 80.0),
            created_at=created_at,
            updated_at=updated_at,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        """Create Budget from dictionary."""
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

        return cls(
            id=data.get("id"),
            category=data.get("category", ""),
            amount=data.get("amount", 0.0),
            period=data.get("period", "monthly"),
            alert_threshold=data.get("alert_threshold", 80.0),
            created_at=created_at,
            updated_at=updated_at,
        )

    def get_spent_percentage(self, spent: float) -> float:
        """Calculate spent percentage of budget."""
        if self.amount <= 0:
            return 0.0
        return min(100.0, (spent / self.amount) * 100)

    def is_over_budget(self, spent: float) -> bool:
        """Check if spending exceeds budget."""
        return spent > self.amount

    def is_alert_triggered(self, spent: float) -> bool:
        """Check if alert threshold is reached."""
        percentage = self.get_spent_percentage(spent)
        return percentage >= self.alert_threshold

    def get_remaining(self, spent: float) -> float:
        """Get remaining budget amount."""
        return max(0.0, self.amount - spent)
