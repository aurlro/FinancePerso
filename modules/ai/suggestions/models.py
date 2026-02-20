"""Data models for smart suggestions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SuggestionType(Enum):
    """Types of suggestions."""

    CATEGORY = "category"
    RULE = "rule"
    BUDGET = "budget"
    MEMBER = "member"
    DUPLICATE = "duplicate"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    INCOME = "income"
    TAG = "tag"
    SAVINGS = "savings"


class Priority(Enum):
    """Priority levels for suggestions."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Suggestion:
    """A single intelligent suggestion.

    Attributes:
        id: Unique identifier for the suggestion
        type: Type of suggestion (category, rule, budget, etc.)
        priority: Priority level (high, medium, low)
        title: Short title describing the suggestion
        description: Detailed description
        action_label: Label for the action button
        action_data: Data needed to execute the action
        impact_score: Impact score from 0-100
        auto_fixable: Whether the suggestion can be auto-fixed
    """

    id: str
    type: str
    priority: str
    title: str
    description: str
    action_label: str
    action_data: dict[str, Any]
    impact_score: int
    auto_fixable: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert suggestion to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "action_label": self.action_label,
            "action_data": self.action_data,
            "impact_score": self.impact_score,
            "auto_fixable": self.auto_fixable,
        }


@dataclass
class AnalysisContext:
    """Context for analysis operations.

    Contains all data needed for analyzers to perform their work.
    """

    transactions: Any  # pd.DataFrame
    rules: Any  # pd.DataFrame
    budgets: Any  # pd.DataFrame
    members: Any  # pd.DataFrame
    categories: list[str] = field(default_factory=list)

    def has_transactions(self) -> bool:
        """Check if transactions data is available."""
        return not (self.transactions is None or len(self.transactions) == 0)

    def has_rules(self) -> bool:
        """Check if rules data is available."""
        return not (self.rules is None or len(self.rules) == 0)

    def has_budgets(self) -> bool:
        """Check if budgets data is available."""
        return not (self.budgets is None or len(self.budgets) == 0)
