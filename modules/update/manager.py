"""Update Manager - Facade for update operations.

Provides a unified interface for version management, changelog operations,
and git analysis.
"""

import os
import re
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

    def create_update_entry(
        self,
        title: str,
        changes: dict[str, list[str]],
        bump_type: str = "patch",
        files_modified: list[str] | None = None,
        breaking_changes: list[str] | None = None,
        force: bool = False,
    ) -> tuple[bool, str]:
        """Create a complete update entry with changelog and version bump.

        This is a high-level method that:
        1. Bumps the version
        2. Creates a VersionEntry with the provided changes
        3. Adds the entry to CHANGELOG.md
        4. Updates version in constants.py

        Args:
            title: Update title/description
            changes: Dictionary with keys 'added', 'fixed', 'performance' containing lists of changes
            bump_type: Type of version bump (patch, minor, major)
            files_modified: List of files modified in this update
            breaking_changes: List of breaking changes (if any)
            force: Whether to force creation even if duplicate

        Returns:
            Tuple of (success, version_or_error_message)
        """
        try:
            # Get current version and bump
            current = self.get_current_version()
            new_version = self.bump_version(current, bump_type)

            # Create VersionEntry
            from modules.update.models import VersionEntry
            from datetime import datetime

            entry = VersionEntry(
                version=new_version,
                title=title,
                date=datetime.now().strftime("%Y-%m-%d"),
                categories={
                    "added": changes.get("added", []),
                    "fixed": changes.get("fixed", []),
                    "performance": changes.get("performance", []),
                },
                files_modified=files_modified or [],
                breaking_changes=breaking_changes or [],
            )

            # Add to changelog
            if not self.add_changelog_entry(entry):
                return False, "Failed to add changelog entry"

            # Update version in constants.py
            if not self.update_version_in_files(new_version):
                logger.warning("Failed to update version in constants.py")

            return True, new_version

        except Exception as e:
            logger.error(f"Failed to create update: {e}")
            return False, str(e)

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
        """Analyze git changes with AI-powered summary generation.

        Args:
            since_tag: Whether to analyze since last tag

        Returns:
            Dictionary with change analysis including suggested title,
            categorized changes, and version bump recommendation
        """
        import re

        ref = None if since_tag else "HEAD~10"
        changes = self._git.get_changes_since(ref)
        commits = self._git.get_commit_messages(ref)

        # Also get uncommitted changes
        uncommitted = self._git.get_uncommitted_changes()
        uncommitted_files = list(uncommitted.keys()) if uncommitted else []

        # Combine all files
        all_files = list(set([c.file_path for c in changes] + uncommitted_files))

        # Categorize changes based on commit messages and file patterns
        added = []
        fixed = []
        performance = []
        changed = []

        # Keywords for categorization
        add_keywords = [
            "add",
            "new",
            "feature",
            "implement",
            "create",
            "introduce",
            "ajout",
            "nouveau",
            "fonctionnalité",
            "implémente",
        ]
        fix_keywords = [
            "fix",
            "bugfix",
            "correct",
            "repair",
            "resolve",
            "bug",
            "correction",
            "corrige",
            "résout",
            "répare",
        ]
        perf_keywords = [
            "perf",
            "optim",
            "speed",
            "fast",
            "cache",
            "improve",
            "performance",
            "optimisation",
            "améliore",
            "rapide",
        ]
        breaking_keywords = [
            "breaking",
            "break",
            "remove",
            "delete",
            "deprecate",
            "supprime",
            "retire",
            "déprécie",
        ]

        for commit in commits:
            commit_lower = commit.lower()
            is_breaking = any(kw in commit_lower for kw in breaking_keywords)

            if any(kw in commit_lower for kw in fix_keywords):
                fixed.append(commit)
            elif any(kw in commit_lower for kw in perf_keywords):
                performance.append(commit)
            elif any(kw in commit_lower for kw in add_keywords):
                added.append(commit)
            else:
                changed.append(commit)

        # Analyze file patterns for additional insights
        has_new_module = any("modules/" in f and f.endswith(".py") for f in all_files)
        has_new_page = any("pages/" in f and f.endswith(".py") for f in all_files)
        has_test = any("test" in f.lower() for f in all_files)
        has_doc = any(f.endswith(".md") for f in all_files)
        has_config = any(f.endswith((".toml", ".cfg", ".ini", ".yaml", ".yml")) for f in all_files)

        # Generate suggested title based on dominant change type
        # Include indicator if both committed and uncommitted changes exist
        has_committed = len(commits) > 0 or len(changes) > 0
        has_uncommitted = len(uncommitted_files) > 0
        has_both = has_committed and has_uncommitted
        suggested_title = self._generate_suggested_title(
            commits, added, fixed, performance, all_files, has_new_module, has_new_page, has_both
        )

        # Determine bump type
        has_breaking = any("breaking" in c.lower() for c in commits)
        suggested_bump = self._determine_bump_type(
            has_breaking, added, fixed, performance, changed, has_new_module, has_new_page
        )

        # Generate detailed change descriptions
        added_items = self._generate_change_descriptions(added, "add") if added else []
        fixed_items = self._generate_change_descriptions(fixed, "fix") if fixed else []
        perf_items = self._generate_change_descriptions(performance, "perf") if performance else []

        # Add file-based detections if no commits
        if not commits and uncommitted_files:
            added_items.extend(self._detect_changes_from_files(uncommitted_files))

        # Generate "other" items (changed items without specific categorization)
        other_items = self._generate_change_descriptions(changed, "other") if changed else []

        return {
            "commits": commits,
            "categories": {
                "added": added,
                "changed": changed,
                "fixed": fixed,
                "removed": [],
                "other": changed,
            },
            "bump_type": suggested_bump,
            "suggested_bump": suggested_bump,
            "files_modified": all_files,
            "suggested_title": suggested_title,
            "added": added_items,
            "fixed": fixed_items,
            "performance": perf_items,
            "other": other_items,
            "has_committed_changes": len(commits) > 0,
            "has_uncommitted_changes": len(uncommitted_files) > 0,
            "committed_files": [c.file_path for c in changes],
            "uncommitted_files": uncommitted_files,
            "uncommitted_status": uncommitted,
        }

    def _generate_suggested_title(
        self,
        commits,
        added,
        fixed,
        performance,
        files,
        has_new_module,
        has_new_page,
        has_both_committed_and_uncommitted: bool = False,
    ) -> str:
        """Generate a suggested title based on changes."""
        title_suffix = " (commits + local)" if has_both_committed_and_uncommitted else ""

        if not commits:
            if has_new_page:
                return "Nouvelle page ajoutée" + title_suffix
            elif has_new_module:
                return "Nouveau module ajouté" + title_suffix
            elif files:
                return f"Mise à jour de {len(files)} fichier(s)" + title_suffix
            return "Mise à jour" + title_suffix

        # Look for the most significant change
        if added and has_new_page:
            return "Nouvelle page fonctionnelle" + title_suffix
        elif added and has_new_module:
            return "Nouveau module fonctionnel" + title_suffix
        elif performance and len(performance) >= len(added) and len(performance) >= len(fixed):
            return "Optimisations et améliorations de performance" + title_suffix
        elif fixed and len(fixed) >= len(added):
            return "Corrections de bugs et stabilisation" + title_suffix
        elif added:
            # Try to extract feature name from first added commit
            first_add = added[0]
            # Clean up common prefixes
            clean = re.sub(
                r"^(add|new|feature|implement|ajout|nouveau)\s*[:\-]?\s*", "", first_add, flags=re.I
            )
            if clean:
                return clean.capitalize() + title_suffix
            return "Nouvelles fonctionnalités" + title_suffix

        # Default to first commit message
        return (commits[0].capitalize() if commits else "Mise à jour") + title_suffix

    def _determine_bump_type(
        self, has_breaking, added, fixed, performance, changed, has_new_module, has_new_page
    ) -> str:
        """Determine the recommended version bump type."""
        if has_breaking:
            return "major"

        total_additions = len(added)
        total_changes = len(changed)

        # Significant new features = minor
        if total_additions >= 2 or has_new_module or has_new_page:
            return "minor"

        # Single new feature = minor
        if total_additions == 1:
            return "minor"

        # Only fixes = patch
        if fixed and not added and not performance:
            return "patch"

        # Mixed small changes = patch
        return "patch"

    def _generate_change_descriptions(self, commits: list, change_type: str) -> list:
        """Generate user-friendly descriptions from commit messages."""
        descriptions = []

        for commit in commits:
            # Clean up the commit message
            clean = commit.strip()

            # Remove common prefixes
            clean = re.sub(
                r"^(fix|add|new|feature|implement|perf|optim|refactor|doc|test|chore)\s*[:\-]?\s*",
                "",
                clean,
                flags=re.I,
            )

            # Capitalize first letter
            if clean:
                clean = clean[0].upper() + clean[1:] if len(clean) > 1 else clean.upper()
                descriptions.append(clean)

        return descriptions

    def _detect_changes_from_files(self, files: list) -> list:
        """Detect changes from file modifications when no commits available."""
        changes = []

        for f in files:
            if "pages/" in f and f.endswith(".py"):
                page_name = f.split("/")[-1].replace(".py", "").replace("_", " ")
                changes.append(f"Amélioration de la page {page_name}")
            elif "modules/" in f and f.endswith(".py"):
                module_name = f.split("/")[-1].replace(".py", "").replace("_", " ")
                changes.append(f"Mise à jour du module {module_name}")
            elif f.endswith(".md"):
                changes.append(f"Documentation mise à jour ({f})")
            elif "test" in f.lower():
                changes.append(f"Tests améliorés ({f})")

        return changes

    def get_module_changes(self) -> dict:
        """Get changes by analyzing module files directly (fallback when no git).

        Returns:
            Dictionary with detected changes from file analysis
        """
        import os
        from pathlib import Path

        changed_files = []
        modules_dir = Path(self.project_root) / "modules"
        pages_dir = Path(self.project_root) / "pages"

        # Scan for recently modified files (within last 7 days)
        import time

        cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days

        for directory in [modules_dir, pages_dir]:
            if directory.exists():
                for file_path in directory.rglob("*.py"):
                    try:
                        mtime = file_path.stat().st_mtime
                        if mtime > cutoff_time:
                            changed_files.append(str(file_path.relative_to(self.project_root)))
                    except Exception:
                        pass

        # Analyze what type of changes
        has_new_module = any("modules/" in f and "__init__.py" not in f for f in changed_files)
        has_new_page = any("pages/" in f for f in changed_files)

        # Generate synthetic changes
        added = []
        if has_new_page:
            added.append("Nouvelle page ajoutée")
        if has_new_module:
            added.append("Nouveau module fonctionnel")

        return {
            "files_modified": changed_files,
            "added": added,
            "fixed": [],
            "performance": [],
            "suggested_title": self._generate_suggested_title(
                [], [], [], [], changed_files, has_new_module, has_new_page
            ),
            "suggested_bump": "minor" if (has_new_module or has_new_page) else "patch",
            "has_committed_changes": False,
            "has_uncommitted_changes": len(changed_files) > 0,
            "uncommitted_files": changed_files,
            "uncommitted_status": {f: "modified" for f in changed_files},
            "committed_files": [],
        }

    def _parse_git_status_code(self, code: str) -> str:
        """Parse git status code (backward compatibility).

        Args:
            code: Git status code (can be 2-char format like 'M ', ' M', '??', etc.)

        Returns:
            Human-readable status
        """
        # Handle 2-char porcelain format
        if len(code) == 2:
            staged, unstaged = code[0], code[1]

            # Check for both staged and unstaged changes first
            if staged != " " and unstaged != " " and code != "??":
                return "staged + unstaged changes"
            elif code == "??":
                return "untracked"
            elif staged == "A":
                return "staged (added)"
            elif staged == "M":
                return "staged (modified)"
            elif staged == "D":
                return "staged (deleted)"
            elif unstaged == "M":
                return "unstaged (modified)"
            elif unstaged == "D":
                return "unstaged (deleted)"
            elif staged == "R":
                return "renamed"
            elif staged == "C":
                return "copied"

        # Legacy single-char mapping
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

    # ==================== Backward Compatibility Methods ====================

    def get_recent_changes(self, count: int = 5) -> list[dict]:
        """Get recent changes from changelog (backward compatibility).

        Args:
            count: Number of recent changes to return

        Returns:
            List of recent change entries
        """
        try:
            content = self._changelog.read()
            if not content:
                return []

            # Simple parsing - look for version entries
            changes = []
            lines = content.split("\n")
            current_entry = None

            for line in lines:
                if line.startswith("## ["):
                    if current_entry:
                        changes.append(current_entry)
                        if len(changes) >= count:
                            break
                    version = line.split("[")[1].split("]")[0] if "[" in line else "unknown"
                    current_entry = {"version": version, "title": line, "content": []}
                elif current_entry and line.strip():
                    current_entry["content"].append(line)

            if current_entry and len(changes) < count:
                changes.append(current_entry)

            # Convert content lists to strings
            for entry in changes:
                entry["content"] = "\n".join(entry["content"])

            return changes
        except Exception as e:
            logger.warning(f"Could not get recent changes: {e}")
            return []


