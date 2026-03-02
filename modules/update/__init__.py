"""Update management module.

Provides functionality for version management, changelog generation,
and git analysis for tracking changes.

Example:
    from modules.update.manager import UpdateManager

    manager = UpdateManager()
    version = manager.get_current_version()
    new_version = manager.bump_version(version, "minor")
"""

from modules.update.manager import UpdateManager, quick_update
from modules.update.models import VersionEntry, ChangeType

# Singleton instance for backward compatibility
_update_manager = None


def get_update_manager() -> UpdateManager:
    """Get the singleton UpdateManager instance."""
    global _update_manager
    if _update_manager is None:
        _update_manager = UpdateManager()
    return _update_manager


__all__ = ["UpdateManager", "VersionEntry", "ChangeType", "get_update_manager", "quick_update"]
