"""
LearningRule model for AI categorization training
"""

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class LearningRule(Base, TimestampMixin):
    """
    Rule for automatic transaction categorization.
    Created from user confirmations to improve AI accuracy.
    """

    __tablename__ = "learning_rules"

    # Pattern matching
    pattern: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    pattern_type: Mapped[str] = mapped_column(
        String(20),
        default="contains",
        nullable=False,  # exact, contains, regex, starts_with, ends_with
    )

    # Target category
    category_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("categories.id"),
        nullable=False,
    )

    # Matching scope
    field: Mapped[str] = mapped_column(
        String(50),
        default="description",
        nullable=False,  # description, beneficiary, full_text
    )

    # Priority (higher = evaluated first)
    priority: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Statistics
    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    success_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Source
    created_by: Mapped[str] = mapped_column(
        String(50),
        default="user",
        nullable=False,  # user, ai, import
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        default=1.0,
        nullable=True,
    )

    # Relationships
    category = relationship("Category", lazy="joined")

    def __str__(self) -> str:
        return f"Rule: '{self.pattern}' → {self.category.name}"

    def matches(self, text: str) -> bool:
        """Check if this rule matches the given text."""
        text = text.lower()
        pattern = self.pattern.lower()

        if self.pattern_type == "exact":
            return text == pattern
        elif self.pattern_type == "contains":
            return pattern in text
        elif self.pattern_type == "starts_with":
            return text.startswith(pattern)
        elif self.pattern_type == "ends_with":
            return text.endswith(pattern)
        elif self.pattern_type == "regex":
            import re

            try:
                return bool(re.search(pattern, text))
            except re.error:
                return False
        return False
