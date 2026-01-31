"""
Tests for multi-tier cache module.
"""

import pytest
import time
from unittest.mock import Mock, call

from modules.cache_multitier import (
    MemoryCache,
    DiskCache,
    MultiTierCache,
    cached,
    get_cache,
)


class TestMemoryCache:
    """Test MemoryCache class."""
    
    def test_basic_get_set(self):
        """Test basic get and set operations."""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_missing_key(self):
        """Test getting missing key."""
        cache = MemoryCache()
        
        result = cache.get("missing")
        assert result is None
    
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = MemoryCache(default_ttl=1)  # 1 second TTL
        
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get("key1") is None
    
    def test_delete(self):
        """Test delete operation."""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        cache.delete("key1")
        
        assert cache.get("key1") is None
    
    def test_clear(self):
        """Test clear operation."""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert len(cache._cache) == 0
    
    def test_max_size_eviction(self):
        """Test LRU eviction when max size reached."""
        cache = MemoryCache(max_size=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_access_updates_lru(self):
        """Test that access updates LRU order."""
        cache = MemoryCache(max_size=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Access key1 to make it more recent
        cache.get("key1")
        
        # Add key3 - should evict key2 (least recently used)
        cache.set("key3", "value3")
        
        assert cache.get("key1") == "value1"  # Still there
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
    
    def test_stats(self):
        """Test cache statistics."""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key1")  # Hit
        cache.get("missing")  # Miss
        
        stats = cache.get_stats()
        
        assert stats['size'] == 1
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_rate'] == "66.7%"


class TestMultiTierCache:
    """Test MultiTierCache class."""
    
    def test_get_with_fetch_func(self):
        """Test get with fetch function."""
        cache = MultiTierCache()
        mock_fetch = Mock(return_value="fetched_value")
        
        # First call should fetch
        result = cache.get("key1", fetch_func=mock_fetch)
        assert result == "fetched_value"
        assert mock_fetch.called
        
        # Second call should get from cache
        mock_fetch.reset_mock()
        result = cache.get("key1", fetch_func=mock_fetch)
        assert result == "fetched_value"
        assert not mock_fetch.called
    
    def test_set_and_get(self):
        """Test set and get operations."""
        cache = MultiTierCache()
        
        cache.set("key1", "value1")
        
        # Should get from memory
        assert cache.get("key1") == "value1"
    
    def test_delete(self):
        """Test delete from both tiers."""
        cache = MultiTierCache()
        
        cache.set("key1", "value1")
        cache.delete("key1")
        
        assert cache.get("key1") is None
    
    def test_clear(self):
        """Test clear both tiers."""
        cache = MultiTierCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_disable_enable(self):
        """Test disable and enable caching."""
        cache = MultiTierCache()
        
        cache.disable()
        cache.set("key1", "value1")
        
        # Should not cache when disabled
        assert cache.get("key1") is None
        
        cache.enable()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"


class TestCachedDecorator:
    """Test cached decorator."""
    
    def test_caches_result(self):
        """Test that decorator caches function results."""
        mock_func = Mock(return_value="result")
        
        @cached(ttl_memory=60)
        def test_func(arg):
            return mock_func(arg)
        
        # First call
        result1 = test_func("arg1")
        assert result1 == "result"
        assert mock_func.call_count == 1
        
        # Second call with same arg - should use cache
        result2 = test_func("arg1")
        assert result2 == "result"
        assert mock_func.call_count == 1  # Not called again
        
        # Call with different arg
        result3 = test_func("arg2")
        assert mock_func.call_count == 2
    
    def test_custom_key_func(self):
        """Test custom key function."""
        mock_func = Mock(return_value="result")
        key_func = Mock(return_value="custom_key")
        
        @cached(key_func=key_func)
        def test_func(arg1, arg2):
            return mock_func(arg1, arg2)
        
        test_func("a", "b")
        
        # Key function should be called
        key_func.assert_called_once_with("a", "b")


class TestSingleton:
    """Test singleton pattern."""
    
    def test_get_cache_returns_same_instance(self):
        """Test that get_cache returns singleton."""
        cache1 = get_cache()
        cache2 = get_cache()
        
        assert cache1 is cache2
    
    def test_cache_isolation(self):
        """Test that singleton cache works correctly."""
        cache = get_cache()
        cache.set("test_key", "test_value")
        
        cache2 = get_cache()
        assert cache2.get("test_key") == "test_value"
        
        # Cleanup
        cache.clear()


class TestEdgeCases:
    """Test edge cases."""
    
    def test_none_values(self):
        """Test handling of None values."""
        cache = MemoryCache()
        
        cache.set("key1", None)
        assert cache.get("key1") is None
    
    def test_complex_objects(self):
        """Test caching complex objects."""
        cache = MemoryCache()
        
        data = {"nested": {"key": "value"}, "list": [1, 2, 3]}
        cache.set("key1", data)
        
        result = cache.get("key1")
        assert result == data
    
    def test_large_values(self):
        """Test caching large values."""
        cache = MemoryCache()
        
        large_data = "x" * 1000000  # 1MB string
        cache.set("key1", large_data)
        
        result = cache.get("key1")
        assert result == large_data
