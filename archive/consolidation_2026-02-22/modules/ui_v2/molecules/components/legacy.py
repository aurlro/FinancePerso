"""
Legacy Wrapper - Backward compatibility for old component imports.

This module provides backward compatibility for code still importing from
the old modules/ui/components/ location. All exports redirect to the new
ui_v2 Atomic Design structure.

Migration Path:
    OLD: from modules.ui.components.confirm_dialog import confirm_dialog
    NEW: from modules.ui_v2.molecules.components import confirm_dialog

Note: This file will be deprecated in a future release.
"""

# =============================================================================
# Re-exports from new Atomic Design structure
# =============================================================================

# Confirm Dialog
from modules.ui_v2.molecules.components.confirm_dialog import (
    confirm_delete as _confirm_delete,
    confirm_dialog as _confirm_dialog,
    reset_confirmation as _reset_confirmation,
    trigger_confirmation as _trigger_confirmation,
    with_confirmation as _with_confirmation,
)

# Empty States
from modules.ui_v2.molecules.components.empty_states import (
    render_empty_state as _render_empty_state,
    render_error_state as _render_error_state,
    render_loading_state as _render_loading_state,
    render_no_budgets_state as _render_no_budgets_state,
    render_no_categories_state as _render_no_categories_state,
    render_no_data_state as _render_no_data_state,
    render_no_rules_state as _render_no_rules_state,
    render_no_search_results as _render_no_search_results,
    render_no_transactions_state as _render_no_transactions_state,
)

# Loading States
from modules.ui_v2.molecules.components.loading_states import (
    clear_operation_progress as _clear_operation_progress,
    loading_spinner as _loading_spinner,
    render_operation_progress as _render_operation_progress,
    render_progress_steps as _render_progress_steps,
    render_skeleton_card as _render_skeleton_card,
    render_skeleton_kpi_cards as _render_skeleton_kpi_cards,
    render_skeleton_table as _render_skeleton_table,
    render_skeleton_text as _render_skeleton_text,
)

# Quick Actions
from modules.ui_v2.molecules.components.quick_actions import (
    render_quick_actions_grid as _render_quick_actions_grid,
    render_quick_config_popover as _render_quick_config_popover,
    render_quick_import_popover as _render_quick_import_popover,
    render_quick_stats_popover as _render_quick_stats_popover,
    render_quick_validation_popover as _render_quick_validation_popover,
)

# Smart Actions
from modules.ui_v2.molecules.components.smart_actions import (
    get_primary_action as _get_primary_action,
    get_secondary_actions as _get_secondary_actions,
    get_user_progress_state as _get_user_progress_state,
    render_compact_tip as _render_compact_tip,
    render_smart_actions as _render_smart_actions,
)

# Selectors (combined chip + member)
from modules.ui_v2.molecules.components.selectors import (
    render_chip_selector as _render_chip_selector,
    render_member_selector as _render_member_selector,
    render_member_selector_pair as _render_member_selector_pair,
)

# Tags
from modules.ui_v2.molecules.components.tags.tag_manager import (
    batch_apply_tags_to_similar as _batch_apply_tags_to_similar,
    find_similar_transactions as _find_similar_transactions,
    get_tag_color as _get_tag_color,
    render_pill_tags as _render_pill_tags,
    render_smart_tag_selector as _render_smart_tag_selector_from_manager,
)
from modules.ui_v2.molecules.components.tags.tag_selector_compact import (
    render_cheque_nature_field as _render_cheque_nature_field,
    render_tag_selector_compact as _render_tag_selector_compact,
)
from modules.ui_v2.molecules.components.tags.tag_selector_smart import (
    apply_tag_to_similar as _apply_tag_to_similar,
    render_smart_tag_selector as _render_smart_tag_selector,
    render_tag_propagation_dialog as _render_tag_propagation_dialog,
)

