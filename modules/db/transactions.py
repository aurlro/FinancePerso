"""
Transaction management operations.
Handles CRUD operations for transactions, the core entity of the application.
"""
import uuid
import pandas as pd
import streamlit as st
from modules.db.connection import get_db_connection, build_filter_clause
from modules.db.members import get_member_mappings
from modules.logger import logger


def transaction_exists(cursor, tx_hash: str) -> bool:
    """
    Check if a transaction exists based on tx_hash.
    
    Args:
        cursor: Database cursor
        tx_hash: Transaction hash to check
        
    Returns:
        True if transaction exists, False otherwise
    """
    if not tx_hash:
        return False
    cursor.execute("SELECT 1 FROM transactions WHERE tx_hash = ?", (tx_hash,))
    return cursor.fetchone() is not None


def save_transactions(df: pd.DataFrame) -> tuple[int, int]:
    """
    Save transactions using Count-Based Verification for robust duplicate handling.
    
    Algorithm:
    1. Group input by (date, label, amount)
    2. Count existing in DB for each group
    3. Insert only the surplus (Delta = Input_Count - DB_Count)
    
    Args:
        df: DataFrame with transaction data
        
    Returns:
        Tuple of (new_count, skipped_count)
        
    Example:
        df = pd.read_csv("transactions.csv")
        new, skipped = save_transactions(df)
        print(f"Imported {new} new transactions, skipped {skipped} duplicates")
    """
    if df.empty:
        return 0, 0

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        new_count = 0
        skipped_count = 0
        
        # Pre-load member mappings
        card_maps = get_member_mappings()
        
        # Ensure date is string for consistent grouping/querying
        df['date_str'] = df['date'].astype(str)
        
        # Group by signature (date, label, amount)
        grouped = df.groupby(['date_str', 'label', 'amount'])
        
        for (date, label, amount), group in grouped:
            # 1. Count in DB
            cursor.execute(
                "SELECT COUNT(*) FROM transactions WHERE date = ? AND label = ? AND amount = ?",
                (date, label, amount)
            )
            db_count = cursor.fetchone()[0]
            
            # 2. Count in Input
            input_count = len(group)
            
            # 3. Calculate Delta
            to_insert_count = max(0, input_count - db_count)
            skipped_count += (input_count - to_insert_count)
            
            if to_insert_count > 0:
                # Take the last N rows from the group
                rows_to_insert = group.tail(to_insert_count)
                
                for _, row in rows_to_insert.iterrows():
                    row_dict = row.to_dict()
                    
                    # Cleanup temp columns
                    if 'date_str' in row_dict:
                        del row_dict['date_str']
                    
                    # Apply member mapping if card suffix exists
                    suffix = row_dict.get('card_suffix')
                    if suffix and suffix in card_maps:
                        row_dict['member'] = card_maps[suffix]
                    
                    cols = ', '.join(row_dict.keys())
                    placeholders = ', '.join(['?'] * len(row_dict))
                    query = f"INSERT INTO transactions ({cols}) VALUES ({placeholders})"
                    cursor.execute(query, list(row_dict.values()))
                    new_count += 1
        
        conn.commit()

    from modules.cache_manager import invalidate_transaction_caches
    invalidate_transaction_caches()

    logger.info(f"Imported {new_count} new transactions, skipped {skipped_count} duplicates")
    return new_count, skipped_count


def apply_member_mappings_to_pending() -> int:
    """
    Update all pending transactions based on current member mappings.
    
    Returns:
        Number of transactions updated
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        card_maps = get_member_mappings()
        count = 0
        for suffix, member in card_maps.items():
            cursor.execute(
                "UPDATE transactions SET member = ? WHERE card_suffix = ? AND status = 'pending'",
                (member, suffix)
            )
            count += cursor.rowcount
        conn.commit()
        return count


def get_transaction_count(date: str, label: str, amount: float) -> int:
    """
    Count existing transactions matching criteria.
    
    Used to generate stable hashes for duplicate detection.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM transactions WHERE date = ? AND label = ? AND amount = ?",
            (str(date), label, amount)
        )
        return cursor.fetchone()[0]


def get_duplicates_report() -> pd.DataFrame:
    """
    Find transactions with identical date, label, and amount.
    
    Returns:
        DataFrame with columns: date, label, amount, count
    """
    with get_db_connection() as conn:
        query = """
            SELECT date, label, amount, COUNT(*) as count 
            FROM transactions 
            GROUP BY date, label, amount 
            HAVING count > 1
        """
        return pd.read_sql(query, conn)


