"""Legacy compatibility wrappers for config UI components.

This module provides backward compatibility for imports from the old location.
All functions delegate to the new implementations in ui_v2.

DEPRECATED: Use `from modules.ui_v2.organisms.config import ...` instead.
"""

import warnings
from typing import Any, Dict, List, Optional

# Import from the new structure
from modules.ui_v2.organisms.config.api_settings import (
    load_env_vars,
    render_api_settings,
    set_secure_env_permissions,
    validate_api_key,
)
from modules.ui_v2.organisms.config.audit_tools import render_audit_tools
from modules.ui_v2.organisms.config.backup_restore import (
    create_backup,
    delete_backup,
    list_backups,
    render_backup_restore,
)
from modules.ui_v2.organisms.config.category_management import render_category_management
from modules.ui_v2.organisms.config.data_operations import (
    render_data_operations,
    render_export_section,
)
from modules.ui_v2.organisms.config.member_management import render_member_management
from modules.ui_v2.organisms.config.notifications import render_notification_settings
from modules.ui_v2.organisms.config.tags_rules import render_tags_rules

# Show deprecation warning
warnings.warn(
    "modules.ui.config is deprecated. Use modules.ui_v2.organisms.config instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    # Main render functions
    "render_member_management",
    "render_category_management",
    "render_api_settings",
    "render_audit_tools",
    "render_backup_restore",
    "render_data_operations",
    "render_export_section",
    "render_notification_settings",
    "render_tags_rules",
    # Utility functions
    "create_backup",
    "list_backups",
    "delete_backup",
    "load_env_vars",
    "validate_api_key",
    "set_secure_env_permissions",
]


# Wrapped functions with deprecation warnings

def _warn_deprecated(old_name: str, new_name: str) -> None:
    """Emit deprecation warning for moved functions."""
    warnings.warn(
        f"{old_name} is deprecated, use {new_name} instead",
        DeprecationWarning,
        stacklevel=3,
    )
