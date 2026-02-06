import pytest
import sqlite3
import pandas as pd
import os
from contextlib import contextmanager

# Path to the database - adjust if testing a test.db vs live db
# PROJECT_ROOT is one level up from tests/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "Data", "finance.db")

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def test_no_cross_account_duplicates():
    """
    Integrity Check: Ensure no transactions with identical (date, label, amount)
    exist on different accounts.
    
    This enforces the 'Universal Signature' policy.
    """
    if not os.path.exists(DB_PATH):
        pytest.skip(f"Database not found at {DB_PATH}")

    with get_db_connection() as conn:
        query = """
            SELECT date, label, amount, COUNT(DISTINCT account_label) as accounts_count
            FROM transactions
            GROUP BY date, label, amount
            HAVING accounts_count > 1
        """
        df = pd.read_sql(query, conn)
        
    assert df.empty, f"Found {len(df)} transactions duplicated across accounts! Run 'Debug' page to fix."

def test_no_exact_duplicates_same_account():
    """
    Integrity Check: Ensure no strict duplicates (same date, label, amount, account) 
    unless they are intentionally multiple (which should be rare).
    
    Note: Sometimes we DO have legitimate duplicates (e.g. 2 coffees same day).
    The system handles this with 'local_occurrence_index' in the hash.
    So checking strict DB count > 1 for exact columns might be valid if they have different hashes.
    
    This test checks if we have rows with SAME hash specifically.
    """
    if not os.path.exists(DB_PATH):
        pytest.skip(f"Database not found at {DB_PATH}")
        
    with get_db_connection() as conn:
        query = "SELECT tx_hash, COUNT(*) as c FROM transactions GROUP BY tx_hash HAVING c > 1"
        df = pd.read_sql(query, conn)
        
    assert df.empty, f"Found {len(df)} transactions with colliding hashes (strict duplicates)!"

if __name__ == "__main__":
    # Allow running this file directly
    print("Running Data Integrity Checks...")
    try:
        test_no_cross_account_duplicates()
        print("✅ No cross-account duplicates found.")
    except AssertionError as e:
        print(f"❌ {e}")
        
    try:
        test_no_exact_duplicates_same_account()
        print("✅ No hash collisions found.")
    except AssertionError as e:
        print(f"❌ {e}")
