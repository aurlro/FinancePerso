"""
Database Manager - SQLite operations for MyFinance Companion.
Refactored with context managers for proper connection handling.
"""
import sqlite3
import pandas as pd
from contextlib import contextmanager
from modules.logger import logger

DB_PATH = "finance.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database schema and run migrations."""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Create transactions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                label TEXT,
                amount REAL,
                original_category TEXT,
                account_id TEXT,
                category_validated TEXT,
                ai_confidence REAL,
                status TEXT,
                comment TEXT,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migrations
        c.execute("PRAGMA table_info(transactions)")
        columns = [info[1] for info in c.fetchall()]
        if 'ai_confidence' not in columns:
            c.execute("ALTER TABLE transactions ADD COLUMN ai_confidence REAL")
        if 'account_label' not in columns:
            c.execute("ALTER TABLE transactions ADD COLUMN account_label TEXT DEFAULT 'Compte Principal'")
        if 'member' not in columns:
            c.execute("ALTER TABLE transactions ADD COLUMN member TEXT DEFAULT 'Anonyme'")
        
        # Create rules table
        c.execute('''
            CREATE TABLE IF NOT EXISTS learning_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT UNIQUE,
                category TEXT,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create budgets table
        c.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                amount REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create members table
        c.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()

# --- Budget Functions ---
def set_budget(category, amount):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", (category, amount))
        conn.commit()

def get_budgets():
    with get_db_connection() as conn:
        try:
            return pd.read_sql("SELECT * FROM budgets", conn)
        except Exception:
            return pd.DataFrame(columns=['category', 'amount'])

# --- Member Functions ---
def add_member(name):
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO members (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def delete_member(member_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()

def get_members():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM members ORDER BY name", conn)

# --- Learning Rules Functions ---
def add_learning_rule(pattern, category):
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT OR REPLACE INTO learning_rules (pattern, category) VALUES (?, ?)", (pattern, category))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding rule: {e}")
            return False

def get_learning_rules():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM learning_rules ORDER BY created_at DESC", conn)

def delete_learning_rule(rule_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM learning_rules WHERE id = ?", (rule_id,))
        conn.commit()

# --- Transaction Functions ---
def transaction_exists(cursor, row):
    """Check if a transaction exists based on Date + Label + Amount."""
    query = "SELECT 1 FROM transactions WHERE date = ? AND label = ? AND amount = ?"
    cursor.execute(query, (str(row['date']), row['label'], row['amount']))
    return cursor.fetchone() is not None

def save_transactions(df):
    """Save transactions, skipping duplicates. Returns (new_count, skipped_count)."""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        new_transactions = []
        skipped_count = 0
        
        for _, row in df.iterrows():
            if not transaction_exists(c, row):
                new_transactions.append(row)
            else:
                skipped_count += 1
                
        if new_transactions:
            df_new = pd.DataFrame(new_transactions)
            df_new.to_sql('transactions', conn, if_exists='append', index=False)
            
        conn.commit()
        return len(new_transactions), skipped_count

def get_pending_transactions():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM transactions WHERE status='pending'", conn)

def get_all_transactions():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM transactions", conn)

def update_transaction_category(tx_id, new_category):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE transactions SET category_validated = ?, status = 'validated' WHERE id = ?", (new_category, tx_id))
        conn.commit()

def delete_transaction(tx_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()

def delete_transactions_by_period(month_str):
    """Delete transactions for a specific month (YYYY-MM). Returns deleted count."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE strftime('%Y-%m', date) = ?", (month_str,))
        deleted_count = c.rowcount
        conn.commit()
        return deleted_count

def get_available_months():
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT DISTINCT strftime('%Y-%m', date) as month FROM transactions ORDER BY month DESC", conn)
        return df['month'].tolist()

def get_unique_members():
    with get_db_connection() as conn:
        df_tx = pd.read_sql("SELECT DISTINCT member FROM transactions WHERE member IS NOT NULL AND member != '' AND member != 'Inconnu'", conn)
        tx_members = set(df_tx['member'].dropna().tolist())
        
        df_mem = pd.read_sql("SELECT name FROM members", conn)
        cfg_members = set(df_mem['name'].tolist())
        
        return sorted(list(tx_members.union(cfg_members)))

def update_transaction_member(tx_id, new_member):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE transactions SET member = ? WHERE id = ?", (new_member, tx_id))
        conn.commit()
