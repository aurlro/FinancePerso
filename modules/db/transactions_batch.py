"""
Batch operations for transactions with multi-table transactions.
Provides atomic operations for complex database updates.
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
from modules.db.connection import get_db_connection
from modules.db.rules import add_learning_rule
from modules.logger import logger


@contextmanager
def atomic_transaction():
    """
    Context manager for atomic database transactions.
    All operations within the context are committed or rolled back together.
    
    Example:
        with atomic_transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ...")
            cursor.execute("UPDATE ...")
            # Both operations succeed or both fail
    """
    conn = None
    try:
        conn = get_db_connection().__enter__()
        conn.execute("BEGIN")
        yield conn
        conn.commit()
        logger.info("Atomic transaction committed successfully")
    except Exception as e:
        if conn:
            conn.rollback()
            logger.error(f"Atomic transaction rolled back: {e}")
        raise
    finally:
        if conn:
            conn.close()


def batch_update_transactions_with_rule(
    transaction_ids: List[int],
    category: str,
    pattern: Optional[str] = None,
    member: Optional[str] = None,
    tags: Optional[str] = None,
    beneficiary: Optional[str] = None
) -> Tuple[int, bool]:
    """
    Atomically update transactions and create a learning rule.
    
    Args:
        transaction_ids: List of transaction IDs to update
        category: Category to assign
        pattern: Optional pattern for learning rule
        member: Optional member to assign
        tags: Optional tags to assign
        beneficiary: Optional beneficiary to assign
        
    Returns:
        Tuple of (updated_count, rule_created)
        
    Example:
        count, created = batch_update_transactions_with_rule(
            [1, 2, 3], 
            category="Alimentation",
            pattern="CARREFOUR",
            member="Aurélien"
        )
    """
    with atomic_transaction() as conn:
        cursor = conn.cursor()
        
        # Build update query dynamically
        update_fields = ["category_validated = ?", "status = 'validated'"]
        params = [category]
        
        if member:
            update_fields.append("member = ?")
            params.append(member)
        
        if tags:
            update_fields.append("tags = ?")
            params.append(tags)
        
        if beneficiary:
            update_fields.append("beneficiary = ?")
            params.append(beneficiary)
        
        # Update transactions
        placeholders = ', '.join(['?'] * len(transaction_ids))
        query = f"""
            UPDATE transactions 
            SET {', '.join(update_fields)}
            WHERE id IN ({placeholders})
        """
        params.extend(transaction_ids)
        
        cursor.execute(query, params)
        updated_count = cursor.rowcount
        
        # Create learning rule if pattern provided
        rule_created = False
        if pattern and len(pattern) >= 3:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO learning_rules (pattern, category, priority) VALUES (?, ?, ?)",
                    (pattern.upper(), category, 5)
                )
                rule_created = cursor.rowcount > 0
            except Exception as e:
                logger.warning(f"Failed to create learning rule: {e}")
        
        return updated_count, rule_created


def batch_categorize_transactions(
    transactions_df: pd.DataFrame,
    use_ai: bool = True,
    progress_callback=None
) -> pd.DataFrame:
    """
    Batch categorize transactions with optimized performance.
    
    Args:
        transactions_df: DataFrame with transactions to categorize
        use_ai: Whether to use AI for categorization
        progress_callback: Optional callback function(current, total)
        
    Returns:
        DataFrame with added 'category_validated', 'ai_confidence', 'status' columns
        
    Example:
        df = batch_categorize_transactions(df, use_ai=True)
    """
    from modules.categorization import categorize_transaction
    from modules.db.rules import get_compiled_learning_rules
    
    # Pre-load rules for performance
    compiled_rules = get_compiled_learning_rules()
    
    results = []
    total = len(transactions_df)
    
    for i, (idx, row) in enumerate(transactions_df.iterrows()):
        # Update progress
        if progress_callback and i % 10 == 0:
            progress_callback(i, total)
        
        # Categorize
        cat, source, conf = categorize_transaction(
            row['label'], 
            row['amount'], 
            row['date']
        )
        
        results.append({
            'category_validated': cat if cat else 'Inconnu',
            'ai_confidence': conf,
            'status': 'validated' if source == 'rule' else 'pending'
        })
    
    # Update progress at end
    if progress_callback:
        progress_callback(total, total)
    
    # Merge results
    results_df = pd.DataFrame(results, index=transactions_df.index)
    return pd.concat([transactions_df, results_df], axis=1)


def merge_categories_atomic(
    source_category: str,
    target_category: str
) -> Dict[str, int]:
    """
    Atomically merge two categories.
    Updates all transactions, rules, and budgets in a single transaction.
    
    Args:
        source_category: Category to merge from (will be removed)
        target_category: Category to merge into (will remain)
        
    Returns:
        Dict with counts: {'transactions': int, 'rules': int, 'budgets': int}
        
    Example:
        result = merge_categories_atomic("Courses", "Alimentation")
        print(f"Merged {result['transactions']} transactions")
    """
    with atomic_transaction() as conn:
        cursor = conn.cursor()
        
        # Update transactions
        cursor.execute(
            """
            UPDATE transactions 
            SET category_validated = ? 
            WHERE category_validated = ? COLLATE NOCASE
            """,
            (target_category, source_category)
        )
        tx_count = cursor.rowcount
        
        # Update learning rules
        cursor.execute(
            """
            UPDATE learning_rules 
            SET category = ? 
            WHERE category = ? COLLATE NOCASE
            """,
            (target_category, source_category)
        )
        rules_count = cursor.rowcount
        
        # Update budgets (transfer amount if target doesn't exist)
        cursor.execute(
            "SELECT amount FROM budgets WHERE category = ? COLLATE NOCASE",
            (source_category,)
        )
        source_budget = cursor.fetchone()
        
        budget_count = 0
        if source_budget:
            source_amount = source_budget[0]
            
            # Check if target budget exists
            cursor.execute(
                "SELECT amount FROM budgets WHERE category = ? COLLATE NOCASE",
                (target_category,)
            )
            target_budget = cursor.fetchone()
            
            if target_budget:
                # Add amounts
                new_amount = target_budget[0] + source_amount
                cursor.execute(
                    "UPDATE budgets SET amount = ? WHERE category = ? COLLATE NOCASE",
                    (new_amount, target_category)
                )
            else:
                # Create new budget with source amount
                cursor.execute(
                    "INSERT INTO budgets (category, amount) VALUES (?, ?)",
                    (target_category, source_amount)
                )
            
            # Delete source budget
            cursor.execute(
                "DELETE FROM budgets WHERE category = ? COLLATE NOCASE",
                (source_category,)
            )
            budget_count = 1
        
        logger.info(
            f"Merged category '{source_category}' into '{target_category}': "
            f"{tx_count} transactions, {rules_count} rules, {budget_count} budgets"
        )
        
        return {
            'transactions': tx_count,
            'rules': rules_count,
            'budgets': budget_count
        }


def bulk_tag_transactions(
    transaction_ids: List[int],
    tags_to_add: List[str],
    create_if_missing: bool = True
) -> int:
    """
    Add tags to multiple transactions atomically.
    
    Args:
        transaction_ids: List of transaction IDs
        tags_to_add: List of tags to add
        create_if_missing: Whether to create tags if they don't exist
        
    Returns:
        Number of transactions updated
        
    Example:
        count = bulk_tag_transactions([1, 2, 3], ["urgent", "remboursement"])
    """
    with atomic_transaction() as conn:
        cursor = conn.cursor()
        
        # Normalize tags
        normalized_tags = [t.lower().strip() for t in tags_to_add if t.strip()]
        
        if not normalized_tags:
            return 0
        
        # Get current tags for all transactions
        placeholders = ', '.join(['?'] * len(transaction_ids))
        cursor.execute(
            f"SELECT id, tags FROM transactions WHERE id IN ({placeholders})",
            transaction_ids
        )
        rows = cursor.fetchall()
        
        updated = 0
        for tx_id, current_tags in rows:
            # Parse current tags
            existing = set()
            if current_tags:
                existing = set(t.strip().lower() for t in current_tags.split(',') if t.strip())
            
            # Add new tags
            new_tags = existing.union(normalized_tags)
            
            # Only update if changed
            if new_tags != existing:
                tags_str = ', '.join(sorted(new_tags))
                cursor.execute(
                    "UPDATE transactions SET tags = ? WHERE id = ?",
                    (tags_str, tx_id)
                )
                updated += 1
        
        return updated


def batch_delete_transactions(
    transaction_ids: List[int],
    create_backup: bool = True
) -> int:
    """
    Delete multiple transactions with optional backup.
    
    Args:
        transaction_ids: List of transaction IDs to delete
        create_backup: Whether to backup before deletion
        
    Returns:
        Number of transactions deleted
        
    Example:
        count = batch_delete_transactions([1, 2, 3], create_backup=True)
    """
    with atomic_transaction() as conn:
        cursor = conn.cursor()
        
        if create_backup:
            # Backup to transaction_history
            placeholders = ', '.join(['?'] * len(transaction_ids))
            cursor.execute(f"""
                INSERT INTO transaction_history 
                (action_group_id, tx_ids, prev_categories, prev_status, action_type)
                SELECT 
                    (SELECT COALESCE(MAX(action_group_id), 0) + 1 FROM transaction_history),
                    json_array({placeholders}),
                    json_group_array(category_validated),
                    json_group_array(status),
                    'delete'
                FROM transactions
                WHERE id IN ({placeholders})
            """, transaction_ids + transaction_ids)
        
        # Delete transactions
        placeholders = ', '.join(['?'] * len(transaction_ids))
        cursor.execute(
            f"DELETE FROM transactions WHERE id IN ({placeholders})",
            transaction_ids
        )
        deleted = cursor.rowcount
        
        logger.info(f"Batch deleted {deleted} transactions")
        return deleted


__all__ = [
    'atomic_transaction',
    'batch_update_transactions_with_rule',
    'batch_categorize_transactions',
    'merge_categories_atomic',
    'bulk_tag_transactions',
    'batch_delete_transactions',
]
