"""
Dashboard Widgets - Atomic Design widgets for the dashboard.

These widgets are molecules/organisms that compose the dashboard.
They receive DataFrames as parameters and use st.metric, st.plotly_chart, etc.

Usage:
    from modules.ui_v2.widgets.dashboard import (
        render_kpi_cards,
        render_category_bar_chart,
        render_evolution_chart,
        render_budget_tracker,
        render_top_expenses,
        render_smart_recommendations_section,
        render_ai_financial_report,
        render_month_end_forecast,
        render_filter_sidebar,
    )
"""

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
    get_filter_options,
    normalize_name,
    consolidate_names,
    render_filter_sidebar,
    render_filter_info,
)
from modules.ui_v2.widgets.dashboard.kpi_cards import (
    calculate_trends,
    compute_previous_period as compute_previous_period_kpi,
    render_kpi_cards,
)
from modules.ui_v2.widgets.dashboard.smart_recommendations import (
    render_smart_recommendations_section,
    render_quick_actions_banner,
)
from modules.ui_v2.widgets.dashboard.top_expenses import render_top_expenses

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
