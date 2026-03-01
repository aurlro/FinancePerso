"""Dashboard V5.5 - Composants du tableau de bord.

Usage:
    from modules.ui.v5_5.dashboard import render_dashboard_v5
    
    render_dashboard_v5()
"""

from .dashboard_v5 import render_dashboard_v5, render_dashboard_simple
from .kpi_grid import render_kpi_grid, calculate_kpis
from .empty_state import render_dashboard_empty, render_onboarding_mini

try:
    from .couple_summary import render_couple_summary
    _COUPLE_AVAILABLE = True
except ImportError:
    _COUPLE_AVAILABLE = False

__all__ = [
    "render_dashboard_v5",
    "render_dashboard_simple",
    "render_kpi_grid",
    "calculate_kpis",
    "render_dashboard_empty",
    "render_onboarding_mini",
    "render_couple_summary",
]
