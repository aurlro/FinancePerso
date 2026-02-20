"""Update creation utilities."""

from datetime import datetime
from typing import Optional

from modules.logger import logger
from modules.update.git import GitAnalyzer, GitChange
from modules.update.models import ChangeType, VersionEntry


class UpdateCreator:
    """Creates version entries from git changes."""

    def __init__(self, repo_path: str):
        """Initialize update creator.

        Args:
            repo_path: Path to the git repository
        """
        self.git = GitAnalyzer(repo_path)

    def create_entry(
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
            VersionEntry populated with changes
        """
        changes = self.git.get_changes_since(since_ref)
        commits = self.git.get_commit_messages(since_ref)

        entry = VersionEntry(
            version=version,
            date=datetime.now().strftime("%Y-%m-%d"),
            title=title,
        )

        # Categorize changes
        for change in changes:
            self._categorize_file_change(entry, change)

        # Add commit messages as changes
        for commit in commits[:10]:  # Limit to 10 commits
            self._categorize_commit(entry, commit)

        return entry

    def _categorize_file_change(self, entry: VersionEntry, change: GitChange) -> None:
        """Categorize a file change and add to entry.

        Args:
            entry: VersionEntry to add to
            change: GitChange to categorize
        """
        # Skip certain files
        if self._should_skip_file(change.file_path):
            return

        # Categorize based on file type and change type
        if change.change_type == "added":
            entry.add_change(ChangeType.ADDED, f"Added {change.file_path}")
        elif change.change_type == "deleted":
            entry.add_change(ChangeType.REMOVED, f"Removed {change.file_path}")
        elif change.change_type == "modified":
            if "fix" in change.file_path.lower() or "bug" in change.file_path.lower():
                entry.add_change(ChangeType.FIXED, f"Fixed {change.file_path}")
            else:
                entry.add_change(ChangeType.CHANGED, f"Updated {change.file_path}")

    def _categorize_commit(self, entry: VersionEntry, commit: str) -> None:
        """Categorize a commit message and add to entry.

        Args:
            entry: VersionEntry to add to
            commit: Commit message
        """
        commit_lower = commit.lower()

        # Skip merge commits
        if commit_lower.startswith("merge"):
            return

        # Categorize based on commit message
        if any(word in commit_lower for word in ["fix", "bugfix", "hotfix"]):
            entry.add_change(ChangeType.FIXED, commit)
        elif any(word in commit_lower for word in ["add", "new", "feature"]):
            entry.add_change(ChangeType.ADDED, commit)
        elif any(word in commit_lower for word in ["remove", "delete", "drop"]):
            entry.add_change(ChangeType.REMOVED, commit)
        elif any(word in commit_lower for word in ["security", "vulnerability", "cve"]):
            entry.add_change(ChangeType.SECURITY, commit)
        elif any(word in commit_lower for word in ["deprecate"]):
            entry.add_change(ChangeType.DEPRECATED, commit)
        else:
            entry.add_change(ChangeType.CHANGED, commit)

    def _should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped in changelog.

        Args:
            file_path: Path to check

        Returns:
            True if file should be skipped
        """
        skip_patterns = [
            ".pyc",
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "*.log",
            ".coverage",
            ".pytest_cache",
        ]

        file_lower = file_path.lower()
        return any(pattern in file_lower for pattern in skip_patterns)

    def suggest_version_bump(self, since_ref: Optional[str] = None) -> str:
        """Suggest version bump type based on changes.

        Args:
            since_ref: Git reference to compare against

        Returns:
            Suggested bump type: "major", "minor", or "patch"
        """
        changes = self.git.get_changes_since(since_ref)
        commits = self.git.get_commit_messages(since_ref)

        # Check for breaking changes
        for commit in commits:
            if any(
                indicator in commit.lower()
                for indicator in ["breaking", "break", "major", "!:"]
            ):
                return "major"

        # Check for new features
        for commit in commits:
            if any(
                indicator in commit.lower()
                for indicator in ["feature", "feat", "add ", "new "]
            ):
                return "minor"

        # Default to patch
        return "patch"
