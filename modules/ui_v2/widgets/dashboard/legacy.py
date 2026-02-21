"""
Legacy Wrapper for Dashboard Widgets

This module provides backward compatibility for code importing from
`modules.ui.dashboard.*`. It re-exports all functions from the new
`modules.ui_v2.widgets.dashboard` location.

Note:
    This file is kept for backward compatibility. New code should import
    directly from `modules.ui_v2.widgets.dashboard`.

Deprecated:
    The `modules.ui.dashboard` package is deprecated. Please update imports:
    
    Old: from modules.ui.dashboard.kpi_cards import render_kpi_cards
    New: from modules.ui_v2.widgets.dashboard import render_kpi_cards
"""

import warnings

# Re-export all widgets from the new location
from modules.ui_v2.widgets.dashboard.ai_insights import (
    render_ai_financial_report,
    render_month_end_forecast,
)
from modules.ui_v2.widgets.dashboard.budget_tracker import render_budget_tracker
from modules.ui_v2.widgets.dashboard.category_charts import (
    prepare_expense_dataframe,
    render_category_bar_chart,
    render_category_pie_chart,
    render_monthly_stacked_chart,
)
from modules.ui_v2.widgets.dashboard.evolution_chart import (
    render_evolution_chart,
    render_savings_trend_chart,
)
from modules.ui_v2.widgets.dashboard.filters import (
    compute_previous_period,
    consolidate_names,
    get_filter_options,
    normalize_name,
    render_filter_info,
    render_filter_sidebar,
)
from modules.ui_v2.widgets.dashboard.kpi_cards import (
    calculate_trends,
    compute_previous_period as compute_previous_period_kpi,
    render_kpi_cards,
)
from modules.ui_v2.widgets.dashboard.smart_recommendations import (
    get_smart_recommendations,
    render_quick_actions_banner,
    render_smart_recommendations_section,
)
from modules.ui_v2.widgets.dashboard.top_expenses import render_top_expenses

# Emit deprecation warning when this module is imported
warnings.warn(
    "modules.ui.dashboard is deprecated. "
    "Use modules.ui_v2.widgets.dashboard instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    # KPI Cards
    "calculate_trends",
    "render_kpi_cards",
    "compute_previous_period_kpi",
    # Category Charts
    "prepare_expense_dataframe",
    "render_category_bar_chart",
    "render_category_pie_chart",
    "render_monthly_stacked_chart",
    # Evolution Chart
    "render_evolution_chart",
    "render_savings_trend_chart",
    # Budget Tracker
    "render_budget_tracker",
    # Top Expenses
    "render_top_expenses",
    # Smart Recommendations
    "render_smart_recommendations_section",
    "render_quick_actions_banner",
    "get_smart_recommendations",
    # AI Insights
    "render_ai_financial_report",
    "render_month_end_forecast",
    # Filters
    "get_filter_options",
    "normalize_name",
    "consolidate_names",
    "render_filter_sidebar",
    "render_filter_info",
    "compute_previous_period",
]
