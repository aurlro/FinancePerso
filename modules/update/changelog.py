"""Changelog management utilities."""

import os
import re
from datetime import datetime
from typing import Optional

from modules.logger import logger
from modules.update.models import VersionEntry


class ChangelogManager:
    """Manages CHANGELOG.md file operations."""

    def __init__(self, project_root: str):
        """Initialize changelog manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.changelog_path = os.path.join(project_root, "CHANGELOG.md")

    def exists(self) -> bool:
        """Check if changelog file exists.

        Returns:
            True if CHANGELOG.md exists
        """
        return os.path.exists(self.changelog_path)

    def read(self) -> str:
        """Read changelog content.

        Returns:
            Changelog content or empty string if file doesn't exist
        """
        if not self.exists():
            return ""

        try:
            with open(self.changelog_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Could not read changelog: {e}")
            return ""

    def add_entry(self, entry: VersionEntry) -> bool:
        """Add a new entry to the changelog.

        Args:
            entry: Version entry to add

        Returns:
            True if added successfully
        """
        content = self.read()
        entry_md = entry.to_markdown()

        if not content:
            # Create new changelog
            content = self._create_new_changelog(entry_md)
        else:
            # Insert after header
            content = self._insert_entry(content, entry_md)

        try:
            with open(self.changelog_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Added changelog entry for version {entry.version}")
            return True
        except Exception as e:
            logger.error(f"Failed to write changelog: {e}")
            return False

    def _create_new_changelog(self, entry_md: str) -> str:
        """Create new changelog with entry.

        Args:
            entry_md: Markdown entry

        Returns:
            Complete changelog content
        """
        return f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

{entry_md}
"""

    def _insert_entry(self, content: str, entry_md: str) -> str:
        """Insert entry into existing changelog.

        Args:
            content: Existing changelog content
            entry_md: Entry to insert

        Returns:
            Updated content
        """
        lines = content.split("\n")
        insert_idx = 0

        # Find first version entry or end of header
        for i, line in enumerate(lines):
            if line.startswith("## ["):
                insert_idx = i
                break
            if line.startswith("#"):
                insert_idx = i + 1

        # Insert entry
        new_lines = lines[:insert_idx] + ["", entry_md] + lines[insert_idx:]
        return "\n".join(new_lines)

    def get_latest_version(self) -> Optional[str]:
        """Get latest version from changelog.

        Returns:
            Version string or None if not found
        """
        content = self.read()
        if not content:
            return None

        match = re.search(r"## \[?([0-9]+\.[0-9]+\.[0-9]+)\]?", content)
        if match:
            return match.group(1)

        return None

    def get_version_history(self) -> list[str]:
        """Get list of all versions in changelog.

        Returns:
            List of version strings
        """
        content = self.read()
        if not content:
            return []

        versions = re.findall(r"## \[?([0-9]+\.[0-9]+\.[0-9]+)\]?", content)
        return versions
