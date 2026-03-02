"""
Test Unit: Cache Advanced (Phase 6)
====================================
"""

import time
import pytest
from modules.performance import AdvancedCache


class TestCache:
    """Tests du cache avancé"""

    def test_cache_basic(self):
        """Test: Stockage et récupération"""
        cache = AdvancedCache()

        cache.set("key", {"data": "value"}, ttl_seconds=60)
        result = cache.get("key")

        assert result == {"data": "value"}

    def test_cache_expiration(self):
        """Test: Expiration TTL"""
        cache = AdvancedCache()

        cache.set("key", "value", ttl_seconds=1)
        time.sleep(1.1)

        result = cache.get("key")
        assert result is None

    def test_cache_compression(self):
        """Test: Compression des grosses valeurs"""
        cache = AdvancedCache(compression_threshold=100)

        large_data = "x" * 1000
        cache.set("key", large_data, ttl_seconds=60)
        result = cache.get("key")

        assert result == large_data
