"""Update Manager - Facade for update operations.

Provides a unified interface for version management, changelog operations,
and git analysis.
"""

import os
from typing import Optional

from modules.logger import logger
from modules.update.changelog import ChangelogManager
from modules.update.creator import UpdateCreator
from modules.update.git import GitAnalyzer
from modules.update.models import VersionEntry
from modules.update.version import VersionManager


class UpdateManager:
    """Manages application updates and documentation synchronization.

    This is the main entry point for update operations. It delegates to
    specialized classes:
    - VersionManager: Version number operations
    - ChangelogManager: CHANGELOG.md operations
    - GitAnalyzer: Git repository analysis
    - UpdateCreator: Version entry creation

    Example:
        manager = UpdateManager()

        # Get current version
        version = manager.get_current_version()

        # Create new release
        new_version = manager.bump_version(version, "minor")
        entry = manager.create_update(new_version, "New features")
        manager.add_changelog_entry(entry)
    """

    def __init__(self, project_root: Optional[str] = None):
        """Initialize update manager.

        Args:
            project_root: Root directory of the project. If None, uses current directory.
        """
        self.project_root = project_root or os.getcwd()

        # Initialize specialized managers
        self._version = VersionManager(self.project_root)
        self._changelog = ChangelogManager(self.project_root)
        self._git = GitAnalyzer(self.project_root)
        self._creator = UpdateCreator(self.project_root)

    # ==================== Backward Compatibility Properties ====================

    @property
    def constants_path(self) -> str:
        """Path to constants.py (backward compatibility)."""
        return self._version.constants_path

    @property
    def changelog_path(self) -> str:
        """Path to CHANGELOG.md (backward compatibility)."""
        return self._changelog.changelog_path

    # ==================== Version Operations ====================

    def get_current_version(self) -> str:
        """Extract current version from constants.py or changelog.

        Returns:
            Current version string (e.g., "3.5.0")
        """
        return self._version.get_current_version()

    def bump_version(self, version: Optional[str] = None, bump_type: str = "patch") -> str:
        """Bump version number.

        Args:
            version: Current version. If None, uses get_current_version().
            bump_type: Type of bump: "patch", "minor", or "major"

        Returns:
            New version string
        """
        if version is None:
            version = self.get_current_version()
        return self._version.bump_version(version, bump_type)

    def update_version_in_files(self, new_version: str) -> bool:
        """Update version in all relevant files.

        Args:
            new_version: New version string

        Returns:
            True if all updates succeeded
        """
        return self._version.update_version_in_constants(new_version)

    # ==================== Changelog Operations ====================

    def add_changelog_entry(self, entry: VersionEntry) -> bool:
        """Add a new entry to CHANGELOG.md.

        Args:
            entry: Version entry to add

        Returns:
            True if added successfully
        """
        return self._changelog.add_entry(entry)

    def get_changelog_content(self) -> str:
        """Read changelog content.

        Returns:
            Changelog content or empty string
        """
        return self._changelog.read()

    # ==================== Git Operations ====================

    def is_git_repo(self) -> bool:
        """Check if project is a git repository.

        Returns:
            True if valid git repository
        """
        return self._git.is_git_repo()

    def get_changes_since_last_tag(self):
        """Get changes since last git tag.

        Returns:
            List of GitChange objects
        """
        return self._git.get_changes_since()

    # ==================== Update Creation ====================

    def create_update(
        self,
        version: str,
        title: str,
        since_ref: Optional[str] = None,
    ) -> VersionEntry:
        """Create a version entry from git changes.

        Args:
            version: Version string
            title: Entry title
            since_ref: Git reference to compare against

        Returns:
            Populated VersionEntry
        """
        return self._creator.create_entry(version, title, since_ref)

    def suggest_version_bump(self, since_ref: Optional[str] = None) -> str:
        """Suggest version bump type based on changes.

        Args:
            since_ref: Git reference to compare against

        Returns:
            Suggested bump type: "major", "minor", or "patch"
        """
        return self._creator.suggest_version_bump(since_ref)

    # ==================== High-Level Operations ====================

    def create_release(
        self,
        bump_type: str = "patch",
        title: Optional[str] = None,
        auto_commit: bool = False,
    ) -> tuple[bool, str]:
        """Create a complete release.

        Performs:
        1. Bump version
        2. Create changelog entry
        3. Update version in files
        4. Optionally commit changes

        Args:
            bump_type: Type of version bump
            title: Release title (auto-generated if None)
            auto_commit: Whether to commit changes

        Returns:
            Tuple of (success, new_version)
        """
        try:
            # Get new version
            current = self.get_current_version()
            new_version = self.bump_version(current, bump_type)

            # Generate title if not provided
            if title is None:
                title = f"Release {new_version}"

            # Create changelog entry
            entry = self.create_update(new_version, title)
            if not self.add_changelog_entry(entry):
                logger.error("Failed to add changelog entry")
                return False, new_version

            # Update version in files
            if not self.update_version_in_files(new_version):
                logger.warning("Failed to update version in files")

            logger.info(f"Created release {new_version}")
            return True, new_version

        except Exception as e:
            logger.error(f"Failed to create release: {e}")
            return False, ""

    # ==================== Backward Compatibility Methods ====================

    def _format_changelog_entry(self, entry: VersionEntry) -> str:
        """Format changelog entry (backward compatibility).

        Args:
            entry: Version entry to format

        Returns:
            Formatted markdown string
        """
        return entry.to_markdown()

    def update_constants(self, version: str) -> bool:
        """Update version in constants.py (backward compatibility).

        Args:
            version: New version string

        Returns:
            True if successful
        """
        return self._version.update_version_in_constants(version)

    def analyze_git_changes(self, since_tag: bool = True) -> dict:
        """Analyze git changes (backward compatibility).

        Args:
            since_tag: Whether to analyze since last tag

        Returns:
            Dictionary with change analysis
        """
        ref = None if since_tag else "HEAD~10"
        changes = self._git.get_changes_since(ref)
        commits = self._git.get_commit_messages(ref)

        # Categorize changes
        categories = {"added": [], "changed": [], "fixed": [], "removed": []}
        for commit in commits:
            commit_lower = commit.lower()
            if any(word in commit_lower for word in ["fix", "bugfix"]):
                categories["fixed"].append(commit)
            elif any(word in commit_lower for word in ["add", "new", "feature"]):
                categories["added"].append(commit)
            elif any(word in commit_lower for word in ["remove", "delete"]):
                categories["removed"].append(commit)
            else:
                categories["changed"].append(commit)

        # Determine bump type
        bump_type = "patch"
        if any("breaking" in c.lower() for c in commits):
            bump_type = "major"
        elif categories["added"]:
            bump_type = "minor"

        return {
            "commits": commits,
            "categories": categories,
            "bump_type": bump_type,
            "files_modified": [c.file_path for c in changes],
        }

    def _parse_git_status_code(self, code: str) -> str:
        """Parse git status code (backward compatibility).

        Args:
            code: Git status code

        Returns:
            Human-readable status
        """
        mapping = {
            "M": "modified",
            "A": "added",
            "D": "deleted",
            "R": "renamed",
            "C": "copied",
            "U": "updated",
            "??": "untracked",
        }
        return mapping.get(code, "unknown")


# Backward compatibility alias
UpdateManagerClass = UpdateManager
