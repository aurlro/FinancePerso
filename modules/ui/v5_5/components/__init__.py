"""Composants V5.5 - Éléments spécifiques aux maquettes.

Usage:
    from modules.ui.v5_5.components import WelcomeCard, KPICard
    
    WelcomeCard.render(on_primary=handler)
"""

from .welcome_card import WelcomeCard
from .kpi_card import KPICard, KPIData, format_currency, create_kpi_variation
from .dashboard_header import DashboardHeader, get_current_month_name, get_last_12_months

# Sous-modules
from . import charts
from . import filters
from . import transactions

# Composants optionnels
try:
    from .savings_goals import SavingsGoalsWidget, render_mini_savings_summary
    _SAVINGS_AVAILABLE = True
except ImportError:
    _SAVINGS_AVAILABLE = False

__all__ = [
    "WelcomeCard",
    "KPICard",
    "KPIData",
    "format_currency",
    "create_kpi_variation",
    "DashboardHeader",
    "get_current_month_name",
    "get_last_12_months",
    # Sous-modules
    "charts",
    "filters",
    "transactions",
    "SavingsGoalsWidget",
    "render_mini_savings_summary",
]
