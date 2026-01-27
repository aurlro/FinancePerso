"""
Cache Monitor for Streamlit @st.cache_data functions.
Tracks cache hit rates and provides analytics.
"""
import time
from functools import wraps
from collections import defaultdict
from typing import Callable, Any
import threading


class CacheMonitor:
    """
    Monitor cache performance for Streamlit cached functions.
    Thread-safe cache statistics tracking.
    """
    
    def __init__(self):
        self.stats = defaultdict(lambda: {
            'hits': 0,
            'misses': 0,
            'total_calls': 0,
            'total_compute_time_ms': 0,
            'avg_compute_time_ms': 0,
            'last_reset': time.time()
        })
        self.lock = threading.Lock()
    
    def record_hit(self, func_name: str):
        """Record a cache hit."""
        with self.lock:
            self.stats[func_name]['hits'] += 1
            self.stats[func_name]['total_calls'] += 1
    
    def record_miss(self, func_name: str, compute_time_ms: float):
        """Record a cache miss with computation time."""
        with self.lock:
            s = self.stats[func_name]
            s['misses'] += 1
            s['total_calls'] += 1
            s['total_compute_time_ms'] += compute_time_ms
            
            # Update average
            if s['misses'] > 0:
                s['avg_compute_time_ms'] = s['total_compute_time_ms'] / s['misses']
    
    def get_stats(self, func_name: str = None) -> dict:
        """
        Get cache statistics.
        
        Args:
            func_name: Specific function name, or None for all
            
        Returns:
            Dict of statistics
        """
        with self.lock:
            if func_name:
                return dict(self.stats.get(func_name, {}))
            return {k: dict(v) for k, v in self.stats.items()}
    
    def get_hit_rate(self, func_name: str) -> float:
        """Calculate cache hit rate percentage."""
        with self.lock:
            s = self.stats.get(func_name, {})
            total = s.get('total_calls', 0)
            if total == 0:
                return 0.0
            hits = s.get('hits', 0)
            return (hits / total) * 100
    
    def reset_stats(self, func_name: str = None):
        """Reset statistics for one or all functions."""
        with self.lock:
            if func_name:
                if func_name in self.stats:
                    self.stats[func_name] = {
                        'hits': 0,
                        'misses': 0,
                        'total_calls': 0,
                        'total_compute_time_ms': 0,
                        'avg_compute_time_ms': 0,
                        'last_reset': time.time()
                    }
            else:
                self.stats.clear()
    
    def print_report(self):
        """Print a formatted cache performance report."""
        print("\n" + "="*70)
        print("CACHE PERFORMANCE REPORT")
        print("="*70)
        
        with self.lock:
            if not self.stats:
                print("\nNo cache statistics available.")
                return
            
            # Sort by total calls
            sorted_stats = sorted(
                self.stats.items(),
                key=lambda x: x[1]['total_calls'],
                reverse=True
            )
            
            print(f"\n{'Function':<40} {'Calls':>8} {'Hit Rate':>10} {'Avg Time':>12}")
            print("-"*70)
            
            for func_name, s in sorted_stats:
                hit_rate = (s['hits'] / s['total_calls'] * 100) if s['total_calls'] > 0 else 0
                avg_time = s['avg_compute_time_ms']
                
                print(f"{func_name:<40} {s['total_calls']:>8} {hit_rate:>9.1f}% {avg_time:>10.2f}ms")
            
            # Summary
            total_calls = sum(s['total_calls'] for s in self.stats.values())
            total_hits = sum(s['hits'] for s in self.stats.values())
            overall_hit_rate = (total_hits / total_calls * 100) if total_calls > 0 else 0
            
            print("-"*70)
            print(f"{'OVERALL':<40} {total_calls:>8} {overall_hit_rate:>9.1f}%")
            
            # Recommendations
            print("\n💡 Recommendations:")
            
            for func_name, s in sorted_stats:
                hit_rate = (s['hits'] / s['total_calls'] * 100) if s['total_calls'] > 0 else 0
                
                if hit_rate < 50 and s['total_calls'] > 10:
                    print(f"  ⚠️  {func_name}: Low hit rate ({hit_rate:.1f}%)")
                    print(f"      Consider increasing TTL or reviewing invalidation logic")
                
                if s['avg_compute_time_ms'] > 100 and s['misses'] > 5:
                    print(f"  ⚠️  {func_name}: Slow computation ({s['avg_compute_time_ms']:.1f}ms avg)")
                    print(f"      Cache is valuable here - hit rate of {hit_rate:.1f}% is good")


# Global monitor instance
_monitor = CacheMonitor()


def monitored_cache(func: Callable) -> Callable:
    """
    Decorator to wrap cached functions with monitoring.
    Use this in addition to @st.cache_data.
    
    Example:
        @st.cache_data(ttl=300)
        @monitored_cache
        def get_categories():
            # ...
    """
    func_name = f"{func.__module__}.{func.__name__}"
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if result is in cache (simplified - actual logic depends on Streamlit internals)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        
        compute_time_ms = (end - start) * 1000
        
        # If computation was very fast, it was likely a cache hit
        if compute_time_ms < 1:
            _monitor.record_hit(func_name)
        else:
            _monitor.record_miss(func_name, compute_time_ms)
        
        return result
    
    return wrapper


def get_cache_stats(func_name: str = None) -> dict:
    """Get cache statistics from global monitor."""
    return _monitor.get_stats(func_name)


def print_cache_report():
    """Print cache performance report."""
    _monitor.print_report()


def reset_cache_stats(func_name: str = None):
    """Reset cache statistics."""
    _monitor.reset_stats(func_name)


# Example usage
if __name__ == "__main__":
    print("Cache Monitor Example")
    
    # Simulate some cache activity
    _monitor.record_hit("get_categories")
    _monitor.record_hit("get_categories")
    _monitor.record_miss("get_categories", 45.3)
    
    _monitor.record_hit("get_transactions")
    _monitor.record_miss("get_transactions", 234.1)
    _monitor.record_miss("get_transactions", 198.7)
    
    # Print report
    _monitor.print_report()
