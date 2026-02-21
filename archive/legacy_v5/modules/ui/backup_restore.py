"""Backup and restore UI component - LEGACY WRAPPER.

DEPRECATED: This module is kept for backward compatibility.
Use `from modules.ui_v2.organisms.config import render_backup_restore` instead.
"""

import warnings

# Emit deprecation warning on import
warnings.warn(
    "modules.ui.config.backup_restore is deprecated. "
    "Use modules.ui_v2.organisms.config.backup_restore instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from modules.ui_v2.organisms.config.backup_restore import (
    create_backup,
    delete_backup,
    list_backups,
    render_backup_restore,
)

__all__ = [
    "create_backup",
    "delete_backup",
    "list_backups",
    "render_backup_restore",
]
