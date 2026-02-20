"""Update Manager for FinancePerso.

DEPRECATED: This module is kept for backward compatibility.
Please use modules.update.manager instead.

Example:
    # Old way (deprecated)
    from modules.update_manager import UpdateManager

    # New way (recommended)
    from modules.update.manager import UpdateManager
"""

import warnings
from typing import List, Tuple

# Import from new location for backward compatibility
from modules.update.manager import UpdateManager, UpdateManagerClass
from modules.update.models import ChangeType, VersionEntry
from modules.update.changelog import ChangelogManager
from modules.update.version import VersionManager
from modules.update.git import GitAnalyzer, GitChange
from modules.update.creator import UpdateCreator

# Issue deprecation warning
warnings.warn(
    "modules.update_manager is deprecated. Use modules.update.manager instead.",
    DeprecationWarning,
    stacklevel=2,
)


# Backward compatibility functions
def get_update_manager() -> UpdateManager:
    """Get default update manager instance."""
    return UpdateManager()


def quick_update(title: str, changes: List[str], bump_type: str = "patch") -> Tuple[bool, str]:
    """
    Quick update with default categorization.

    DEPRECATED: Use UpdateManager.create_release() instead.

    Args:
        title: Update title
        changes: List of changes (will be categorized as "added")
        bump_type: Version bump type

    Returns:
        Tuple of (success, new_version)
    """
    warnings.warn(
        "quick_update is deprecated. Use UpdateManager.create_release() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    manager = get_update_manager()
    success, version = manager.create_release(bump_type=bump_type, title=title)
    return success, version


__all__ = [
    "UpdateManager",
    "UpdateManagerClass",
    "VersionEntry",
    "ChangeType",
    "ChangelogManager",
    "VersionManager",
    "GitAnalyzer",
    "GitChange",
    "UpdateCreator",
    "get_update_manager",
    "quick_update",
]
