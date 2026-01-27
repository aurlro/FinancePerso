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
from modules.backup_manager import auto_backup_daily

# Get absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "Data", "finance.db")

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
    auto_backup_daily() # Automatic daily versioning
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
        if 'is_manually_ungrouped' not in columns:
            c.execute("ALTER TABLE transactions ADD COLUMN is_manually_ungrouped INTEGER DEFAULT 0")
        
        # New History Table for Undo
        c.execute('''
            CREATE TABLE IF NOT EXISTS transaction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_group_id TEXT,
                tx_ids TEXT,
                prev_status TEXT,
                prev_category TEXT,
                prev_member TEXT,
                prev_tags TEXT,
                prev_beneficiary TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        if 'suggested_tags' not in columns_cat:
            c.execute("ALTER TABLE categories ADD COLUMN suggested_tags TEXT")

        # Initialize/Migrate default categories
        # name, emoji, is_fixed, suggested_tags
        default_cats = [
            ("Alimentation", "🛒", 0, "Courses, Supermarché, Bio"), 
            ("Transport", "🚗", 0, "Essence, Péage, Parking, SNCF"), 
            ("Loisirs", "🎮", 0, "Cinéma, Sortie, Sport"), 
            ("Santé", "🏥", 0, "Docteur, Pharmacie, Dentiste, Mutuelle, Remboursement"), 
            ("Logement", "🏠", 1, "Loyer, Travaux, Meuble, Déco"), 
            ("Revenus", "💰", 0, "Salaire, Virement, Remboursement"), 
            ("Autre", "📦", 0, ""), 
            ("Restaurants", "🍴", 0, "Restau, Bar, Café, Deliveroo"), 
            ("Abonnements", "📱", 1, "Netflix, Spotify, Internet, Mobile"),
            ("Services", "🛠️", 0, "Assurance, Banque, Impôts"),
            ("Cadeaux", "🎁", 0, "Anniversaire, Noël"),
            ("Virement Interne", "🔄", 0, ""),
            ("Inconnu", "❓", 0, ""),
            ("Hors Budget", "🚫", 0, ""), 
            ("Impôts", "🧾", 1, ""), 
            ("Assurances", "🛡️", 1, "")
        ]
        
        for name, emoji, is_fixed, s_tags in default_cats:
            c.execute("INSERT OR IGNORE INTO categories (name, emoji, is_fixed, suggested_tags) VALUES (?, ?, ?, ?)", (name, emoji, is_fixed, s_tags))
            # Also update existing categories if suggested_tags is empty
            c.execute("UPDATE categories SET suggested_tags = ? WHERE name = ? AND (suggested_tags IS NULL OR suggested_tags = '')", (s_tags, name))
        
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

        # Migration: Add member_type column if it doesn't exist
        c.execute("PRAGMA table_info(members)")
        columns_mem = [info[1] for info in c.fetchall()]
        if 'member_type' not in columns_mem:
            c.execute("ALTER TABLE members ADD COLUMN member_type TEXT DEFAULT 'HOUSEHOLD'")

        # Initialize/Migrate default members
        default_members = [
            ("Aurélien", "HOUSEHOLD"),
            ("Elise", "HOUSEHOLD"),
            ("Famille", "HOUSEHOLD"),
            ("Maison", "HOUSEHOLD"),
            ("Elise Carraud", "EXTERNAL")
        ]
        c.executemany("INSERT OR IGNORE INTO members (name, member_type) VALUES (?, ?)", default_members)
        
        # Initialize/Migrate default rules for internal transfers
        default_rules = [
            ("VIR INST CARRAUD ELISE", "Virement Interne", 5),
            ("VIR VRT de Elise CARRAUD", "Virement Interne", 5),
            ("VIR SEPA CARRAUD ELISE", "Virement Interne", 5)
        ]
        c.executemany("INSERT OR IGNORE INTO learning_rules (pattern, category, priority) VALUES (?, ?, ?)", default_rules)

        # Initialize default card mappings for the user
        default_mappings = [
            ("6759", "Aurélien"),
            ("7238", "Duo"),
            ("9533", "Aurélien")
        ]
        c.executemany("INSERT OR IGNORE INTO member_mappings (card_suffix, member_name) VALUES (?, ?)", default_mappings)

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
def add_member(name, member_type='HOUSEHOLD'):
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO members (name, member_type) VALUES (?, ?)", (name, member_type))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def update_member_type(member_id, member_type):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE members SET member_type = ? WHERE id = ?", (member_type, member_id))
        conn.commit()
        st.cache_data.clear()


def delete_member(member_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()

def get_members():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM members ORDER BY name", conn)

def rename_member(old_name, new_name):
    """
    Rename a member and propagate the change to all transactions and mappings.
    Returns the total number of affected rows.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Update member table
        c.execute("UPDATE members SET name = ? WHERE name = ?", (new_name, old_name))
        
        # Update all transactions (member field)
        c.execute("UPDATE transactions SET member = ? WHERE member = ?", (new_name, old_name))
        tx_count = c.rowcount
        
        # Update all transactions (beneficiary field)
        c.execute("UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", (new_name, old_name))
        tx_count += c.rowcount
        
        # Update member mappings
        c.execute("UPDATE member_mappings SET member_name = ? WHERE member_name = ?", (new_name, old_name))
        
        conn.commit()
        st.cache_data.clear()
        return tx_count

def get_orphan_labels():
    """
    Find values in transactions.member or transactions.beneficiary that are NOT in the members table.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Get members
        c.execute("SELECT name FROM members")
        official_members = {r[0] for r in c.fetchall()}
        # Standard reserved names
        official_members.update({'Maison', 'Famille', 'Inconnu', 'Anonyme', '', None})
        
        # Get unique values from transactions
        c.execute("SELECT DISTINCT member FROM transactions")
        txn_members = {r[0] for r in c.fetchall() if r[0]}
        
        c.execute("SELECT DISTINCT beneficiary FROM transactions")
        txn_benefs = {r[0] for r in c.fetchall() if r[0]}
        
        all_txn_values = txn_members.union(txn_benefs)
        orphans = all_txn_values - official_members
        
        return sorted(list(orphans))

def auto_fix_common_inconsistencies():
    """
    Magic Fix 2.0:
    1. Fix common typos (accented names)
    2. Auto-delete duplicates
    3. Normalize tags to lowercase
    4. Re-apply rules to pending transactions
    """
    total_fixed = 0
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 1. Accent fixes
        fixes = {"Élise": "Elise", "Aurelien": "Aurélien", "Anonyme": "Inconnu"}
        for wrong, right in fixes.items():
            # Only fix if 'wrong' exists in transactions but 'right' is an official member
            c.execute("SELECT count(*) FROM members WHERE name = ?", (right,))
            if c.fetchone()[0] > 0:
                c.execute("UPDATE transactions SET member = ? WHERE member = ?", (right, wrong))
                total_fixed += c.rowcount
                c.execute("UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", (right, wrong))
                total_fixed += c.rowcount
        
        # 2. Auto-delete duplicates (Robust logic)
        query = "SELECT date, label, amount, COUNT(*) as c FROM transactions GROUP BY date, label, amount HAVING c > 1"
        dups = pd.read_sql(query, conn)
        for _, row in dups.iterrows():
            c.execute("SELECT id FROM transactions WHERE date = ? AND label = ? AND amount = ? ORDER BY id ASC", (str(row['date']), row['label'], row['amount']))
            ids = [r[0] for r in c.fetchall()]
            to_delete = ids[1:]
            if to_delete:
                c.execute(f"DELETE FROM transactions WHERE id IN ({','.join(['?']*len(to_delete))})", to_delete)
                total_fixed += c.rowcount
        
        # 3. Normalize tags (lowercase and dedupe)
        c.execute("SELECT id, tags FROM transactions WHERE tags IS NOT NULL AND tags != ''")
        idx_tags = c.fetchall()
        for tx_id, tags_str in idx_tags:
            normalized = ", ".join(sorted(list(set([t.strip().lower() for t in tags_str.split(',') if t.strip()]))))
            if normalized != tags_str:
                c.execute("UPDATE transactions SET tags = ? WHERE id = ?", (normalized, tx_id))
                total_fixed += 1
                
        conn.commit()

    # 4. Re-apply rules (Local import to avoid circular dependency)
    try:
        from modules.categorization import apply_rules
        with get_db_connection() as conn:
            # We fetch fresh pending list
            pending_df = pd.read_sql("SELECT id, label FROM transactions WHERE status='pending'", conn)
            c = conn.cursor()
            for _, row in pending_df.iterrows():
                cat, conf = apply_rules(row['label'])
                if cat:
                    c.execute("UPDATE transactions SET category_validated = ?, status = 'validated' WHERE id = ?", (cat, row['id']))
                    total_fixed += c.rowcount
            conn.commit()
    except Exception as e:
        logger.error(f"Error re-applying rules in magic fix: {e}")

    if total_fixed > 0:
        st.cache_data.clear()
    return total_fixed

def learn_tags_from_history():
    """
    Scans all validated transactions.
    For each category, identifies frequently used tags and adds them to the 'suggested_tags' (allowed) list.
    This bootstraps the Strict Mode.
    """
    count_learned = 0
    with get_db_connection() as conn:
        # Get all tags by category
        df = pd.read_sql("SELECT category_validated, tags FROM transactions WHERE status='validated' AND tags != ''", conn)
        
        cat_tags_map = {}
        
        for _, row in df.iterrows():
            cat = row['category_validated']
            if not cat or cat == 'Inconnu': continue
            
            tags = [t.strip() for t in row['tags'].split(',') if t.strip()]
            if cat not in cat_tags_map: cat_tags_map[cat] = set()
            cat_tags_map[cat].update(tags)
            
        # Update DB
        c = conn.cursor()
        for cat, tags in cat_tags_map.items():
            # Get existing
            c.execute("SELECT id, suggested_tags FROM categories WHERE name = ?", (cat,))
            row = c.fetchone()
            if row:
                cat_id, existing_str = row
                existing = set([t.strip() for t in str(existing_str).split(',') if t.strip() and t != 'None'])
                
                # Merge
                new_set = existing.union(tags)
                if len(new_set) > len(existing):
                    new_str = ", ".join(sorted(list(new_set)))
                    c.execute("UPDATE categories SET suggested_tags = ? WHERE id = ?", (new_str, cat_id))
                    count_learned += (len(new_set) - len(existing))
        
        conn.commit()
    return count_learned

def get_suggested_mappings():
    """
    Identify recurring card suffixes in labels that are not yet mapped to a member.
    """
    with get_db_connection() as conn:
        query = """
            SELECT card_suffix, COUNT(*) as occurrence, MAX(label) as example_label
            FROM transactions
            WHERE card_suffix IS NOT NULL 
              AND card_suffix NOT IN (SELECT card_suffix FROM member_mappings)
            GROUP BY card_suffix
            HAVING occurrence >= 2
            ORDER BY occurrence DESC
        """
        return pd.read_sql(query, conn)

def get_transfer_inconsistencies():
    """Identifie les virements mal catégorisés."""
    with get_db_connection() as conn:
        TRANSFER_KEYWORDS = ["VIR ", "VIREMENT", "VRT", "PIVOT", "MOUVEMENT", "TRANSFERT"]
        likes = " OR ".join([f"upper(label) LIKE '%{k}%'" for k in TRANSFER_KEYWORDS])
        # Missing transfers: 
        # 1. Transactions that are still pending (must be reviewed)
        # 2. Transactions in generic/unclear categories (Virements, Inconnu...)
        # 3. Only flag if they are NOT already Virement Interne or Hors Budget
        query_missing = f"""
            SELECT * FROM transactions 
            WHERE ({likes})
            AND category_validated NOT IN ('Virement Interne', 'Hors Budget') 
            AND (
                status = 'pending'
                OR category_validated IN ('Virements', 'Virements reçus', 'Inconnu')
            )
        """
        
        query_wrong = f"""
            SELECT * FROM transactions 
            WHERE category_validated = 'Virement Interne' 
            AND NOT ({likes})
        """
        
        missing = pd.read_sql(query_missing, conn)
        wrong = pd.read_sql(query_wrong, conn)
        return missing, wrong

def delete_and_replace_label(old_label, replacement_label="Inconnu"):
    """
    1. Update all transactions using this label in member or beneficiary fields.
    2. Delete any member mapping for this label.
    3. Delete the member from the members table if it exists.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 1. Update transactions
        c.execute("UPDATE transactions SET member = ? WHERE member = ?", (replacement_label, old_label))
        count = c.rowcount
        c.execute("UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", (replacement_label, old_label))
        count += c.rowcount
        
        # 2. Delete mappings
        c.execute("DELETE FROM member_mappings WHERE member_name = ?", (old_label,))
        
        # 3. Delete from members table
        c.execute("DELETE FROM members WHERE name = ?", (old_label,))
        
        conn.commit()
        st.cache_data.clear()
        return count


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

def update_category_suggested_tags(cat_id, tags_list_str):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE categories SET suggested_tags = ? WHERE id = ?", (tags_list_str, cat_id))
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

def get_categories_suggested_tags():
    """Returns a dict {name: [tags]}."""
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT name, suggested_tags FROM categories", conn)
        res = {}
        for _, row in df.iterrows():
            tags = [t.strip() for t in str(row['suggested_tags']).split(',') if t.strip() and t != 'None']
            res[row['name']] = tags
        return res

def get_categories_df():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM categories ORDER BY name", conn)

def get_all_categories_including_ghosts():
    """
    Returns a list of all categories found in transactions, distinguishing official vs ghost.
    Returns: [{'name': 'Foo', 'type': 'OFFICIAL'}, {'name': 'Bar', 'type': 'GHOST'}]
    """
    with get_db_connection() as conn:
        # Official
        official_df = pd.read_sql("SELECT name FROM categories", conn)
        official_set = set(official_df['name'].tolist())
        
        # Used
        used_df = pd.read_sql("SELECT DISTINCT category_validated FROM transactions WHERE category_validated IS NOT NULL AND category_validated != 'Inconnu'", conn)
        used_set = set(used_df['category_validated'].tolist())
        
        all_cats = []
        # Union
        all_names = sorted(list(official_set.union(used_set)))
        
        for name in all_names:
            all_cats.append({
                'name': name,
                'type': 'OFFICIAL' if name in official_set else 'GHOST'
            })
            
        return all_cats

def add_tag_to_category(cat_name, new_tag):
    """
    Adds a tag to the allowed/suggested list of a category.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, suggested_tags FROM categories WHERE name = ?", (cat_name,))
        row = c.fetchone()
        if not row:
            return False # Category doesn't exist
            
        cat_id, current_tags_str = row
        current_tags = [t.strip() for t in str(current_tags_str).split(',') if t.strip() and t != 'None']
        
        if new_tag not in current_tags:
            current_tags.append(new_tag)
            new_tags_str = ", ".join(sorted(current_tags))
            c.execute("UPDATE categories SET suggested_tags = ? WHERE id = ?", (new_tags_str, cat_id))
            conn.commit()
            return True
        return True # Already exists

def merge_categories(source_category, target_category):
    """
    Merge source_category into target_category.
    Updates all transactions and learning rules.
    Returns dict with counts of affected rows.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Update transactions (validated category)
        c.execute("""
            UPDATE transactions 
            SET category_validated = ? 
            WHERE category_validated = ?
        """, (target_category, source_category))
        tx_count = c.rowcount
        
        # Update transactions (original category)
        c.execute("""
            UPDATE transactions 
            SET original_category = ? 
            WHERE original_category = ?
        """, (target_category, source_category))
        
        # Update learning rules
        c.execute("""
            UPDATE learning_rules 
            SET category = ? 
            WHERE category = ?
        """, (target_category, source_category))
        rule_count = c.rowcount
        
        conn.commit()
        st.cache_data.clear()
        
        return {
            'transactions': tx_count,
            'rules': rule_count
        }


# --- Transaction Functions ---
def transaction_exists(cursor, tx_hash):
    """Check if a transaction exists based on tx_hash."""
    if not tx_hash: return False
    cursor.execute("SELECT 1 FROM transactions WHERE tx_hash = ?", (tx_hash,))
    return cursor.fetchone() is not None

def save_transactions(df):
    """
    Save transactions using Count-Based Verification to handle duplicates robustly.
    1. Group input by (date, label, amount).
    2. Count existing in DB for each group.
    3. Insert only the surplus (Delta = Input_Count - DB_Count).
    """
    if df.empty:
        return 0, 0

    with get_db_connection() as conn:
        c = conn.cursor()
        
        new_count = 0
        skipped_count = 0
        
        # Pre-process member mappings
        card_maps = get_member_mappings()
        
        # Ensure date is string for consistent grouping/querying
        df['date_str'] = df['date'].astype(str)
        
        # Group by signature
        # We process each unique signature (date, label, amount)
        grouped = df.groupby(['date_str', 'label', 'amount'])
        
        for (date, label, amount), group in grouped:
            # 1. Count in DB
            c.execute("SELECT COUNT(*) FROM transactions WHERE date = ? AND label = ? AND amount = ?", (date, label, amount))
            db_count = c.fetchone()[0]
            
            # 2. Count in Input
            input_count = len(group)
            
            # 3. Calculate Delta
            # If DB has 2 and Input has 3, we need to insert 1 (the 3rd one).
            # If DB has 3 and Input has 3, we insert 0.
            # If DB has 5 (manually added?) and Input has 3, we insert 0.
            to_insert_count = max(0, input_count - db_count)
            skipped_count += (input_count - to_insert_count)
            
            if to_insert_count > 0:
                # We simply take the *last* N rows from the input group.
                # Why last? Because they have higher '_local_occ' index if we generated it, 
                # ensuring hashes are distinct if we re-import larger files.
                # Actually _local_occ logic in ingestion produced 0,1,2... 
                # If DB has 1 (index 0), we want to insert index 1 and 2.
                # So we take the slice `[db_count:]` from the group (which is sorted by ingestion).
                # But to be safe, we just take the last 'to_insert_count' rows.
                
                rows_to_insert = group.tail(to_insert_count)
                
                for _, row in rows_to_insert.iterrows():
                    row_dict = row.to_dict()
                    
                    # Cleanup temp cols
                    if 'date_str' in row_dict: del row_dict['date_str']
                    
                    # Apply member mapping
                    suffix = row_dict.get('card_suffix')
                    if suffix and suffix in card_maps:
                        row_dict['member'] = card_maps[suffix]
                    
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
    with get_db_connection() as conn:
        c = conn.cursor()
        card_maps = get_member_mappings()
        count = 0
        for suffix, member in card_maps.items():
            c.execute("UPDATE transactions SET member = ? WHERE card_suffix = ? AND status = 'pending'", (member, suffix))
            count += c.rowcount
        conn.commit()
        return count

def get_transaction_count(date, label, amount):
    """Count existing transactions with same criteria to help generate stable hash."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM transactions WHERE date = ? AND label = ? AND amount = ?", (str(date), label, amount))
        return c.fetchone()[0]

def get_duplicates_report():
    """Find transactions with same date, label, amount."""
    with get_db_connection() as conn:
        query = """
            SELECT date, label, amount, COUNT(*) as count 
            FROM transactions 
            GROUP BY date, label, amount 
            HAVING count > 1
        """
        return pd.read_sql(query, conn)

def get_transactions_by_criteria(date, label, amount):
    """Retrieve transactions matching specific criteria."""
    with get_db_connection() as conn:
        query = "SELECT * FROM transactions WHERE date = ? AND label = ? AND amount = ?"
        return pd.read_sql(query, conn, params=(str(date), label, amount))

def delete_transaction_by_id(tx_id):
    """Delete a specific transaction."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()
        st.cache_data.clear()
        return c.rowcount

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
    """Update multiple transactions at once and log for undo."""
    if not tx_ids:
        return
    
    import uuid
    import json
    action_id = str(uuid.uuid4())[:8]

    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 1. Capture Previous State for Undo
        placeholders = ', '.join(['?'] * len(tx_ids))
        c.execute(f"SELECT id, status, category_validated, member, tags, beneficiary FROM transactions WHERE id IN ({placeholders})", list(tx_ids))
        rows = c.fetchall()
        
        for r in rows:
            c.execute("""
                INSERT INTO transaction_history (action_group_id, tx_ids, prev_status, prev_category, prev_member, prev_tags, prev_beneficiary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (action_id, str(r[0]), r[1], r[2], r[3], r[4], r[5]))
            
        # 2. Apply Update
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
        st.cache_data.clear()

def undo_last_action():
    """Reverts the last validation action group."""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Get last action ID
        c.execute("SELECT action_group_id FROM transaction_history ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        if not row:
            return False, "Aucune action à annuler."
            
        action_id = row[0]
        
        # Get all entries for this action
        c.execute("SELECT * FROM transaction_history WHERE action_group_id = ?", (action_id,))
        entries = c.fetchall()
        
        for e in entries:
            # e: (id, group_id, tx_id_str, status, cat, mem, tags, benef, ts)
            tx_id = int(e[2])
            c.execute("""
                UPDATE transactions 
                SET status = ?, category_validated = ?, member = ?, tags = ?, beneficiary = ?
                WHERE id = ?
            """, (e[3], e[4], e[5], e[6], e[7], tx_id))
            
        # Delete history for this action
        c.execute("DELETE FROM transaction_history WHERE action_group_id = ?", (action_id,))
        conn.commit()
        st.cache_data.clear()
        return True, f"Action {action_id} annulée ({len(entries)} transactions rétablies)."

def mark_transaction_as_ungrouped(tx_id):
    """Marks a transaction to be permanently excluded from smart grouping."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE transactions SET is_manually_ungrouped = 1 WHERE id = ?", (tx_id,))
        conn.commit()
        st.cache_data.clear()

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

def remove_tag_from_all_transactions(tag_to_remove):
    """
    Removes a specific tag from all transactions that contain it.
    Performs string manipulation on the comma-separated tags field.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        # Find all transactions with this tag (simple LIKE for efficiency first)
        pattern = f"%{tag_to_remove}%"
        c.execute("SELECT id, tags FROM transactions WHERE tags LIKE ?", (pattern,))
        rows = c.fetchall()
        
        updated_count = 0
        for tx_id, tags_str in rows:
            if not tags_str: continue
            
            current_tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            if tag_to_remove in current_tags:
                current_tags.remove(tag_to_remove)
                new_tags_str = ", ".join(current_tags)
                c.execute("UPDATE transactions SET tags = ? WHERE id = ?", (new_tags_str, tx_id))
                updated_count += 1
        
        conn.commit()
        st.cache_data.clear()
        return updated_count

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


# --- App Initialization & Global Stats ---
def is_app_initialized():
    """
    Check if the app has any data. 
    Returns True if at least one transaction exists.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        # Check for transactions table existence first to avoid error on fresh init
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if not c.fetchone():
            return False
            
        c.execute("SELECT 1 FROM transactions LIMIT 1")
        return c.fetchone() is not None

def get_global_stats():
    """
    Get high-level stats for the homepage dashboard.
    Returns dict with simplified KPIs.
    """
    with get_db_connection() as conn:
        try:
            # 1. Total Transactions
            df_count = pd.read_sql("SELECT COUNT(*) as c FROM transactions", conn)
            total_tx = df_count.iloc[0]['c']
            
            # 2. Last Import Date
            df_last = pd.read_sql("SELECT MAX(import_date) as last_imp FROM transactions", conn)
            last_import = df_last.iloc[0]['last_imp']
            
            # 3. Current Month Savings (Approx)
            import datetime
            today = datetime.date.today()
            month_str = today.strftime('%Y-%m')
            
            query_month = f"SELECT amount FROM transactions WHERE strftime('%Y-%m', date) = '{month_str}'"
            df_curr = pd.read_sql(query_month, conn)
            
            if not df_curr.empty:
                inc = df_curr[df_curr['amount'] > 0]['amount'].sum()
                exp = abs(df_curr[df_curr['amount'] < 0]['amount'].sum())
                savings = inc - exp
                savings_rate = (savings / inc * 100) if inc > 0 else 0
            else:
                inc, exp, savings, savings_rate = 0, 0, 0, 0
                
            return {
                "total_transactions": total_tx,
                "last_import": last_import,
                "current_month_savings": savings,
                "current_month_rate": savings_rate,
                "initialized": True
            }
        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            return {"initialized": False}
