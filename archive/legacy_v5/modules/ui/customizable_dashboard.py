"""
Customizable Dashboard System - LEGACY WRAPPER
=============================================

⚠️ DEPRECATED: This module is kept for backward compatibility.

New location: modules.ui_v2.templates

Migration guide:
    OLD: from modules.ui.dashboard.customizable_dashboard import DashboardLayoutManager
    NEW: from modules.ui_v2.templates import DashboardLayoutManager
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "modules.ui.dashboard.customizable_dashboard is deprecated. "
    "Use modules.ui_v2.templates instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from new location
from modules.ui_v2.templates.layouts import (
    DEFAULT_LAYOUT,
    LAYOUT_TEMPLATES,
    DashboardWidget,
    WidgetType,
)
from modules.ui_v2.templates.manager import DashboardLayoutManager
from modules.ui_v2.templates.renderer import (
    render_customizable_overview,
    render_dashboard_configurator,
)

__all__ = [
    "WidgetType",
    "DashboardWidget",
    "DashboardLayoutManager",
    "LAYOUT_TEMPLATES",
    "DEFAULT_LAYOUT",
    "render_dashboard_configurator",
    "render_customizable_overview",
]
