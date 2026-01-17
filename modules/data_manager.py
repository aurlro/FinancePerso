"""
Database Manager - SQLite operations for MyFinance Companion.
Refactored with context managers for proper connection handling.
"""
import sqlite3
import pandas as pd
from contextlib import contextmanager
import unicodedata
from modules.logger import logger

import streamlit as st
import os

DB_PATH = "Data/finance.db"

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
        if 'tags' not in columns:
            c.execute("ALTER TABLE transactions ADD COLUMN tags TEXT")
        if 'beneficiary' not in columns:
            c.execute("ALTER TABLE transactions ADD COLUMN beneficiary TEXT")
        if 'tx_hash' not in columns:
            c.execute("ALTER TABLE transactions ADD COLUMN tx_hash TEXT")
            c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tx_hash ON transactions(tx_hash)")
        if 'card_suffix' not in columns:
            c.execute("ALTER TABLE transactions ADD COLUMN card_suffix TEXT")
        
        # Performance Indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_status ON transactions(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_date ON transactions(date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_category ON transactions(category_validated)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_member ON transactions(member)")
        
        # Create categories table
        c.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                emoji TEXT DEFAULT '🏷️',
                is_fixed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migration: Add emoji column if it doesn't exist
        c.execute("PRAGMA table_info(categories)")
        columns_cat = [info[1] for info in c.fetchall()]
        if 'emoji' not in columns_cat:
            c.execute("ALTER TABLE categories ADD COLUMN emoji TEXT DEFAULT '🏷️'")
        if 'is_fixed' not in columns_cat:
            c.execute("ALTER TABLE categories ADD COLUMN is_fixed INTEGER DEFAULT 0")

        # Initialize/Migrate default categories
        # name, emoji, is_fixed
        default_cats = [
            ("Alimentation", "🛒", 0), ("Transport", "🚗", 0), ("Loisirs", "🎮", 0), 
            ("Santé", "🏥", 0), ("Logement", "🏠", 1), ("Revenus", "💰", 0), 
            ("Autre", "📦", 0), ("Restaurants", "🍴", 0), ("Abonnements", "📱", 1), 
            ("Achats", "🛍️", 0), ("Services", "🛠️", 0), ("Virement Interne", "🔄", 0),
            ("Hors Budget", "🚫", 0), ("Impôts", "🧾", 1), ("Assurances", "🛡️", 1)
        ]
        c.executemany("INSERT OR IGNORE INTO categories (name, emoji, is_fixed) VALUES (?, ?, ?)", default_cats)
        
        # Create member mappings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS member_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_suffix TEXT UNIQUE,
                member_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

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
        
        c.execute("PRAGMA table_info(learning_rules)")
        columns_rules = [info[1] for info in c.fetchall()]
        if 'priority' not in columns_rules:
            c.execute("ALTER TABLE learning_rules ADD COLUMN priority INTEGER DEFAULT 1")

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
def add_learning_rule(pattern, category, priority=1):
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT OR REPLACE INTO learning_rules (pattern, category, priority) VALUES (?, ?, ?)", (pattern, category, priority))
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

# --- Category Functions ---
def add_category(name, emoji='🏷️', is_fixed=0):
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO categories (name, emoji, is_fixed) VALUES (?, ?, ?)", (name, emoji, is_fixed))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def update_category_emoji(cat_id, new_emoji):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE categories SET emoji = ? WHERE id = ?", (new_emoji, cat_id))
        conn.commit()

def update_category_fixed(cat_id, is_fixed):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE categories SET is_fixed = ? WHERE id = ?", (is_fixed, cat_id))
        conn.commit()

