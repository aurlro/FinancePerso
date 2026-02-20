"""
FinancePerso Core Modules.
"""

# Import cache_manager to register event handlers for cache invalidation
# This ensures cache is properly cleared when data changes via EventBus
from modules import cache_manager

__all__ = ["cache_manager"]
