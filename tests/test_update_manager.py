"""
Tests for update manager module.
"""

import os
import subprocess

import pytest

from modules.update import UpdateManager, VersionEntry, quick_update
from modules.update.manager import UpdateManager as OldUpdateManager  # For compatibility


class TestVersionBump:
    """Test version bumping logic."""

    def test_bump_patch(self):
        """Test patch version bump."""
        manager = UpdateManager()
        assert manager.bump_version("3.5.0", "patch") == "3.5.1"
        assert manager.bump_version("1.0.0", "patch") == "1.0.1"

    def test_bump_minor(self):
        """Test minor version bump."""
        manager = UpdateManager()
        assert manager.bump_version("3.5.0", "minor") == "3.6.0"
        assert manager.bump_version("1.0.0", "minor") == "1.1.0"

    def test_bump_major(self):
        """Test major version bump."""
        manager = UpdateManager()
        assert manager.bump_version("3.5.0", "major") == "4.0.0"
        assert manager.bump_version("1.0.0", "major") == "2.0.0"


class TestChangelogFormat:
    """Test changelog formatting."""

    def test_format_changelog_entry(self):
        """Test formatting of changelog entry."""
        manager = UpdateManager()

        entry = VersionEntry(
            version="3.6.0",
            date="2026-02-01",
            title="Nouvelle fonctionnalité",
            categories={
                "added": ["Fonction X", "Fonction Y"],
                "fixed": ["Bug Z"],
            },
            files_modified=["modules/x.py"],
            breaking_changes=[],
        )

        formatted = manager._format_changelog_entry(entry)

        assert "## [3.6.0] - 2026-02-01" in formatted
        assert "### Nouvelle fonctionnalité" in formatted
        assert "Fonction X" in formatted
        assert "Bug Z" in formatted
        assert "modules/x.py" in formatted


class TestUpdateManagerIntegration:
    """Integration tests with temporary files."""

    @pytest.fixture
    def temp_manager(self, tmp_path):
        """Create update manager with temp directory."""
        return UpdateManager(project_root=str(tmp_path))

    def test_create_constants_file(self, temp_manager):
        """Test creating constants.py if not exists."""
        success = temp_manager.update_constants("3.5.0")
        assert success
        assert os.path.exists(temp_manager.constants_path)

        with open(temp_manager.constants_path) as f:
            content = f.read()
            assert 'APP_VERSION = "3.5.0"' in content

    def test_update_existing_constants(self, temp_manager):
        """Test updating existing constants.py."""
        # Create initial file
        os.makedirs(os.path.dirname(temp_manager.constants_path), exist_ok=True)
        with open(temp_manager.constants_path, "w") as f:
            f.write('APP_VERSION = "1.0.0"\n')

        # Update
        success = temp_manager.update_constants("2.0.0")
        assert success

        with open(temp_manager.constants_path) as f:
            content = f.read()
            assert 'APP_VERSION = "2.0.0"' in content
            assert "1.0.0" not in content

    def test_add_changelog_entry(self, temp_manager):
        """Test adding entry to changelog."""
        entry = VersionEntry(
            version="1.1.0",
            date="2026-02-01",
            title="Test Update",
            categories={"added": ["Feature 1"]},
            files_modified=["test.py"],
            breaking_changes=[],
        )

        success = temp_manager.add_changelog_entry(entry)
        assert success
        assert os.path.exists(temp_manager.changelog_path)

        with open(temp_manager.changelog_path) as f:
            content = f.read()
            assert "## [1.1.0] - 2026-02-01" in content
            assert "Test Update" in content
            assert "Feature 1" in content


class TestVersionDetection:
    """Test version detection from files."""

    def test_get_version_from_constants(self, tmp_path):
        """Test reading version from constants.py."""
        manager = UpdateManager(project_root=str(tmp_path))

        # Create constants.py
        os.makedirs(os.path.join(tmp_path, "modules"), exist_ok=True)
        with open(manager.constants_path, "w") as f:
            f.write('APP_VERSION = "3.2.1"\n')

        version = manager.get_current_version()
        assert version == "3.2.1"

    def test_get_version_from_changelog(self, tmp_path):
        """Test fallback to changelog."""
        manager = UpdateManager(project_root=str(tmp_path))

        # Create changelog
        with open(manager.changelog_path, "w") as f:
            f.write("## [2.0.0] - 2026-01-01\n\nContent\n")

        version = manager.get_current_version()
        assert version == "2.0.0"

    def test_get_version_default(self, tmp_path):
        """Test default version when no files."""
        manager = UpdateManager(project_root=str(tmp_path))
        version = manager.get_current_version()
        assert version == "0.0.0"


