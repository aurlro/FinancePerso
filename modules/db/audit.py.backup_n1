"""
Data quality audit and cleanup operations.
Handles data integrity checks, duplicate detection, and automatic fixes.
"""
import pandas as pd
from modules.db.connection import get_db_connection
from modules.logger import logger


def auto_fix_common_inconsistencies() -> int:
    """
    Magic Fix 2.0: Automated data quality improvements.
    
    Performs:
    1. Fix common typos (accented names)
    2. Auto-delete duplicates
    3. Normalize tags to lowercase
    4. Re-apply categorization rules to pending transactions
    
    Returns:
        Number of fixes applied
    """
    total_fixed = 0
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Accent fixes
        fixes = {"Élise": "Elise", "Aurelien": "Aurélien", "Anonyme": "Inconnu"}
        for wrong, right in fixes.items():
            # Only fix if 'wrong' exists in transactions but 'right' is an official member
            cursor.execute("SELECT count(*) FROM members WHERE name = ?", (right,))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE transactions SET member = ? WHERE member = ?", (right, wrong))
                total_fixed += cursor.rowcount
                cursor.execute("UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", (right, wrong))
                total_fixed += cursor.rowcount
        
        # 2. Auto-delete duplicates (robust logic)
        query = "SELECT date, label, amount, COUNT(*) as c FROM transactions GROUP BY date, label, amount HAVING c > 1"
        dups = pd.read_sql(query, conn)
        for _, row in dups.iterrows():
            cursor.execute(
                "SELECT id FROM transactions WHERE date = ? AND label = ? AND amount = ? ORDER BY id ASC",
                (str(row['date']), row['label'], row['amount'])
            )
            ids = [r[0] for r in cursor.fetchall()]
            to_delete = ids[1:]  # Keep first, delete rest
            if to_delete:
                placeholders = ','.join(['?'] * len(to_delete))
                cursor.execute(f"DELETE FROM transactions WHERE id IN ({placeholders})", to_delete)
                total_fixed += cursor.rowcount
        
        # 3. Normalize tags (lowercase and dedupe)
        cursor.execute("SELECT id, tags FROM transactions WHERE tags IS NOT NULL AND tags != ''")
        idx_tags = cursor.fetchall()
        for tx_id, tags_str in idx_tags:
            normalized = ", ".join(sorted(list(set([
                t.strip().lower() 
                for t in tags_str.split(',') 
                if t.strip()
            ]))))
            if normalized != tags_str:
                cursor.execute("UPDATE transactions SET tags = ? WHERE id = ?", (normalized, tx_id))
                total_fixed += 1
        
        conn.commit()

    # 4. Re-apply rules (avoid circular import)
    try:
        from modules.categorization import apply_rules
        with get_db_connection() as conn:
            pending_df = pd.read_sql("SELECT id, label FROM transactions WHERE status='pending'", conn)
            cursor = conn.cursor()
            for _, row in pending_df.iterrows():
                cat, conf = apply_rules(row['label'])
                if cat:
                    cursor.execute(
                        "UPDATE transactions SET category_validated = ?, status = 'validated' WHERE id = ?",
                        (cat, row['id'])
                    )
                    total_fixed += cursor.rowcount
            conn.commit()
    except Exception as e:
        logger.error(f"Error re-applying rules in magic fix: {e}")

    if total_fixed > 0:
        # Magic fix touches multiple domains (members, transactions, tags, categories)
        from modules.cache_manager import invalidate_all_caches
        invalidate_all_caches()

    logger.info(f"Auto-fix applied {total_fixed} corrections")
    return total_fixed


def get_suggested_mappings() -> pd.DataFrame:
    """
    Identify recurring card suffixes that are not yet mapped.
    
    Returns:
        DataFrame with columns: card_suffix, occurrence, example_label
        Sorted by frequency (most common first)
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


def get_transfer_inconsistencies() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identify potentially miscategorized internal transfers.
    
    Returns:
        Tuple of (missing_transfers, wrong_transfers)
        - missing_transfers: Transactions with transfer keywords but not categorized as such
        - wrong_transfers: Transactions categorized as transfers but lacking transfer keywords
    """
    with get_db_connection() as conn:
        TRANSFER_KEYWORDS = ["VIR ", "VIREMENT", "VRT", "PIVOT", "MOUVEMENT", "TRANSFERT"]
        likes = " OR ".join([f"upper(label) LIKE '%{k}%'" for k in TRANSFER_KEYWORDS])
        
        # Missing transfers: have keywords but wrong category
        query_missing = f"""
            SELECT * FROM transactions 
            WHERE ({likes})
            AND category_validated NOT IN ('Virement Interne', 'Hors Budget') 
            AND (
                status = 'pending'
                OR category_validated IN ('Virements', 'Virements reçus', 'Inconnu')
            )
        """
        
        # Wrong transfers: categorized as transfer but no keywords
        query_wrong = f"""
            SELECT * FROM transactions 
            WHERE category_validated = 'Virement Interne' 
            AND NOT ({likes})
        """
        
        missing = pd.read_sql(query_missing, conn)
        wrong = pd.read_sql(query_wrong, conn)
        return missing, wrong