def get_transactions_by_criteria(
    date: str = None, 
    label: str = None, 
    amount: float = None,
    period: str = None,
    label_contains: str = None
) -> pd.DataFrame:
    """
    Retrieve transactions matching specific criteria (exact or partial).
    
    Args:
        date: Exact date match (YYYY-MM-DD)
        label: Exact label match
        amount: Exact amount match
        period: Month period match (YYYY-MM)
        label_contains: Partial label match (LIKE %value%)
    """
    with get_db_connection() as conn:
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if date:
            query += " AND date = ?"
            params.append(str(date))
        if label:
            query += " AND label = ?"
            params.append(label)
        if amount is not None:
            query += " AND amount = ?"
            params.append(amount)
        if period:
             query += " AND strftime('%Y-%m', date) = ?"
             params.append(period)
        if label_contains:
             query += " AND label LIKE ?"
             params.append(f"%{label_contains}%")
             
        return pd.read_sql(query, conn, params=params)


def delete_transaction_by_id(tx_id: int) -> int:
    """
    Delete a specific transaction.
    
    Returns:
        Number of rows deleted (0 or 1)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()
        from modules.cache_manager import invalidate_transaction_caches
        invalidate_transaction_caches()
        return cursor.rowcount


def add_tag_to_transactions(tx_ids: list[int], tag: str) -> int:
    """
    Add a tag to existing tags for multiple transactions without overwriting.
    
    Args:
        tx_ids: List of transaction IDs
        tag: Tag to add
        
    Returns:
        Number of transactions updated
    """
    if not tx_ids:
        return 0
        
    updated = 0
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get current tags
        placeholders = ', '.join(['?'] * len(tx_ids))
        cursor.execute(f"SELECT id, tags FROM transactions WHERE id IN ({placeholders})", list(tx_ids))
        rows = cursor.fetchall()
        
        for tx_id, current_tags in rows:
            new_tags = tag
            if current_tags:
                if tag in current_tags.split(','):
                    continue # Already tagged
                new_tags = f"{current_tags},{tag}"
            
            cursor.execute(
                "UPDATE transactions SET tags = ? WHERE id = ?",
                (new_tags, tx_id)
            )
            updated += 1

        conn.commit()

    from modules.cache_manager import invalidate_transaction_caches
    invalidate_transaction_caches()
    return updated



def get_pending_transactions() -> pd.DataFrame:
    """
    Get all pending (unvalidated) transactions.
    
    Returns:
        DataFrame with all pending transactions
    """
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM transactions WHERE status='pending'", conn)


@st.cache_data
def get_all_hashes() -> set[str]:
    """
    Retrieve all transaction hashes for fast duplicate detection.
    
    Returns:
        Set of all tx_hash values
    """
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT tx_hash FROM transactions WHERE tx_hash IS NOT NULL", conn)
        return set(df['tx_hash'].tolist())


@st.cache_data(show_spinner="Chargement des données...")
def get_all_transactions(
    limit: int = None,
    offset: int = 0,
    filters: dict = None,
    order_by: str = "date DESC"
) -> pd.DataFrame:
    """
    Get transactions with optional pagination and filtering.

    Args:
        limit: Maximum number of rows to return (None for all)
        offset: Number of rows to skip (for pagination)
        filters: Dictionary of filter conditions {column: value or (operator, value)}
                 Examples: {"status": "validated"}, {"amount": (">", 100)}
        order_by: SQL ORDER BY clause (default: "date DESC")

    Returns:
        DataFrame with transactions matching the criteria
    """
    query = "SELECT * FROM transactions WHERE 1=1"

    # Apply filters using helper function
    where_clause, params = build_filter_clause(filters)
    query += where_clause

    # Add ordering
    if order_by:
        query += f" ORDER BY {order_by}"

    # Add pagination
    if limit is not None:
        query += f" LIMIT {limit}"
        if offset > 0:
            query += f" OFFSET {offset}"

    with get_db_connection() as conn:
        return pd.read_sql(query, conn, params=params if params else None)


@st.cache_data(show_spinner="Chargement des données...")
def get_transactions_count(filters: dict = None) -> int:
    """
    Get total count of transactions matching filters.
    Useful for pagination controls.

    Args:
        filters: Dictionary of filter conditions

    Returns:
        Total count of matching transactions
    """
    query = "SELECT COUNT(*) as count FROM transactions WHERE 1=1"

    # Apply filters using helper function
    where_clause, params = build_filter_clause(filters)
    query += where_clause

    with get_db_connection() as conn:
        result = pd.read_sql(query, conn, params=params if params else None)
        return result['count'].iloc[0]


def update_transaction_category(tx_id: int, new_category: str, tags: str = None, beneficiary: str = None) -> None:
    """
    Update a single transaction's category.
    
    Delegates to bulk_update_transaction_status for consistency.
    """
    bulk_update_transaction_status([tx_id], new_category, tags, beneficiary)


def bulk_update_transaction_status(
    tx_ids: list[int], 
    new_category: str, 
    tags: str = None, 
    beneficiary: str = None
) -> None:
    """
    Update multiple transactions at once and log for undo.
    
    Creates a single action group that can be reverted using undo_last_action().
    
    Args:
        tx_ids: List of transaction IDs to update
        new_category: New category to assign
        tags: Optional tags to set
        beneficiary: Optional beneficiary to set
    """
    if not tx_ids:
        return
    
    action_id = str(uuid.uuid4())[:8]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Capture Previous State for Undo
        placeholders = ', '.join(['?'] * len(tx_ids))
        cursor.execute(
            f"SELECT id, status, category_validated, member, tags, beneficiary "
            f"FROM transactions WHERE id IN ({placeholders})",
            list(tx_ids)
        )
        rows = cursor.fetchall()
        
        for r in rows:
            cursor.execute(
                """
                INSERT INTO transaction_history 
                (action_group_id, tx_ids, prev_status, prev_category, prev_member, prev_tags, prev_beneficiary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (action_id, str(r[0]), r[1], r[2], r[3], r[4], r[5])
            )
        
        # 2. Apply Update
        set_clauses = [
            "category_validated = ?", 
            "status = 'validated'"
        ]
        params = [new_category]
        
        if tags is not None:
            set_clauses.append("tags = ?")
            params.append(tags)
            
        if beneficiary is not None:
            set_clauses.append("beneficiary = ?")
            params.append(beneficiary)
            
        query = f"""
            UPDATE transactions 
            SET {', '.join(set_clauses)} 
            WHERE id IN ({placeholders})
        """
        params.extend(list(tx_ids))
        
        cursor.execute(query, params)
        conn.commit()
        from modules.cache_manager import invalidate_transaction_caches
        invalidate_transaction_caches()


