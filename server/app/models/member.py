"""
Member model for household/family management
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    pass  # Add transaction sharing models if needed


class Member(Base, TimestampMixin):
    """
    Household member for multi-person finance tracking.
    Tracks income sharing and expense allocation.
    """

    __tablename__ = "members"

    # Basic info
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Display
    color: Mapped[str] = mapped_column(
        String(7),
        default="#3B82F6",
        nullable=False,
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,  # URL or base64
    )

    # Income sharing
    share_percentage: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=50.0,
        nullable=False,
    )
    monthly_income: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # Role
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    def __str__(self) -> str:
        return self.name

    @property
    def initials(self) -> str:
        """Get initials from name."""
        parts = self.name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        return self.name[:2].upper()
