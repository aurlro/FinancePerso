"""Data operations UI component - LEGACY WRAPPER.

DEPRECATED: This module is kept for backward compatibility.
Use `from modules.ui_v2.organisms.config import render_data_operations` instead.
"""

import warnings

# Emit deprecation warning on import
warnings.warn(
    "modules.ui.config.data_operations is deprecated. "
    "Use modules.ui_v2.organisms.config.data_operations instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from modules.ui_v2.organisms.config.data_operations import (
    render_data_operations,
    render_export_section,
)

__all__ = [
    "render_data_operations",
    "render_export_section",
]
