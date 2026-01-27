#!/usr/bin/env python3
"""
Database Query Profiler for FinancePerso
Analyzes SQL queries, identifies N+1 problems, and suggests optimizations.
"""
import sqlite3
import sys
import os
from pathlib import Path
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class QueryProfiler:
    """Profile SQLite queries and provide optimization suggestions."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.query_stats = defaultdict(lambda: {'count': 0, 'total_time': 0})
        
    def analyze_query_plan(self, query: str) -> dict:
        """
        Analyze query execution plan using EXPLAIN QUERY PLAN.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            Dict with analysis results
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get query plan
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            plan = cursor.fetchall()
            
            # Analyze for performance issues
            issues = []
            uses_index = False
            has_scan = False
            
            for row in plan:
                detail = str(row)
                if 'SCAN' in detail.upper():
                    has_scan = True
                    issues.append("⚠️  Full table scan detected")
                if 'USING INDEX' in detail.upper():
                    uses_index = True
            
            result = {
                'query': query[:100] + '...' if len(query) > 100 else query,
                'plan': plan,
                'uses_index': uses_index,
                'has_scan': has_scan,
                'issues': issues
            }
            
        except Exception as e:
            result = {
                'query': query,
                'error': str(e),
                'issues': [f"❌ Query analysis failed: {e}"]
            }
        
        finally:
            conn.close()
        
        return result
    
    def get_table_stats(self) -> dict:
        """Get statistics about all tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        try:
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                # Row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                # Table size (approximate)
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                stats[table_name] = {
                    'rows': row_count,
                    'columns': len(columns),
                    'column_names': [col[1] for col in columns]
                }
        
        finally:
            conn.close()
        
        return stats
    
    def get_index_usage(self) -> list:
        """Get all indexes and their usage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        indexes = []
        
        try:
            # Get all indexes
            cursor.execute("""
                SELECT name, tbl_name, sql 
                FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            
            for name, table, sql in cursor.fetchall():
                indexes.append({
                    'name': name,
                    'table': table,
                    'sql': sql or '(auto-generated)'
                })
        
        finally:
            conn.close()
        
        return indexes
    
    def suggest_indexes(self, table_stats: dict) -> list:
        """Suggest potentially useful indexes based on table structure."""
        suggestions = []
        
        # Common patterns that benefit from indexes
        patterns = {
            'date': ['date', 'created_at', 'updated_at', 'import_date'],
            'status': ['status', 'validated', 'pending'],
            'foreign_keys': ['category_id', 'member_id', 'category_validated'],
            'search': ['label', 'pattern', 'name']
        }
        
        for table, stats in table_stats.items():
            if stats['rows'] < 100:
                continue  # Skip small tables
            
            columns = stats['column_names']
            
            for col in columns:
                for pattern_type, pattern_cols in patterns.items():
                    if any(p in col.lower() for p in pattern_cols):
                        suggestions.append({
                            'table': table,
                            'column': col,
                            'reason': f"Large table ({stats['rows']} rows) with {pattern_type} column",
                            'sql': f"CREATE INDEX idx_{table}_{col} ON {table}({col})"
                        })
        
        return suggestions


def main():
    """Run database profiling."""
    print("\n🔍 FinancePerso Database Profiler")
    print("="*70)
    
    # Get database path
    db_path = os.getenv('DB_PATH', 'Data/finance.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
    profiler = QueryProfiler(db_path)
    
    # 1. Table Statistics
    print("\n📊 TABLE STATISTICS")
    print("-"*70)
    table_stats = profiler.get_table_stats()
    
    for table, stats in sorted(table_stats.items(), key=lambda x: x[1]['rows'], reverse=True):
        print(f"  {table:20s} {stats['rows']:8,} rows, {stats['columns']:2} columns")
    
    # 2. Index Usage
    print("\n📇 CURRENT INDEXES")
    print("-"*70)
    indexes = profiler.get_index_usage()
    
    if indexes:
        for idx in indexes:
            print(f"  {idx['name']:30s} on {idx['table']}")
            print(f"    SQL: {idx['sql']}")
    else:
        print("  ⚠️  No custom indexes found!")
    
    # 3. Common Query Analysis
    print("\n🔎 ANALYZING COMMON QUERIES")
    print("-"*70)
    
    common_queries = [
        "SELECT * FROM transactions WHERE status = 'PENDING'",
        "SELECT * FROM transactions WHERE category_validated = 'Alimentation'",
        "SELECT * FROM transactions WHERE strftime('%Y-%m', date) = '2024-01'",
        "SELECT category_validated, COUNT(*) FROM transactions GROUP BY category_validated"
    ]
    
    for query in common_queries:
        print(f"\nQuery: {query}")
        analysis = profiler.analyze_query_plan(query)
        
        if 'error' not in analysis:
            if analysis['uses_index']:
                print("  ✅ Uses index")
            if analysis['has_scan']:
                print("  ⚠️  Contains table scan")
            
            for issue in analysis['issues']:
                print(f"  {issue}")
        else:
            print(f"  ❌ Error: {analysis['error']}")
    
    # 4. Optimization Suggestions
    print("\n💡 OPTIMIZATION SUGGESTIONS")
    print("-"*70)
    
    suggestions = profiler.suggest_indexes(table_stats)
    
    if suggestions:
        print("\n  Recommended indexes:")
        for i, sug in enumerate(suggestions[:5], 1):  # Top 5
            print(f"\n  {i}. {sug['table']}.{sug['column']}")
            print(f"     Reason: {sug['reason']}")
            print(f"     SQL: {sug['sql']}")
    else:
        print("  ✅ No additional indexes recommended")
    
    # 5. General Tips
    print("\n📋 PERFORMANCE TIPS")
    print("-"*70)
    
    total_rows = sum(s['rows'] for s in table_stats.values())
    transactions_count = table_stats.get('transactions', {}).get('rows', 0)
    
    print(f"\n  Database size: {total_rows:,} total rows")
    print(f"  Transactions: {transactions_count:,} rows")
    
    if transactions_count > 10000:
        print("\n  ⚠️  Large transactions table detected:")
        print("    - Consider archiving old transactions")
        print("    - Ensure date-based queries use indexes")
        print("    - Use date range filters in queries")
    
    if len(indexes) < 3:
        print("\n  ⚠️  Few indexes detected:")
        print("    - Add indexes on frequently queried columns")
        print("    - Consider composite indexes for multi-column filters")
    
    print("\n✅ Profiling complete!")


if __name__ == "__main__":
    main()