# Transactions
from modules.ui_v2.molecules.components.transactions.drill_down import (
    render_category_drill_down_expander as _render_category_drill_down_expander,
    render_transaction_drill_down as _render_transaction_drill_down,
)
from modules.ui_v2.molecules.components.transactions.diagnostic import (
    find_inconsistent_transactions as _find_inconsistent_transactions,
    fix_transaction_amount as _fix_transaction_amount,
    render_compact_diagnostic_card as _render_compact_diagnostic_card,
    render_diagnostic_summary as _render_diagnostic_summary,
    render_transaction_diagnostic_page as _render_transaction_diagnostic_page,
)

# Widgets
from modules.ui_v2.molecules.components.widgets.savings_goals import (
    get_goal_insight_for_daily_widget as _get_goal_insight_for_daily_widget,
    render_goal_creation_form as _render_goal_creation_form,
    render_savings_goal_card as _render_savings_goal_card,
    render_savings_goals_page as _render_savings_goals_page,
    render_savings_goals_summary as _render_savings_goals_summary,
)
from modules.ui_v2.molecules.components.widgets.smart_reminders import (
    get_reminder_insight_for_daily_widget as _get_reminder_insight_for_daily_widget,
    has_urgent_reminders as _has_urgent_reminders,
    render_compact_reminder as _render_compact_reminder,
    render_reminder_card as _render_reminder_card,
    render_reminders_in_sidebar as _render_reminders_in_sidebar,
    render_smart_reminders_widget as _render_smart_reminders_widget,
)
from modules.ui_v2.molecules.components.widgets.daily_widget import (
    get_spending_insight as _get_spending_insight,
    render_daily_widget as _render_daily_widget,
    render_quick_stats_row as _render_quick_stats_row,
)
from modules.ui_v2.molecules.components.widgets.progress_tracker import (
    clear_operation_progress as _clear_progress_progress,  # Different from loading_states
    render_progress_tracker as _render_progress_tracker,
    reset_progress_tracker as _reset_progress_tracker,
)

# Forms
from modules.ui_v2.molecules.components.forms.profile_form import (
    render_profile_setup_form as _render_profile_setup_form,
)
from modules.ui_v2.molecules.components.forms.avatar_selector import (
    render_avatar_selector as _render_avatar_selector,
)

# Onboarding
from modules.ui_v2.molecules.components.onboarding_modal import (
    dismiss_onboarding as _dismiss_onboarding,
    render_floating_help_button as _render_floating_help_button,
    render_onboarding_modal as _render_onboarding_modal,
    should_show_onboarding as _should_show_onboarding,
)

# =============================================================================
# Public API - Same signatures as original modules/ui/components/
# =============================================================================

# Confirm Dialog
confirm_dialog = _confirm_dialog
trigger_confirmation = _trigger_confirmation
reset_confirmation = _reset_confirmation
with_confirmation = _with_confirmation
confirm_delete = _confirm_delete

# Empty States
render_empty_state = _render_empty_state
render_no_transactions_state = _render_no_transactions_state
render_no_budgets_state = _render_no_budgets_state
render_no_rules_state = _render_no_rules_state
render_no_categories_state = _render_no_categories_state
render_no_search_results = _render_no_search_results
render_no_data_state = _render_no_data_state
render_error_state = _render_error_state
render_loading_state = _render_loading_state

# Loading States
render_skeleton_card = _render_skeleton_card
render_skeleton_text = _render_skeleton_text
render_skeleton_kpi_cards = _render_skeleton_kpi_cards
render_skeleton_table = _render_skeleton_table
loading_spinner = _loading_spinner
render_progress_steps = _render_progress_steps
render_operation_progress = _render_operation_progress
clear_operation_progress = _clear_operation_progress

# Quick Actions
render_quick_validation_popover = _render_quick_validation_popover
render_quick_config_popover = _render_quick_config_popover
render_quick_import_popover = _render_quick_import_popover
render_quick_stats_popover = _render_quick_stats_popover
render_quick_actions_grid = _render_quick_actions_grid

