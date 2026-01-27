"""
Database Manager - DEPRECATED MODULE (Backward Compatibility Layer)

⚠️  MIGRATION NOTICE ⚠️
This module has been refactored into specialized modules in modules/db/
Please update your imports to use the new modular structure:

OLD: from modules.data_manager import get_transactions
NEW: from modules.db.transactions import get_all_transactions

This file now re-exports all functions for backward compatibility.
It will be removed in a future version once all imports are updated.

NEW MODULE STRUCTURE:
- modules.db.connection  - Database connections
- modules.db.transactions - Transaction CRUD operations
- modules.db.categories  - Category management
- modules.db.members     - Member management + mappings
- modules.db.rules       - Learning rules
- modules.db.budgets     - Budget management
- modules.db.tags        - Tag operations
- modules.db.stats       - Statistics and global queries
- modules.db.migrations  - Schema initialization
- modules.db.audit       - Data quality checks
"""

# Re-export everything for backward compatibility
from modules.db.connection import get_db_connection, DB_PATH, PROJECT_ROOT

# Migrations
from modules.db.migrations import init_db

# Budgets
from modules.db.budgets import set_budget, get_budgets

# Members
from modules.db.members import (
    add_member,
    update_member_type,
    delete_member,
    get_members,
    rename_member,
    get_orphan_labels,
    delete_and_replace_label,
    add_member_mapping,
    get_member_mappings,
    delete_member_mapping,
    get_member_mappings_df,
    get_unique_members,
    update_transaction_member,
)

# Audit
from modules.db.audit import (
    auto_fix_common_inconsistencies,
    get_suggested_mappings,
    get_transfer_inconsistencies,
)

# Tags
from modules.db.tags import (
    get_all_tags,
    remove_tag_from_all_transactions,
    learn_tags_from_history,
)

# Learning Rules
from modules.db.rules import (
    add_learning_rule,
    get_learning_rules,
    delete_learning_rule,
)

# Categories
from modules.db.categories import (
    add_category,
    update_category_emoji,
    update_category_fixed,
    update_category_suggested_tags,
    delete_category,
    get_categories,
    get_categories_with_emojis,
    get_categories_suggested_tags,
    get_categories_df,
    get_all_categories_including_ghosts,
    add_tag_to_category,
    merge_categories,
)

# Transactions
from modules.db.transactions import (
    transaction_exists,
    save_transactions,
    apply_member_mappings_to_pending,
    get_transaction_count,
    get_duplicates_report,
    get_transactions_by_criteria,
    delete_transaction_by_id,
    get_pending_transactions,
    get_all_hashes,
    get_all_transactions,
    update_transaction_category,
    bulk_update_transaction_status,
    undo_last_action,
    mark_transaction_as_ungrouped,
    delete_transaction,
    delete_transactions_by_period,
)

# Stats
from modules.db.stats import (
    is_app_initialized,
    get_global_stats,
    get_available_months,
    get_all_account_labels,
    get_recent_imports,
)


# Show deprecation warning on import
import warnings
warnings.warn(
    "modules.data_manager is deprecated. Please update imports to use modules.db.*",
    DeprecationWarning,
    stacklevel=2
)