def delete_category(cat_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()

def get_categories():
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT name, emoji FROM categories ORDER BY name", conn)
        # Return list of "Emoji Name" for display or just name? 
        # Usually logic expects just matching name. 
        # But for UI we might want both. Let's return names as usual to avoid breaking AI.
        return df['name'].tolist()

def get_categories_with_emojis():
    """Returns a dict {name: emoji}"""
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT name, emoji FROM categories", conn)
        return dict(zip(df['name'], df['emoji']))

def get_categories_df():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM categories ORDER BY name", conn)

# --- Transaction Functions ---
def transaction_exists(cursor, tx_hash):
    """Check if a transaction exists based on tx_hash."""
    if not tx_hash: return False
    cursor.execute("SELECT 1 FROM transactions WHERE tx_hash = ?", (tx_hash,))
    return cursor.fetchone() is not None

def save_transactions(df):
    """Save transactions using tx_hash to skip duplicates."""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        new_count = 0
        skipped_count = 0
        
        # Pre-process member mappings
        card_maps = get_member_mappings()
        
        for _, row in df.iterrows():
            # Get dict early to avoid pandas copy-on-write issues during iteration
            row_dict = row.to_dict()
            
            # Apply member mapping if card_suffix exists
            suffix = row_dict.get('card_suffix')
            if suffix and suffix in card_maps:
                row_dict['member'] = card_maps[suffix]
                
            if transaction_exists(c, row_dict.get('tx_hash')):
                skipped_count += 1
            else:
                cols = ', '.join(row_dict.keys())
                placeholders = ', '.join(['?'] * len(row_dict))
                query = f"INSERT INTO transactions ({cols}) VALUES ({placeholders})"
                c.execute(query, list(row_dict.values()))
                new_count += 1
            
        conn.commit()
        st.cache_data.clear() # Invalidate cache on new imports
        return new_count, skipped_count

def apply_member_mappings_to_pending():
    """Update all pending transactions based on current mappings."""
    card_maps = get_member_mappings()
    if not card_maps:
        return 0
        
    updated = 0
    with get_db_connection() as conn:
        c = conn.cursor()
        for suffix, member in card_maps.items():
            c.execute("""
                UPDATE transactions 
                SET member = ? 
                WHERE status = 'pending' AND card_suffix = ?
            """, (member, suffix))
            updated += c.rowcount
        conn.commit()
    return updated

def get_pending_transactions():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM transactions WHERE status='pending'", conn)

@st.cache_data
def get_all_hashes():
    """Retrieve all hashes for duplicate detection without loading full rows."""
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT tx_hash FROM transactions WHERE tx_hash IS NOT NULL", conn)
        return set(df['tx_hash'].tolist())

@st.cache_data(show_spinner="Chargement des données...")
def get_all_transactions():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM transactions", conn)

# --- Member Mapping Functions ---
def add_member_mapping(card_suffix, member_name):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO member_mappings (card_suffix, member_name) VALUES (?, ?)", (card_suffix, member_name))
        conn.commit()

def get_member_mappings():
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT card_suffix, member_name FROM member_mappings", conn)
        return dict(zip(df['card_suffix'], df['member_name']))

def delete_member_mapping(m_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM member_mappings WHERE id = ?", (m_id,))
        conn.commit()

def get_member_mappings_df():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM member_mappings", conn)

def update_transaction_category(tx_id, new_category, tags=None, beneficiary=None):
    bulk_update_transaction_status([tx_id], new_category, tags, beneficiary)

def bulk_update_transaction_status(tx_ids, new_category, tags=None, beneficiary=None):
    """Update multiple transactions at once."""
    if not tx_ids:
        return
    
    with get_db_connection() as conn:
        c = conn.cursor()
        # Using placeholders for the IN clause
        placeholders = ', '.join(['?'] * len(tx_ids))
        query = f"""
            UPDATE transactions 
            SET category_validated = ?, 
                tags = ?, 
                beneficiary = ?, 
                status = 'validated' 
            WHERE id IN ({placeholders})
        """
        params = [new_category, tags, beneficiary] + list(tx_ids)
        c.execute(query, params)
        conn.commit()
        st.cache_data.clear() # Invalidate cache on validation

def delete_transaction(tx_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()
        st.cache_data.clear()

def delete_transactions_by_period(month_str):
    """Delete transactions for a specific month (YYYY-MM). Returns deleted count."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE strftime('%Y-%m', date) = ?", (month_str,))
        deleted_count = c.rowcount
        conn.commit()
        st.cache_data.clear()
        return deleted_count

def get_all_account_labels():
    """Retrieve all unique account labels used in transactions."""
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT DISTINCT account_label FROM transactions WHERE account_label IS NOT NULL", conn)
        return df['account_label'].tolist()

def get_available_months():
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT DISTINCT strftime('%Y-%m', date) as month FROM transactions ORDER BY month DESC", conn)
        return df['month'].tolist()

def get_all_tags():
    """Extract all unique tags from validated transactions."""
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT tags FROM transactions WHERE tags IS NOT NULL AND tags != ''", conn)
        if df.empty:
            return []
        
        all_tags = set()
        for t in df['tags']:
            # Handle comma separated tags
            tags_list = [tag.strip() for tag in t.split(',') if tag.strip()]
            all_tags.update(tags_list)
        
        return sorted(list(all_tags))

def get_unique_members():
    def norm(s):
        if not s: return ""
        return "".join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn').lower()
    
    with get_db_connection() as conn:
        # 1. Official Members from config
        df_mem = pd.read_sql("SELECT name FROM members", conn)
        cfg_members = df_mem['name'].dropna().tolist()
        
        # If user has configured members, we strictly follow that list (Managed Mode)
        if cfg_members:
            return sorted(list(set(cfg_members)))
            
        # 2. Fallback: Auto-discovery from transactions (Legacy/Unmanaged Mode)
        df_tx_m = pd.read_sql("SELECT DISTINCT member FROM transactions WHERE member IS NOT NULL AND member != '' AND member != 'Inconnu'", conn)
        df_tx_b = pd.read_sql("SELECT DISTINCT beneficiary FROM transactions WHERE beneficiary IS NOT NULL AND beneficiary != '' AND beneficiary != 'Famille' AND beneficiary != 'Maison'", conn)
        
        tx_names = set(df_tx_m['member'].dropna().tolist() + df_tx_b['beneficiary'].dropna().tolist())
        
        # Deduplicate
        seen = {}
        for m in tx_names:
            n = norm(m)
            if n not in seen: seen[n] = m
            
        return sorted(list(seen.values()))

def update_transaction_member(tx_id, new_member):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE transactions SET member = ? WHERE id = ?", (new_member, tx_id))
        conn.commit()

def get_recent_imports(limit=3):
    """Returns a summary of the latest import sessions."""
    with get_db_connection() as conn:
        query = """
        SELECT account_label, COUNT(*) as count, import_date 
        FROM transactions 
        GROUP BY import_date, account_label 
        ORDER BY import_date DESC 
        LIMIT ?
        """
        return pd.read_sql(query, conn, params=(limit,))

