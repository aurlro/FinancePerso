"""
Widgets Components - Small reusable widget molecules.

Migrated from:
- modules/ui/components/savings_goals_widget.py
- modules/ui/components/smart_reminders_widget.py
- modules/ui/components/daily_widget.py
- modules/ui/components/progress_tracker.py

Classification: Molecules (small self-contained widgets)
"""

from modules.ui_v2.molecules.components.widgets.savings_goals import (
    get_goal_insight_for_daily_widget,
    render_goal_creation_form,
    render_savings_goal_card,
    render_savings_goals_page,
    render_savings_goals_summary,
)
from modules.ui_v2.molecules.components.widgets.smart_reminders import (
    get_reminder_insight_for_daily_widget,
    has_urgent_reminders,
    render_compact_reminder,
    render_reminder_card,
    render_reminders_in_sidebar,
    render_smart_reminders_widget,
)
from modules.ui_v2.molecules.components.widgets.daily_widget import (
    get_spending_insight,
    render_daily_widget,
    render_quick_stats_row,
)
from modules.ui_v2.molecules.components.widgets.progress_tracker import (
    clear_operation_progress,
    render_progress_tracker,
    reset_progress_tracker,
)

__all__ = [
    # Savings Goals
    "render_savings_goal_card",
    "render_savings_goals_summary",
    "render_goal_creation_form",
    "render_savings_goals_page",
    "get_goal_insight_for_daily_widget",
    # Smart Reminders
    "render_smart_reminders_widget",
    "render_reminder_card",
    "render_compact_reminder",
    "render_reminders_in_sidebar",
    "has_urgent_reminders",
    "get_reminder_insight_for_daily_widget",
    # Daily Widget
    "render_daily_widget",
    "get_spending_insight",
    "render_quick_stats_row",
    # Progress Tracker
    "render_progress_tracker",
    "reset_progress_tracker",
    "clear_operation_progress",
]