# Smart Actions
get_user_progress_state = _get_user_progress_state
get_primary_action = _get_primary_action
get_secondary_actions = _get_secondary_actions
render_smart_actions = _render_smart_actions
render_compact_tip = _render_compact_tip

# Selectors
render_chip_selector = _render_chip_selector
render_member_selector = _render_member_selector
render_member_selector_pair = _render_member_selector_pair

# Tags
get_tag_color = _get_tag_color
render_pill_tags = _render_pill_tags
find_similar_transactions = _find_similar_transactions
render_smart_tag_selector = _render_smart_tag_selector
batch_apply_tags_to_similar = _batch_apply_tags_to_similar
render_tag_selector_compact = _render_tag_selector_compact
render_cheque_nature_field = _render_cheque_nature_field
render_tag_propagation_dialog = _render_tag_propagation_dialog
apply_tag_to_similar = _apply_tag_to_similar

# Transactions
render_transaction_drill_down = _render_transaction_drill_down
render_category_drill_down_expander = _render_category_drill_down_expander
find_inconsistent_transactions = _find_inconsistent_transactions
fix_transaction_amount = _fix_transaction_amount
render_diagnostic_summary = _render_diagnostic_summary
render_transaction_diagnostic_page = _render_transaction_diagnostic_page
render_compact_diagnostic_card = _render_compact_diagnostic_card

# Widgets
render_savings_goal_card = _render_savings_goal_card
render_savings_goals_summary = _render_savings_goals_summary
render_goal_creation_form = _render_goal_creation_form
render_savings_goals_page = _render_savings_goals_page
get_goal_insight_for_daily_widget = _get_goal_insight_for_daily_widget
render_smart_reminders_widget = _render_smart_reminders_widget
render_reminder_card = _render_reminder_card
render_compact_reminder = _render_compact_reminder
render_reminders_in_sidebar = _render_reminders_in_sidebar
has_urgent_reminders = _has_urgent_reminders
get_reminder_insight_for_daily_widget = _get_reminder_insight_for_daily_widget
render_daily_widget = _render_daily_widget
get_spending_insight = _get_spending_insight
render_quick_stats_row = _render_quick_stats_row
render_progress_tracker = _render_progress_tracker
reset_progress_tracker = _reset_progress_tracker

# Forms
render_profile_setup_form = _render_profile_setup_form
render_avatar_selector = _render_avatar_selector

# Onboarding
should_show_onboarding = _should_show_onboarding
dismiss_onboarding = _dismiss_onboarding
render_onboarding_modal = _render_onboarding_modal
render_floating_help_button = _render_floating_help_button

# =============================================================================
# Legacy module exports
# =============================================================================

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
    "get_tag_color",
    "render_pill_tags",
    "find_similar_transactions",
    "render_smart_tag_selector",
    "batch_apply_tags_to_similar",
    "render_tag_selector_compact",
    "render_cheque_nature_field",
    "render_tag_propagation_dialog",
    "apply_tag_to_similar",
    # Transactions
    "render_transaction_drill_down",
    "render_category_drill_down_expander",
    "find_inconsistent_transactions",
    "fix_transaction_amount",
    "render_diagnostic_summary",
    "render_transaction_diagnostic_page",
    "render_compact_diagnostic_card",
    # Widgets
    "render_savings_goal_card",
    "render_savings_goals_summary",
    "render_goal_creation_form",
    "render_savings_goals_page",
    "get_goal_insight_for_daily_widget",
    "render_smart_reminders_widget",
    "render_reminder_card",
    "render_compact_reminder",
    "render_reminders_in_sidebar",
    "has_urgent_reminders",
    "get_reminder_insight_for_daily_widget",
    "render_daily_widget",
    "get_spending_insight",
    "render_quick_stats_row",
    "render_progress_tracker",
    "reset_progress_tracker",
    # Forms
    "render_profile_setup_form",
    "render_avatar_selector",
    # Onboarding
    "should_show_onboarding",
    "dismiss_onboarding",
    "render_onboarding_modal",
    "render_floating_help_button",
]
