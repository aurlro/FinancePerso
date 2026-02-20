"""
Database layer package.
Provides modular access to all database operations.
"""

# Import cache_manager to register event handlers for cache invalidation
# This ensures cache is properly cleared when data changes via EventBus
from modules import cache_manager

# This __init__.py allows importing from modules.db
# Example: from modules.db.transactions import get_pending_transactions
