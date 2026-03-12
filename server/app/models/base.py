"""
Base model class with common functionality
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid4())


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """
    Base class for all models.
    Provides common functionality and configuration.
    """

    # Generate __tablename__ automatically from class name
    @classmethod
    def __declare_last__(cls) -> None:
        pass

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """String representation of the model."""
        attrs = [f"{key}={value!r}" for key, value in self.to_dict().items()]
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps.
    Inherit from this class to automatically track creation and update times.
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
