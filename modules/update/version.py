"""Version management utilities."""

import os
import re
from typing import Optional

from modules.logger import logger


class VersionManager:
    """Manages version numbers and version file operations."""

    DEFAULT_VERSION = "0.0.0"

    def __init__(self, project_root: str):
        """Initialize version manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.constants_path = os.path.join(project_root, "modules", "constants.py")
        self.changelog_path = os.path.join(project_root, "CHANGELOG.md")

    def get_current_version(self) -> str:
        """Extract current version from constants.py or changelog.

        Returns:
            Current version string (e.g., "3.5.0")
        """
        # Try constants.py first
        version = self._get_version_from_constants()
        if version:
            return version

        # Fallback to changelog
        version = self._get_version_from_changelog()
        if version:
            return version

        return self.DEFAULT_VERSION

    def _get_version_from_constants(self) -> Optional[str]:
        """Try to extract version from constants.py.

        Returns:
            Version string or None if not found
        """
        if not os.path.exists(self.constants_path):
            return None

        try:
            with open(self.constants_path, encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        except Exception as e:
            logger.warning(f"Could not read constants.py: {e}")

        return None

    def _get_version_from_changelog(self) -> Optional[str]:
        """Try to extract version from CHANGELOG.md.

        Returns:
            Version string or None if not found
        """
        if not os.path.exists(self.changelog_path):
            return None

        try:
            with open(self.changelog_path, encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"## \[?([0-9]+\.[0-9]+\.[0-9]+)\]?", content)
                if match:
                    return match.group(1)
        except Exception as e:
            logger.warning(f"Could not read CHANGELOG.md: {e}")

        return None

    def bump_version(self, version: str, bump_type: str = "patch") -> str:
        """Bump version number.

        Args:
            version: Current version (e.g., "3.5.0")
            bump_type: Type of bump: "major", "minor", or "patch"

        Returns:
            New version string

        Raises:
            ValueError: If version format is invalid or bump_type is unknown
        """
        try:
            parts = version.split(".")
            if len(parts) != 3:
                raise ValueError(f"Invalid version format: {version}")

            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid version format: {version}") from e

        bump_type = bump_type.lower()
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Unknown bump type: {bump_type}")

        return f"{major}.{minor}.{patch}"

    def update_version_in_constants(self, new_version: str) -> bool:
        """Update version in constants.py file.

        Args:
            new_version: New version string

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.constants_path), exist_ok=True)

            if os.path.exists(self.constants_path):
                # Update existing file
                with open(self.constants_path, encoding="utf-8") as f:
                    content = f.read()

                new_content = re.sub(
                    r'APP_VERSION\s*=\s*["\']([^"\']+)["\']',
                    f'APP_VERSION = "{new_version}"',
                    content,
                )
            else:
                # Create new file with default content
                new_content = f'''"""Application constants."""

APP_VERSION = "{new_version}"
'''

            with open(self.constants_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info(f"Updated version in constants.py to {new_version}")
            return True

        except Exception as e:
            logger.error(f"Failed to update version in constants.py: {e}")
            return False
