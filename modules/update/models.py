"""Data models for update management."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ChangeType(Enum):
    """Types of changes in a version."""

    ADDED = "added"
    CHANGED = "changed"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    FIXED = "fixed"
    SECURITY = "security"


@dataclass
class VersionEntry:
    """Represents a version entry in the changelog.

    Attributes:
        version: Version string (e.g., "3.5.0")
        date: Date string in format YYYY-MM-DD
        title: Short title/description of the release
        categories: Dictionary mapping change types to lists of changes
        files_modified: List of files modified in this version
        breaking_changes: List of breaking changes (if any)
    """

    version: str
    date: str
    title: str
    categories: dict[str, list[str]] = field(default_factory=dict)
    files_modified: list[str] = field(default_factory=list)
    breaking_changes: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate version format."""
        if not self._is_valid_version(self.version):
            raise ValueError(f"Invalid version format: {self.version}")

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if version string is valid (semver-like)."""
        import re

        return bool(re.match(r"^\d+\.\d+\.\d+", version))

    def add_change(self, change_type: ChangeType, description: str) -> None:
        """Add a change to this version entry.

        Args:
            change_type: Type of change
            description: Description of the change
        """
        key = change_type.value
        if key not in self.categories:
            self.categories[key] = []
        self.categories[key].append(description)

    def to_markdown(self) -> str:
        """Convert entry to markdown format for changelog.

        Returns:
            Markdown formatted string
        """
        lines = [
            f"## [{self.version}] - {self.date}",
            "",
            f"### {self.title}",
            "",
        ]

        for change_type in ChangeType:
            changes = self.categories.get(change_type.value, [])
            if changes:
                lines.append(f"**{change_type.value.upper()}**")
                for change in changes:
                    lines.append(f"- {change}")
                lines.append("")

        if self.breaking_changes:
            lines.append("**BREAKING CHANGES**")
            for change in self.breaking_changes:
                lines.append(f"- ⚠️ {change}")
            lines.append("")
        
        if self.files_modified:
            lines.append("**FICHIERS MODIFIÉS**")
            for file_path in self.files_modified:
                lines.append(f"- `{file_path}`")
            lines.append("")

        return "\n".join(lines)
