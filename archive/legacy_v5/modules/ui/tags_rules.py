"""Tags and rules UI component - LEGACY WRAPPER.

DEPRECATED: This module is kept for backward compatibility.
Use `from modules.ui_v2.organisms.config import render_tags_rules` instead.
"""

import warnings

# Emit deprecation warning on import
warnings.warn(
    "modules.ui.config.tags_rules is deprecated. "
    "Use modules.ui_v2.organisms.config.tags_rules instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from modules.ui_v2.organisms.config.tags_rules import (
    render_tags_rules,
)

__all__ = ["render_tags_rules"]
