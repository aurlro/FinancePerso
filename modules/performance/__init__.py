"""
Performance Module - Optimisations et Cache
============================================

Ce module contient les outils d'optimisation des performances.

Usage:
    from modules.performance import AdvancedCache, cache_monte_carlo

    @cache_monte_carlo(ttl_seconds=600)
    def run_simulation():
        pass
"""

from modules.performance.cache_advanced import (
    AdvancedCache,
    CacheEntry,
    CacheStats,
    cache_monte_carlo,
    cache_transactions,
    cache_wealth_projection,
    invalidate_cache_pattern,
    get_cache_stats,
    clear_all_cache,
    render_cache_stats,
)

__all__ = [
    "AdvancedCache",
    "CacheEntry",
    "CacheStats",
    "cache_monte_carlo",
    "cache_transactions",
    "cache_wealth_projection",
    "invalidate_cache_pattern",
    "get_cache_stats",
    "clear_all_cache",
    "render_cache_stats",
]
