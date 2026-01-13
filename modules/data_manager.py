import sqlite3
import pandas as pd
import os
from modules.logger import logger

DB_PATH = "finance.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    
    # Simple migration: check if column exists, if not add it
    c.execute("PRAGMA table_info(transactions)")
    columns = [info[1] for info in c.fetchall()]
    if 'ai_confidence' not in columns:
        c.execute("ALTER TABLE transactions ADD COLUMN ai_confidence REAL")
    if 'account_label' not in columns:
        c.execute("ALTER TABLE transactions ADD COLUMN account_label TEXT DEFAULT 'Compte Principal'")
    if 'member' not in columns:
        c.execute("ALTER TABLE transactions ADD COLUMN member TEXT DEFAULT 'Anonyme'")
    
    # Create rules table for Memory
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT UNIQUE,
            category TEXT,
            priority INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''') # Pattern should be unique to avoid conflicts

    # Migration for rules table (if needed, though IF NOT EXISTS handles creation)
    # Simple migration logic usually unnecessary for new table, but consistency is good.

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
    conn.close()

def set_budget(category, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Insert or Replace
    c.execute("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", (category, amount))
    conn.commit()
    conn.close()

def get_budgets():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM budgets", conn)
    except:
        df = pd.DataFrame(columns=['category', 'amount'])
    conn.close()
    return df

def add_member(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO members (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Already exists
    finally:
        conn.close()

def delete_member(member_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

def get_members():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM members ORDER BY name", conn)
    conn.close()
    return df

def add_learning_rule(pattern, category):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # Check if exists, update category if so
        c.execute("INSERT OR REPLACE INTO learning_rules (pattern, category) VALUES (?, ?)", (pattern, category))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding rule: {e}")
        return False
    finally:
        conn.close()

def get_learning_rules():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM learning_rules ORDER BY created_at DESC", conn)
    conn.close()
    return df

def delete_learning_rule(rule_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM learning_rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()

def transaction_exists(cursor, row):
    """
    Check if a transaction exists based on Date + Label + Amount + Status (optional, but keep it simple)
    Using Date + Label + Amount is usually unique enough for MVP.
    """
    query = "SELECT 1 FROM transactions WHERE date = ? AND label = ? AND amount = ?"
    cursor.execute(query, (str(row['date']), row['label'], row['amount']))
    return cursor.fetchone() is not None

def save_transactions(df):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    new_transactions = []
    skipped_count = 0
    
    for index, row in df.iterrows():
        if not transaction_exists(c, row):
            new_transactions.append(row)
        else:
            skipped_count += 1
            
    if new_transactions:
        # bulk insert via pandas is easier, reused df structure
        df_new = pd.DataFrame(new_transactions)
        df_new.to_sql('transactions', conn, if_exists='append', index=False)
        
    conn.commit()
    conn.close()
    return len(new_transactions), skipped_count

def get_pending_transactions():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM transactions WHERE status='pending'", conn)
    conn.close()
    return df

def get_all_transactions():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()
    return df

def update_transaction_category(tx_id, new_category):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE transactions SET category_validated = ?, status = 'validated' WHERE id = ?", (new_category, tx_id))
    conn.commit()
    conn.close()

def delete_transaction(tx_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()

def delete_transactions_by_period(month_str):
    """
    Delete transactions for a specific month (YYYY-MM).
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # SQLite strftime('%Y-%m', date)
    c.execute("DELETE FROM transactions WHERE strftime('%Y-%m', date) = ?", (month_str,))
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    return deleted_count

def get_available_months():
    conn = sqlite3.connect(DB_PATH)
    # Get distinct YYYY-MM
    df = pd.read_sql("SELECT DISTINCT strftime('%Y-%m', date) as month FROM transactions ORDER BY month DESC", conn)
    conn.close()
    return df['month'].tolist()

def get_unique_members():
    conn = sqlite3.connect(DB_PATH)
    # Get distinct members from transactions
    df_tx = pd.read_sql("SELECT DISTINCT member FROM transactions WHERE member IS NOT NULL AND member != '' AND member != 'Inconnu'", conn)
    tx_members = set(df_tx['member'].dropna().tolist())
    
    # Get members from config
    df_mem = pd.read_sql("SELECT name FROM members", conn)
    cfg_members = set(df_mem['name'].tolist())
    
    conn.close()
    
    # Combine and sort
    all_members = sorted(list(tx_members.union(cfg_members)))
    return all_members

def update_transaction_member(tx_id, new_member):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE transactions SET member = ? WHERE id = ?", (new_member, tx_id))
    conn.commit()
    conn.close()
