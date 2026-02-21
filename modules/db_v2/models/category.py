"""
Category Entity Model
=====================
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd


@dataclass
class Category:
    """
    Category entity for transaction classification.

    Attributes:
        id: Primary key
        name: Category name (unique)
        emoji: Display emoji
        is_fixed: Whether it's a fixed/recurring category
        suggested_tags: Comma-separated suggested tags
        created_at: Creation timestamp
    """

    id: Optional[int] = None
    name: str = ""
    emoji: str = "📦"
    is_fixed: bool = False
    suggested_tags: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Set default timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "emoji": self.emoji,
            "is_fixed": self.is_fixed,
            "suggested_tags": self.suggested_tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_series(cls, series: pd.Series) -> "Category":
        """Create Category from DataFrame row."""
        created_at = series.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return cls(
            id=series.get("id"),
            name=series.get("name", ""),
            emoji=series.get("emoji", "📦"),
            is_fixed=series.get("is_fixed", False),
            suggested_tags=series.get("suggested_tags"),
            created_at=created_at,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        """Create Category from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            emoji=data.get("emoji", "📦"),
            is_fixed=data.get("is_fixed", False),
            suggested_tags=data.get("suggested_tags"),
            created_at=created_at,
        )

    def get_suggested_tags_list(self) -> list[str]:
        """Get suggested tags as list."""
        if not self.suggested_tags:
            return []
        return [tag.strip() for tag in self.suggested_tags.split(",") if tag.strip()]

    def add_suggested_tag(self, tag: str) -> None:
        """Add a suggested tag."""
        tags = self.get_suggested_tags_list()
        if tag not in tags:
            tags.append(tag)
            self.suggested_tags = ", ".join(tags)

    def remove_suggested_tag(self, tag: str) -> None:
        """Remove a suggested tag."""
        tags = self.get_suggested_tags_list()
        if tag in tags:
            tags.remove(tag)
            self.suggested_tags = ", ".join(tags) if tags else None

    def __str__(self) -> str:
        """String representation."""
        return f"{self.emoji} {self.name}"
