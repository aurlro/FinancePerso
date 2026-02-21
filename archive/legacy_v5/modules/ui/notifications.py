"""Notification settings UI component - LEGACY WRAPPER.

DEPRECATED: This module is kept for backward compatibility.
Use `from modules.ui_v2.organisms.config import render_notification_settings` instead.
"""

import warnings

# Emit deprecation warning on import
warnings.warn(
    "modules.ui.config.notifications is deprecated. "
    "Use modules.ui_v2.organisms.config.notifications instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from modules.ui_v2.organisms.config.notifications import (
    render_notification_settings,
)

__all__ = ["render_notification_settings"]
