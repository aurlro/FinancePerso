"""Audit tools UI component - LEGACY WRAPPER.

DEPRECATED: This module is kept for backward compatibility.
Use `from modules.ui_v2.organisms.config import render_audit_tools` instead.
"""

import warnings

# Emit deprecation warning on import
warnings.warn(
    "modules.ui.config.audit_tools is deprecated. "
    "Use modules.ui_v2.organisms.config.audit_tools instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from modules.ui_v2.organisms.config.audit_tools import (
    render_audit_tools,
)

__all__ = ["render_audit_tools"]
