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

# Migrations

# Budgets

# Members

# Audit

# Tags

# Learning Rules

# Categories

# Transactions

# Stats


# Show deprecation warning on import
import warnings

warnings.warn(
    "modules.data_manager is deprecated. Please update imports to use modules.db.*",
    DeprecationWarning,
    stacklevel=2,
)
