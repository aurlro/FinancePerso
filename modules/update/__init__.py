"""Update management module.

Provides functionality for version management, changelog generation,
and git analysis for tracking changes.

Example:
    from modules.update.manager import UpdateManager
    
    manager = UpdateManager()
    version = manager.get_current_version()
    new_version = manager.bump_version(version, "minor")
"""

from modules.update.manager import UpdateManager
from modules.update.models import VersionEntry, ChangeType

__all__ = ["UpdateManager", "VersionEntry", "ChangeType"]
