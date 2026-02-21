"""Category management UI component - LEGACY WRAPPER.

DEPRECATED: This module is kept for backward compatibility.
Use `from modules.ui_v2.organisms.config import render_category_management` instead.
"""

import warnings

# Emit deprecation warning on import
warnings.warn(
    "modules.ui.config.category_management is deprecated. "
    "Use modules.ui_v2.organisms.config.category_management instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from modules.ui_v2.organisms.config.category_management import (
    render_category_management,
)

__all__ = ["render_category_management"]
