"""Git analysis utilities."""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from modules.logger import logger


@dataclass
class GitChange:
    """Represents a single git change.

    Attributes:
        file_path: Path to the changed file
        change_type: Type of change (added, modified, deleted)
        additions: Number of lines added
        deletions: Number of lines deleted
    """

    file_path: str
    change_type: str
    additions: int
    deletions: int


class GitAnalyzer:
    """Analyzes git repository for changes."""

    def __init__(self, repo_path: str):
        """Initialize git analyzer.

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)

    def is_git_repo(self) -> bool:
        """Check if path is a git repository.

        Returns:
            True if valid git repository
        """
        git_dir = self.repo_path / ".git"
        return git_dir.exists()

    def get_last_tag(self) -> Optional[str]:
        """Get the most recent git tag.

        Returns:
            Tag name or None if no tags exist
        """
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Could not get last tag: {e}")

        return None

    def get_changes_since(self, ref: Optional[str] = None) -> list[GitChange]:
        """Get changes since a git reference.

        Args:
            ref: Git reference (tag, commit, etc.). If None, uses last tag.

        Returns:
            List of GitChange objects
        """
        if ref is None:
            ref = self.get_last_tag()
            if ref is None:
                # Fallback: try to get all commits from the beginning
                ref = self._get_first_commit()
                if ref is None:
                    ref = "HEAD"  # Last resort

        return self._get_changes_from_git(ref)

    def _get_first_commit(self) -> Optional[str]:
        """Get the first commit hash in the repository.

        Returns:
            First commit hash or None
        """
        try:
            result = subprocess.run(
                ["git", "rev-list", "--max-parents=0", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass
        return None

    def _get_changes_from_git(self, ref: str) -> list[GitChange]:
        """Get changes from git diff.

        Args:
            ref: Git reference to compare against

        Returns:
            List of GitChange objects
        """
        try:
            # Get diff stats
            result = subprocess.run(
                ["git", "diff", ref, "HEAD", "--numstat"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode != 0:
                logger.warning(f"Git diff failed: {result.stderr}")
                return []

            return self._parse_numstat(result.stdout)

        except Exception as e:
            logger.error(f"Error getting git changes: {e}")
            return []

    def _parse_numstat(self, output: str) -> list[GitChange]:
        """Parse git numstat output.

        Args:
            output: Git numstat output

        Returns:
            List of GitChange objects
        """
        changes = []

        for line in output.strip().split("\n"):
            if not line or line.startswith("-"):
                continue

            parts = line.split("\t")
            if len(parts) != 3:
                continue

            additions_str, deletions_str, file_path = parts

            try:
                additions = int(additions_str) if additions_str != "-" else 0
                deletions = int(deletions_str) if deletions_str != "-" else 0
            except ValueError:
                continue

            # Determine change type
            if additions > 0 and deletions == 0:
                change_type = "added"
            elif additions == 0 and deletions > 0:
                change_type = "deleted"
            else:
                change_type = "modified"

            changes.append(
                GitChange(
                    file_path=file_path,
                    change_type=change_type,
                    additions=additions,
                    deletions=deletions,
                )
            )

        return changes

    def get_commit_messages(self, ref: Optional[str] = None) -> list[str]:
        """Get commit messages since reference.

        Args:
            ref: Git reference. If None, uses last tag.

        Returns:
            List of commit messages
        """
        if ref is None:
            ref = self.get_last_tag()
            if ref is None:
                # Fallback: try to get all commits from the beginning
                ref = self._get_first_commit()
                if ref is None:
                    return []  # No commits to show

        try:
            result = subprocess.run(
                ["git", "log", f"{ref}..HEAD", "--pretty=format:%s"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode == 0:
                messages = result.stdout.strip().split("\n")
                return [m for m in messages if m]  # Filter empty messages

        except Exception as e:
            logger.error(f"Error getting commit messages: {e}")

        return []

    def get_uncommitted_changes(self) -> dict[str, str]:
        """Get uncommitted changes in the working directory.

        Returns:
            Dictionary mapping file paths to their status
        """
        try:
            # Get status in porcelain format for parsing
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode != 0:
                return {}

            changes = {}
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                # Parse porcelain format: XY filename or XY "filename with spaces"
                status_code = line[:2]
                file_path = line[3:].strip()

                # Determine human-readable status
                if status_code == "??":
                    status = "untracked"
                elif status_code[0] == "A":
                    status = "staged (added)"
                elif status_code[0] == "M":
                    status = "staged (modified)"
                elif status_code[0] == "D":
                    status = "staged (deleted)"
                elif status_code[1] == "M":
                    status = "unstaged (modified)"
                elif status_code[1] == "D":
                    status = "unstaged (deleted)"
                elif status_code[0] != " " and status_code[1] != " ":
                    status = "staged + unstaged changes"
                else:
                    status = "modified"

                changes[file_path] = status

            return changes

        except Exception as e:
            logger.error(f"Error getting uncommitted changes: {e}")
            return {}
