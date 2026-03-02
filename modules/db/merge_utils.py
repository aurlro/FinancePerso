"""
Merge utilities for database operations.
Provides atomic merge operations for categories and other entities.
"""

import sqlite3

from modules.db.connection import get_db_connection
from modules.logger import logger


def _do_merge_categories(
    conn: sqlite3.Connection,
    source_category: str,
    target_category: str,
) -> dict[str, int]:
    """
    Internal function to perform the merge operation.

    Args:
        conn: Active database connection
        source_category: Category to merge from
        target_category: Category to merge into

    Returns:
        Dict with counts
    """
    cursor = conn.cursor()

    # 1. Update transactions (validated category)
    cursor.execute(
        """
        UPDATE transactions
        SET category_validated = ?
        WHERE category_validated = ? COLLATE NOCASE
        """,
        (target_category, source_category),
    )
    tx_count = cursor.rowcount

    # 2. Update transactions (original category)
    cursor.execute(
        """
        UPDATE transactions
        SET original_category = ?
        WHERE original_category = ? COLLATE NOCASE
        """,
        (target_category, source_category),
    )

    # 3. Update learning rules
    cursor.execute(
        """
        UPDATE learning_rules
        SET category = ?
        WHERE category = ? COLLATE NOCASE
        """,
        (target_category, source_category),
    )
    rules_count = cursor.rowcount

    # 4. Transfer budget if exists
    cursor.execute(
        "SELECT amount FROM budgets WHERE category = ? COLLATE NOCASE",
        (source_category,),
    )
    row = cursor.fetchone()
    source_budget = row[0] if row else None

    budgets_count = 0
    if source_budget:
        source_amount = source_budget

        cursor.execute(
            "SELECT amount FROM budgets WHERE category = ? COLLATE NOCASE",
            (target_category,),
        )
        target_row = cursor.fetchone()

        if target_row:
            # Add budgets together
            new_amount = target_row[0] + source_amount
            cursor.execute(
                "UPDATE budgets SET amount = ? WHERE category = ? COLLATE NOCASE",
                (new_amount, target_category),
            )
        else:
            # Transfer budget
            cursor.execute(
                "INSERT INTO budgets (category, amount) VALUES (?, ?)",
                (target_category, source_amount),
            )

        cursor.execute(
            "DELETE FROM budgets WHERE category = ? COLLATE NOCASE",
            (source_category,),
        )
        budgets_count = 1

    # 5. Delete source category
    cursor.execute(
        "DELETE FROM categories WHERE name = ? COLLATE NOCASE",
        (source_category,),
    )

    return {
        "transactions": tx_count,
        "rules": rules_count,
        "budgets": budgets_count,
    }


def merge_categories_atomic(
    source_category: str,
    target_category: str,
    conn: sqlite3.Connection | None = None,
) -> dict[str, int]:
    """
    Atomically merge two categories.

    Updates all transactions, rules, and budgets in a single transaction.
    If source_category == target_category, the operation is a no-op.

    Args:
        source_category: Category to merge from (will be removed)
        target_category: Category to merge into (will remain)
        conn: Optional existing connection (for transaction reuse).
              If provided, caller is responsible for commit/rollback.

    Returns:
        Dict with counts: {'transactions': int, 'rules': int, 'budgets': int}

    Example:
        result = merge_categories_atomic("Courses", "Alimentation")
        print(f"Merged {result['transactions']} transactions")
    """
    # Handle edge case: same category
    if source_category.lower() == target_category.lower():
        logger.info(
            f"Source and target categories are the same ('{source_category}'), " "nothing to merge"
        )
        return {"transactions": 0, "rules": 0, "budgets": 0}

    if conn is None:
        # Create our own connection and transaction
        with get_db_connection() as connection:
            result = _do_merge_categories(connection, source_category, target_category)
            connection.commit()

            logger.info(
                f"Merged '{source_category}' -> '{target_category}': "
                f"{result['transactions']} transactions, {result['rules']} rules, "
                f"{result['budgets']} budgets"
            )
            return result
    else:
        # Use provided connection (caller manages transaction)
        return _do_merge_categories(conn, source_category, target_category)