# Backward compatibility alias
UpdateManagerClass = UpdateManager


def quick_update(
    bump_type: str = "patch",
    title: Optional[str] = None,
    changes: Optional[dict | list] = None,
    project_root: Optional[str] = None,
) -> tuple[bool, str]:
    """Quick update function for backward compatibility.

    Args:
        bump_type: Type of version bump (patch, minor, major)
        title: Update title (auto-generated if None)
        changes: Dict with 'added', 'fixed', 'performance' lists, or a simple list of changes
        project_root: Project root directory

    Returns:
        Tuple of (success, version_or_error)
    """
    try:
        manager = UpdateManager(project_root)

        # Get current version and bump
        current = manager.get_current_version()
        new_version = manager.bump_version(current, bump_type)

        # Generate title if not provided
        if title is None:
            title = f"Release {new_version}"

        # Normalize changes parameter
        if changes is None:
            added, fixed, performance = [], [], []
        elif isinstance(changes, list):
            # Simple list of changes -> treat as added
            added = changes
            fixed, performance = [], []
        else:
            # Dict with specific categories
            added = changes.get("added", []) if isinstance(changes, dict) else []
            fixed = changes.get("fixed", []) if isinstance(changes, dict) else []
            performance = changes.get("performance", []) if isinstance(changes, dict) else []

        # Create update via creator
        from modules.update.models import VersionEntry, ChangeType

        entry = VersionEntry(
            version=new_version,
            title=title,
            date=__import__("datetime").datetime.now().strftime("%Y-%m-%d"),
            categories={
                "added": added,
                "fixed": fixed,
                "performance": performance,
            },
        )

        # Add to changelog
        if manager.add_changelog_entry(entry):
            # Update version in files
            manager.update_version_in_files(new_version)
            return True, new_version
        else:
            return False, "Failed to add changelog entry"

    except Exception as e:
        return False, str(e)
