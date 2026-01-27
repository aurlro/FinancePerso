#!/usr/bin/env python3
"""
Performance Benchmark Tool for FinancePerso
Measures page load times, query performance, and generates reports.
"""
import time
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.db.transactions import get_all_transactions, get_pending_transactions
from modules.db.categories import get_categories, get_categories_with_emojis
from modules.db.members import get_members, get_member_mappings
from modules.db.tags import get_all_tags
from modules.db.budgets import get_budgets
from modules.analytics import detect_financial_profile, get_monthly_savings_trend


def benchmark_function(name: str, func, *args, **kwargs):
    """
    Benchmark a single function and return execution time.
    
    Args:
        name: Function name for display
        func: Function to benchmark
        *args, **kwargs: Arguments to pass to function
        
    Returns:
        Tuple of (result, execution_time_ms)
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000
    
    print(f"  {name:40s} {elapsed_ms:8.2f}ms")
    return result, elapsed_ms


def benchmark_db_queries():
    """Benchmark all database query functions."""
    print("\n" + "="*60)
    print("DATABASE QUERY BENCHMARKS")
    print("="*60)
    
    timings = {}
    
    # Transactions
    print("\n📊 Transactions:")
    _, timings['get_all_transactions'] = benchmark_function(
        "get_all_transactions()", get_all_transactions
    )
    _, timings['get_pending_transactions'] = benchmark_function(
        "get_pending_transactions()", get_pending_transactions
    )
    
    # Categories
    print("\n🏷️  Categories:")
    _, timings['get_categories'] = benchmark_function(
        "get_categories()", get_categories
    )
    _, timings['get_categories_with_emojis'] = benchmark_function(
        "get_categories_with_emojis()", get_categories_with_emojis
    )
    
    # Members
    print("\n👥 Members:")
    _, timings['get_members'] = benchmark_function(
        "get_members()", get_members
    )
    _, timings['get_member_mappings'] = benchmark_function(
        "get_member_mappings()", get_member_mappings
    )
    
    # Tags & Budgets
    print("\n🏷️  Tags & Budgets:")
    _, timings['get_all_tags'] = benchmark_function(
        "get_all_tags()", get_all_tags
    )
    _, timings['get_budgets'] = benchmark_function(
        "get_budgets()", get_budgets
    )
    
    return timings


def benchmark_analytics():
    """Benchmark analytics functions."""
    print("\n" + "="*60)
    print("ANALYTICS BENCHMARKS")
    print("="*60)
    
    timings = {}
    
    # Get data once for analytics
    df, load_time = benchmark_function(
        "Load transactions for analytics", get_all_transactions
    )
    
    if not df.empty:
        print("\n📈 Analytics Functions:")
        _, timings['detect_financial_profile'] = benchmark_function(
            "detect_financial_profile()", detect_financial_profile, df
        )
        _, timings['get_monthly_savings_trend'] = benchmark_function(
            "get_monthly_savings_trend(12)", get_monthly_savings_trend, 12
        )
    
    return timings


def generate_report(db_timings, analytics_timings):
    """Generate performance report."""
    print("\n" + "="*60)
    print("PERFORMANCE REPORT")
    print("="*60)
    
    all_timings = {**db_timings, **analytics_timings}
    
    # Sort by execution time
    sorted_timings = sorted(all_timings.items(), key=lambda x: x[1], reverse=True)
    
    print("\n⏱️  Top 5 Slowest Operations:")
    for i, (name, time_ms) in enumerate(sorted_timings[:5], 1):
        print(f"  {i}. {name:40s} {time_ms:8.2f}ms")
    
    print("\n⚡ Top 5 Fastest Operations:")
    for i, (name, time_ms) in enumerate(sorted_timings[-5:], 1):
        print(f"  {i}. {name:40s} {time_ms:8.2f}ms")
    
    # Summary stats
    total_time = sum(all_timings.values())
    avg_time = total_time / len(all_timings) if all_timings else 0
    
    print(f"\n📊 Summary:")
    print(f"  Total operations: {len(all_timings)}")
    print(f"  Total time: {total_time:.2f}ms")
    print(f"  Average time: {avg_time:.2f}ms")
    
    # Performance recommendations
    print("\n💡 Recommendations:")
    slow_ops = [name for name, time_ms in all_timings.items() if time_ms > 100]
    
    if slow_ops:
        print(f"  ⚠️  {len(slow_ops)} operations exceed 100ms threshold:")
        for op in slow_ops[:3]:
            print(f"    - {op}: Consider caching or query optimization")
    else:
        print("  ✅ All operations under 100ms - excellent performance!")
    
    # Cache effectiveness
    cached_ops = [name for name in all_timings.keys() if 'categories' in name or 'members' in name or 'tags' in name]
    if cached_ops:
        avg_cached = sum(all_timings[op] for op in cached_ops) / len(cached_ops)
        print(f"\n💾 Cache Performance:")
        print(f"  Cached operations average: {avg_cached:.2f}ms")
        if avg_cached < 10:
            print("  ✅ Cache is highly effective")
        elif avg_cached < 50:
            print("  ⚠️  Cache could be more effective")
        else:
            print("  ❌ Cache may not be working properly")


def main():
    """Run all benchmarks."""
    print("\n🚀 FinancePerso Performance Benchmark")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run benchmarks
        db_timings = benchmark_db_queries()
        analytics_timings = benchmark_analytics()
        
        # Generate report
        generate_report(db_timings, analytics_timings)
        
        print("\n✅ Benchmark complete!")
        
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
