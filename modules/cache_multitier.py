"""
Multi-tier caching system for FinancePerso.
Provides memory (LRU) and disk caching for optimal performance.
"""

import os
import time
import pickle
import hashlib
from typing import Any, Optional, Callable, Dict
from functools import wraps
from pathlib import Path

try:
    import diskcache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

from modules.logger import logger


class CacheEntry:
    """Represents a cached value with metadata."""
    
    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = time.time()
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Update access metadata."""
        self.access_count += 1
        self.last_accessed = time.time()


class MemoryCache:
    """In-memory LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time-to-live in seconds
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self._cache.get(key)
        
        if entry is None:
            self._misses += 1
            return None
        
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None
        
        entry.touch()
        self._hits += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        # Evict oldest entries if cache is full
        if len(self._cache) >= self._max_size:
            self._evict_oldest()
        
        ttl = ttl or self._default_ttl
        self._cache[key] = CacheEntry(value, ttl)
    
    def delete(self, key: str):
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """Clear all entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def _evict_oldest(self):
        """Evict oldest accessed entry."""
        if not self._cache:
            return
        
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        del self._cache[oldest_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'entries': list(self._cache.keys())
        }


class DiskCache:
    """Disk-based persistent cache."""
    
    def __init__(self, cache_dir: str = "Data/cache", default_ttl: int = 3600):
        """
        Initialize disk cache.
        
        Args:
            cache_dir: Directory for cache files
            default_ttl: Default time-to-live in seconds
        """
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        
        if DISKCACHE_AVAILABLE:
            self._cache = diskcache.Cache(cache_dir)
            logger.info(f"Disk cache initialized at {cache_dir}")
        else:
            self._cache = None
            logger.warning("diskcache not installed, disk caching disabled")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        if self._cache is None:
            self._misses += 1
            return None
        
        try:
            value = self._cache.get(key)
            if value is not None:
                self._hits += 1
                return value
        except Exception as e:
            logger.warning(f"Disk cache get error: {e}")
        
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in disk cache."""
        if self._cache is None:
            return
        
        try:
            ttl = ttl or self._default_ttl
            self._cache.set(key, value, expire=ttl)
        except Exception as e:
            logger.warning(f"Disk cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from disk cache."""
        if self._cache is not None:
            try:
                del self._cache[key]
            except Exception:
                pass
    
    def clear(self):
        """Clear all entries."""
        if self._cache is not None:
            self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            'enabled': self._cache is not None,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }


class MultiTierCache:
    """
    Multi-tier caching combining memory and disk cache.
    
    Strategy:
    1. Check memory cache (fastest)
    2. Check disk cache (persistent)
    3. Execute fetch function
    4. Store in both caches
    """
    
    def __init__(self):
        self.memory = MemoryCache(max_size=1000, default_ttl=300)
        self.disk = DiskCache(default_ttl=3600)
        self._enabled = True
    
    def get(self, key: str, fetch_func: Optional[Callable] = None, 
            ttl_memory: int = 300, ttl_disk: int = 3600) -> Any:
        """
        Get value from cache or fetch it.
        
        Args:
            key: Cache key
            fetch_func: Function to call if value not in cache
            ttl_memory: TTL for memory cache
            ttl_disk: TTL for disk cache
            
        Returns:
            Cached or fetched value
            
        Example:
            >>> cache = MultiTierCache()
            >>> value = cache.get('categories', lambda: get_categories_from_db())
        """
        if not self._enabled:
            return fetch_func() if fetch_func else None
        
        # Try memory cache
        value = self.memory.get(key)
        if value is not None:
            return value
        
        # Try disk cache
        value = self.disk.get(key)
        if value is not None:
            # Promote to memory cache
            self.memory.set(key, value, ttl_memory)
            return value
        
        # Fetch if function provided
        if fetch_func:
            value = fetch_func()
            if value is not None:
                self.set(key, value, ttl_memory, ttl_disk)
            return value
        
        return None
    
    def set(self, key: str, value: Any, ttl_memory: int = 300, ttl_disk: int = 3600):
        """Set value in both caches."""
        if not self._enabled:
            return
        
        self.memory.set(key, value, ttl_memory)
        self.disk.set(key, value, ttl_disk)
    
    def delete(self, key: str):
        """Delete from both caches."""
        self.memory.delete(key)
        self.disk.delete(key)
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        # Invalidate from memory
        memory_keys = list(self.memory._cache.keys())
        for key in memory_keys:
            if pattern in key:
                self.memory.delete(key)
        
        # Note: Disk cache doesn't support pattern deletion efficiently
        # Would need to iterate all keys
    
    def clear(self):
        """Clear all caches."""
        self.memory.clear()
        self.disk.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get combined cache statistics."""
        return {
            'memory': self.memory.get_stats(),
            'disk': self.disk.get_stats(),
            'enabled': self._enabled
        }
    
    def enable(self):
        """Enable caching."""
        self._enabled = True
    
    def disable(self):
        """Disable caching."""
        self._enabled = False


# Singleton instance
_cache_instance = None

def get_cache() -> MultiTierCache:
    """Get singleton cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MultiTierCache()
    return _cache_instance


def cached(ttl_memory: int = 300, ttl_disk: int = 3600, key_func: Optional[Callable] = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl_memory: Memory cache TTL
        ttl_disk: Disk cache TTL
        key_func: Optional function to generate cache key from arguments
        
    Example:
        >>> @cached(ttl_memory=600)
        ... def get_categories():
        ...     return db.query("SELECT * FROM categories")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: function name + arguments hash
                key_parts = [func.__name__]
                key_parts.extend([str(arg) for arg in args])
                key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
                cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_memory, ttl_disk)
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str = ""):
    """Invalidate cache entries matching pattern."""
    cache = get_cache()
    if pattern:
        cache.invalidate_pattern(pattern)
    else:
        cache.clear()


__all__ = [
    'MemoryCache',
    'DiskCache',
    'MultiTierCache',
    'get_cache',
    'cached',
    'invalidate_cache',
]
