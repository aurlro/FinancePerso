"""API settings UI component - LEGACY WRAPPER.

DEPRECATED: This module is kept for backward compatibility.
Use `from modules.ui_v2.organisms.config import render_api_settings` instead.
"""

import warnings

# Emit deprecation warning on import
warnings.warn(
    "modules.ui.config.api_settings is deprecated. "
    "Use modules.ui_v2.organisms.config.api_settings instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from modules.ui_v2.organisms.config.api_settings import (
    load_env_vars,
    render_api_settings,
    set_secure_env_permissions,
    validate_api_key,
)

__all__ = [
    "load_env_vars",
    "render_api_settings",
    "set_secure_env_permissions",
    "validate_api_key",
]