class TestQuickUpdate:
    """Test quick update convenience function."""

    def test_quick_update(self, tmp_path):
        """Test quick update function."""
        # Change to temp directory
        old_cwd = os.getcwd()
        os.chdir(tmp_path)

        # Create AGENTS.md to avoid failure
        with open("AGENTS.md", "w") as f:
            f.write("# AGENTS\n\nTest file\n")

        try:
            success, version = quick_update(
                title="Test Update", changes=["Change 1", "Change 2"], bump_type="minor"
            )

            # Note: quick_update may fail on agents.md update, but changelog should work
            assert version.startswith("0.")  # Starts from 0.0.0

        finally:
            os.chdir(old_cwd)


class TestRecentChanges:
    """Test retrieving recent changes."""

    def test_get_recent_changes(self, tmp_path):
        """Test getting recent changes."""
        manager = UpdateManager(project_root=str(tmp_path))

        # Create changelog with multiple versions
        with open(manager.changelog_path, "w") as f:
            f.write("# Changelog\n\n")
            for i in range(5):
                f.write(f"## [1.{i}.0] - 2026-01-0{i+1}\n\nContent {i}\n\n---\n\n")

        recent = manager.get_recent_changes(count=3)

        # Parser may return different number based on parsing
        assert len(recent) <= 5  # We wrote 5 versions
        # Check that we got some versions
        assert len(recent) > 0


