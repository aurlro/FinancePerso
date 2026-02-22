"""
Member Entity Model
===================
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

import pandas as pd


class MemberType(str, Enum):
    """Member type enumeration."""

    HOUSEHOLD = "HOUSEHOLD"
    EXTERNAL = "EXTERNAL"


@dataclass
class Member:
    """
    Member entity representing a household member or external entity.

    Attributes:
        id: Primary key
        name: Member name (unique)
        member_type: Type (HOUSEHOLD or EXTERNAL)
        created_at: Creation timestamp
    """

    id: Optional[int] = None
    name: str = ""
    member_type: str = "HOUSEHOLD"
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Set default timestamp and validate type."""
        if self.created_at is None:
            self.created_at = datetime.now()
        # Ensure member_type is valid
        if self.member_type not in [t.value for t in MemberType]:
            self.member_type = MemberType.HOUSEHOLD.value

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "member_type": self.member_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_series(cls, series: pd.Series) -> "Member":
        """Create Member from DataFrame row."""
        created_at = series.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return cls(
            id=series.get("id"),
            name=series.get("name", ""),
            member_type=series.get("member_type", MemberType.HOUSEHOLD.value),
            created_at=created_at,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Member":
        """Create Member from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            member_type=data.get("member_type", MemberType.HOUSEHOLD.value),
            created_at=created_at,
        )

    def is_household(self) -> bool:
        """Check if member is household type."""
        return self.member_type == MemberType.HOUSEHOLD.value

    def is_external(self) -> bool:
        """Check if member is external type."""
        return self.member_type == MemberType.EXTERNAL.value

    def __str__(self) -> str:
        """String representation."""
        prefix = "🏠" if self.is_household() else "👤"
        return f"{prefix} {self.name}"


@dataclass
class MemberMapping:
    """
    Mapping between card/account suffix and member.

    Attributes:
        id: Primary key
        card_suffix: Last digits of card/account
        member_name: Associated member name
        created_at: Creation timestamp
    """

    id: Optional[int] = None
    card_suffix: str = ""
    member_name: str = ""
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Set default timestamp."""
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "card_suffix": self.card_suffix,
            "member_name": self.member_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_series(cls, series: pd.Series) -> "MemberMapping":
        """Create MemberMapping from DataFrame row."""
        created_at = series.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return cls(
            id=series.get("id"),
            card_suffix=series.get("card_suffix", ""),
            member_name=series.get("member_name", ""),
            created_at=created_at,
        )
