"""Member management UI component - LEGACY WRAPPER.

DEPRECATED: This module is kept for backward compatibility.
Use `from modules.ui_v2.organisms.config import render_member_management` instead.
"""

import warnings

# Emit deprecation warning on import
warnings.warn(
    "modules.ui.config.member_management is deprecated. "
    "Use modules.ui_v2.organisms.config.member_management instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from modules.ui_v2.organisms.config.member_management import (
    render_member_management,
)

__all__ = ["render_member_management"]
