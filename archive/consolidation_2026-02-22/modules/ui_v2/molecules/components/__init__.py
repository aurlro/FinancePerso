"""
Components - Reusable UI molecules for FinancePerso.

This module contains composite UI components that combine atoms
to create reusable interface elements.

Migration Status:
- confirm_dialog.py: Migrated from organisms (reclassified as molecule)
- empty_states.py: Migrated from ui/components
- loading_states.py: Migrated from ui/components
- quick_actions.py: Migrated from ui/components
- smart_actions.py: Migrated from ui/components
- selectors.py: Combined chip_selector + member_selector
- tags/: Tag-related components (tag_manager, tag_selector_compact, tag_selector_smart)
- transactions/: Transaction components (drill_down, diagnostic)
- widgets/: Small widgets (savings_goals, smart_reminders, daily_widget, progress_tracker)
- forms/: Form components (profile_form, avatar_selector)
- legacy.py: Backward compatibility wrapper
"""

# Direct exports from this module
from modules.ui_v2.molecules.components.confirm_dialog import (
    confirm_delete,
    confirm_dialog,
    reset_confirmation,
    trigger_confirmation,
    with_confirmation,
)
from modules.ui_v2.molecules.components.empty_states import (
    render_empty_state,
    render_error_state,
    render_loading_state,
    render_no_budgets_state,
    render_no_categories_state,
    render_no_data_state,
    render_no_rules_state,
    render_no_search_results,
    render_no_transactions_state,
)
from modules.ui_v2.molecules.components.loading_states import (
    clear_operation_progress,
    loading_spinner,
    render_operation_progress,
    render_progress_steps,
    render_skeleton_card,
    render_skeleton_kpi_cards,
    render_skeleton_table,
    render_skeleton_text,
)
from modules.ui_v2.molecules.components.quick_actions import (
    render_quick_actions_grid,
    render_quick_config_popover,
    render_quick_import_popover,
    render_quick_stats_popover,
    render_quick_validation_popover,
)
from modules.ui_v2.molecules.components.selectors import (
    render_chip_selector,
    render_member_selector,
    render_member_selector_pair,
)
from modules.ui_v2.molecules.components.smart_actions import (
    get_primary_action,
    get_secondary_actions,
    get_user_progress_state,
    render_compact_tip,
    render_smart_actions,
)

# Tag components
from modules.ui_v2.molecules.components.tags import (
    render_smart_tag_selector,
    render_tag_selector_compact,
)

# Transaction components
from modules.ui_v2.molecules.components.transactions import (
    render_transaction_diagnostic_page,
    render_transaction_drill_down,
)

# Widget components
from modules.ui_v2.molecules.components.widgets import (
    render_daily_widget,
    render_progress_tracker,
    render_quick_stats_row,
    render_savings_goal_card,
    render_savings_goals_page,
    render_savings_goals_summary,
    render_smart_reminders_widget,
)

# Form components
from modules.ui_v2.molecules.components.forms import (
    render_avatar_selector,
    render_profile_setup_form,
)

# Onboarding
from modules.ui_v2.molecules.components.onboarding_modal import (
    dismiss_onboarding,
    render_floating_help_button,
    render_onboarding_modal,
    should_show_onboarding,
)

__all__ = [
    # Confirm Dialog
    "confirm_dialog",
    "trigger_confirmation",
    "reset_confirmation",
    "with_confirmation",
    "confirm_delete",
    # Empty States
    "render_empty_state",
    "render_no_transactions_state",
    "render_no_budgets_state",
    "render_no_rules_state",
    "render_no_categories_state",
    "render_no_search_results",
    "render_no_data_state",
    "render_error_state",
    "render_loading_state",
    # Loading States
    "render_skeleton_card",
    "render_skeleton_text",
    "render_skeleton_kpi_cards",
    "render_skeleton_table",
    "loading_spinner",
    "render_progress_steps",
    "render_operation_progress",
    "clear_operation_progress",
    # Quick Actions
    "render_quick_validation_popover",
    "render_quick_config_popover",
    "render_quick_import_popover",
    "render_quick_stats_popover",
    "render_quick_actions_grid",
    # Smart Actions
    "get_user_progress_state",
    "get_primary_action",
    "get_secondary_actions",
    "render_smart_actions",
    "render_compact_tip",
    # Selectors
    "render_chip_selector",
    "render_member_selector",
    "render_member_selector_pair",
    # Tags
    "render_tag_selector_compact",
    "render_smart_tag_selector",
    # Transactions
    "render_transaction_drill_down",
    "render_transaction_diagnostic_page",
    # Widgets
    "render_savings_goal_card",
    "render_savings_goals_summary",
    "render_savings_goals_page",
    "render_smart_reminders_widget",
    "render_daily_widget",
    "render_quick_stats_row",
    "render_progress_tracker",
    # Forms
    "render_profile_setup_form",
    "render_avatar_selector",
    # Onboarding
    "should_show_onboarding",
    "dismiss_onboarding",
    "render_onboarding_modal",
    "render_floating_help_button",
]
