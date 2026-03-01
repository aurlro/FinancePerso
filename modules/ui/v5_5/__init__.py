"""Modules UI V5.5 - Interface moderne type FinCouple.

Nouvelle interface light mode avec design épuré.

Usage:
    from modules.ui.v5_5 import ThemeV5, apply_light_theme
    from modules.ui.v5_5.components import WelcomeCard, KPICard
    from modules.ui.v5_5.welcome import render_welcome_screen
    from modules.ui.v5_5.dashboard import render_dashboard_v5
    
    # Appliquer le thème
    apply_light_theme()
    
    # Afficher welcome ou dashboard
    render_welcome_screen()
    # ou
    render_dashboard_v5()
"""

from .theme import (
    LightColors,
    ThemeV5,
    apply_light_theme,
    get_light_theme_css,
)

# Composants
from .components import (
    WelcomeCard,
    KPICard,
    KPIData,
    format_currency,
    DashboardHeader,
    get_current_month_name,
    get_last_12_months,
    charts,
    filters,
    transactions,
    SavingsGoalsWidget,
    render_mini_savings_summary,
)

# Welcome screen
from .welcome import (
    render_welcome_screen,
    render_welcome_or_dashboard,
    has_transactions,
    get_user_name,
)

# Dashboard
from .dashboard import (
    render_dashboard_v5,
    render_kpi_grid,
    calculate_kpis,
    render_dashboard_empty,
)

# Pages (controllers)
try:
    from .pages import DashboardController
    _PAGES_AVAILABLE = True
except ImportError:
    _PAGES_AVAILABLE = False

__all__ = [
    # Theme
    "LightColors",
    "ThemeV5",
    "apply_light_theme",
    "get_light_theme_css",
    # Components
    "WelcomeCard",
    "KPICard",
    "KPIData",
    "format_currency",
    "DashboardHeader",
    "get_current_month_name",
    "get_last_12_months",
    # Welcome
    "render_welcome_screen",
    "render_welcome_or_dashboard",
    "has_transactions",
    "get_user_name",
    # Dashboard
    "render_dashboard_v5",
    "render_kpi_grid",
    "calculate_kpis",
    "render_dashboard_empty",
    # Pages
    "DashboardController",
]