def undo_last_action() -> tuple[bool, str]:
    """
    Revert the last validation action group.
    
    Returns:
        Tuple of (success, message)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get last action ID
        cursor.execute("SELECT action_group_id FROM transaction_history ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return False, "Aucune action à annuler."
        
        action_id = row[0]
        
        # Get all entries for this action
        cursor.execute("SELECT * FROM transaction_history WHERE action_group_id = ?", (action_id,))
        entries = cursor.fetchall()
        
        for e in entries:
            # e: (id, group_id, tx_id_str, status, cat, mem, tags, benef, ts)
            tx_id = int(e[2])
            cursor.execute(
                """
                UPDATE transactions 
                SET status = ?, category_validated = ?, member = ?, tags = ?, beneficiary = ?
                WHERE id = ?
                """,
                (e[3], e[4], e[5], e[6], e[7], tx_id)
            )
        
        # Delete history for this action
        cursor.execute("DELETE FROM transaction_history WHERE action_group_id = ?", (action_id,))
        conn.commit()
        from modules.cache_manager import invalidate_transaction_caches
        invalidate_transaction_caches()
        return True, f"Action {action_id} annulée ({len(entries)} transactions rétablies)."


def mark_transaction_as_ungrouped(tx_id: int) -> None:
    """Mark a transaction to be permanently excluded from smart grouping."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE transactions SET is_manually_ungrouped = 1 WHERE id = ?", (tx_id,))
        conn.commit()
        from modules.cache_manager import invalidate_transaction_caches
        invalidate_transaction_caches()


def delete_transaction(tx_id: int) -> None:
    """Delete a transaction."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()
        from modules.cache_manager import invalidate_transaction_caches
        invalidate_transaction_caches()


def delete_transactions_by_period(month_str: str) -> int:
    """
    Delete all transactions for a specific month (YYYY-MM).
    
    Args:
        month_str: Month in format 'YYYY-MM'
        
    Returns:
        Number of transactions deleted
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE strftime('%Y-%m', date) = ?", (month_str,))
        deleted_count = cursor.rowcount
        conn.commit()
        from modules.cache_manager import invalidate_transaction_caches
        invalidate_transaction_caches()
        logger.info(f"Deleted {deleted_count} transactions for period {month_str}")
        return deleted_count