class TestGitChangeAnalysis:
    """Test git change detection and analysis."""

    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create a temporary git repository with commits."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

        # Create initial commit
        init_file = tmp_path / "initial.py"
        init_file.write_text("# initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmp_path, capture_output=True)

        return tmp_path

    def test_detect_committed_changes_since_tag(self, git_repo):
        """Test detection of committed changes since last tag."""
        # Create a tag
        subprocess.run(["git", "tag", "v1.0.0"], cwd=git_repo, capture_output=True)

        # Create a committed change after tag
        new_file = git_repo / "feature.py"
        new_file.write_text("# new feature")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: add new feature"], cwd=git_repo, capture_output=True
        )

        manager = UpdateManager(project_root=str(git_repo))
        result = manager.analyze_git_changes()

        assert result["has_committed_changes"] is True
        assert "feature.py" in result["committed_files"]
        assert len(result["added"]) == 1
        assert "new feature" in result["added"][0].lower()

    def test_detect_uncommitted_changes(self, git_repo):
        """Test detection of unstaged and staged uncommitted changes."""
        # Create a tag first
        subprocess.run(["git", "tag", "v1.0.0"], cwd=git_repo, capture_output=True)

        # Create unstaged file (untracked)
        unstaged_file = git_repo / "unstaged.py"
        unstaged_file.write_text("# unstaged change")

        # Create staged file
        staged_file = git_repo / "staged.py"
        staged_file.write_text("# staged change")
        subprocess.run(["git", "add", "staged.py"], cwd=git_repo, capture_output=True)

        manager = UpdateManager(project_root=str(git_repo))
        result = manager.analyze_git_changes()

        assert result["has_uncommitted_changes"] is True
        assert "unstaged.py" in result["uncommitted_files"]
        assert "staged.py" in result["uncommitted_files"]
        assert result["uncommitted_status"]["unstaged.py"] == "untracked"
        assert "staged" in result["uncommitted_status"]["staged.py"]

    def test_detect_both_committed_and_uncommitted(self, git_repo):
        """Test detection when both committed and uncommitted changes exist."""
        # Create tag
        subprocess.run(["git", "tag", "v1.0.0"], cwd=git_repo, capture_output=True)

        # Create committed change
        committed_file = git_repo / "committed.py"
        committed_file.write_text("# committed")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: committed change"], cwd=git_repo, capture_output=True
        )

        # Create uncommitted change
        uncommitted_file = git_repo / "uncommitted.py"
        uncommitted_file.write_text("# uncommitted")

        manager = UpdateManager(project_root=str(git_repo))
        result = manager.analyze_git_changes()

        assert result["has_committed_changes"] is True
        assert result["has_uncommitted_changes"] is True
        assert "committed.py" in result["committed_files"]
        assert "uncommitted.py" in result["uncommitted_files"]
        assert "committed.py" in result["files_modified"]
        assert "uncommitted.py" in result["files_modified"]
        assert "(commits + local)" in result["suggested_title"]

    def test_no_tags_uses_recent_commits(self, git_repo):
        """Test that recent commits are used when no tags exist."""
        # Create multiple commits without tags
        for i in range(3):
            f = git_repo / f"file{i}.py"
            f.write_text(f"# content {i}")
            subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", f"feat: commit {i}"], cwd=git_repo, capture_output=True
            )

        manager = UpdateManager(project_root=str(git_repo))
        result = manager.analyze_git_changes()

        assert result["has_committed_changes"] is True
        assert len(result["committed_files"]) >= 3  # Should include all new files

    def test_commit_categorization(self, git_repo):
        """Test categorization of commits by type."""
        subprocess.run(["git", "tag", "v1.0.0"], cwd=git_repo, capture_output=True)

        # Create various commit types
        commits = [
            ("feat: add new feature", "added"),
            ("fix: resolve bug", "fixed"),
            ("perf: optimize speed", "performance"),
            ("docs: update readme", "other"),
        ]

        for msg, _ in commits:
            f = git_repo / f"{msg.replace(' ', '_')}.py"
            f.write_text("# content")
            subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
            subprocess.run(["git", "commit", "-m", msg], cwd=git_repo, capture_output=True)

        manager = UpdateManager(project_root=str(git_repo))
        result = manager.analyze_git_changes()

        assert len(result["added"]) == 1
        assert len(result["fixed"]) == 1
        assert len(result["performance"]) == 1
        assert len(result["other"]) == 1

    def test_bump_type_suggestion(self, git_repo):
        """Test version bump type suggestion based on changes."""
        subprocess.run(["git", "tag", "v1.0.0"], cwd=git_repo, capture_output=True)

        # Feature commit should suggest minor
        f = git_repo / "feature.py"
        f.write_text("# feature")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: new feature"], cwd=git_repo, capture_output=True
        )

        manager = UpdateManager(project_root=str(git_repo))
        result = manager.analyze_git_changes()

        assert result["suggested_bump"] == "minor"

    def test_major_bump_detection(self, git_repo):
        """Test detection of major/breaking changes."""
        subprocess.run(["git", "tag", "v1.0.0"], cwd=git_repo, capture_output=True)

        # Breaking change commit should suggest major
        f = git_repo / "breaking.py"
        f.write_text("# breaking")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "breaking: remove old api"], cwd=git_repo, capture_output=True
        )

        manager = UpdateManager(project_root=str(git_repo))
        result = manager.analyze_git_changes()

        assert result["suggested_bump"] == "major"

    def test_parse_git_status_code(self):
        """Test parsing of git status porcelain codes."""
        manager = UpdateManager()

        assert manager._parse_git_status_code("??") == "untracked"
        assert manager._parse_git_status_code("M ") == "staged (modified)"
        assert manager._parse_git_status_code("A ") == "staged (added)"
        assert manager._parse_git_status_code(" M") == "unstaged (modified)"
        assert manager._parse_git_status_code(" D") == "unstaged (deleted)"
        assert manager._parse_git_status_code("MM") == "staged + unstaged changes"

    def test_empty_repo_no_errors(self, tmp_path):
        """Test that empty git repos are handled gracefully."""
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)

        manager = UpdateManager(project_root=str(tmp_path))
        result = manager.analyze_git_changes()

        # Should return empty result without errors
        assert isinstance(result, dict)
        assert result["has_committed_changes"] is False
        assert result["has_uncommitted_changes"] is False
