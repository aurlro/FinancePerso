"""Composants V5.5 - Éléments spécifiques aux maquettes.

Usage:
    from modules.ui.v5_5.components import WelcomeCard, KPICard
    
    WelcomeCard.render(on_primary=handler)
"""

from .welcome_card import WelcomeCard
from .kpi_card import KPICard, KPIData, format_currency, create_kpi_variation
from .dashboard_header import DashboardHeader, get_current_month_name, get_last_12_months

__all__ = [
    "WelcomeCard",
    "KPICard",
    "KPIData",
    "format_currency",
    "create_kpi_variation",
    "DashboardHeader",
    "get_current_month_name",
    "get_last_12_months",
]
