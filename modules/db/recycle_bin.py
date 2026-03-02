"""
Recycle Bin Module - Système de corbeille (soft delete)

Permet de restaurer les transactions supprimées pendant 30 jours.
Particulièrement utile pour les débutants qui ont peur de faire des erreurs.
"""

import datetime
import json

import pandas as pd

from modules.db.connection import get_db_connection
from modules.logger import logger

# Durée de conservation dans la corbeille (jours)
RETENTION_DAYS = 30


def init_recycle_bin():
    """Initialize the recycle bin table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recycle_bin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_id INTEGER NOT NULL,
                table_name TEXT NOT NULL DEFAULT 'transactions',
                data JSON NOT NULL,
                deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_by TEXT,
                expires_at TIMESTAMP,
                restored_at TIMESTAMP,
                restored BOOLEAN DEFAULT 0
            )
        """)

        # Index pour recherche rapide
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recycle_bin_original_id 
            ON recycle_bin(original_id, restored)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recycle_bin_expires 
            ON recycle_bin(expires_at, restored)
        """)

        conn.commit()
        logger.info("Recycle bin table initialized")


def soft_delete_transaction(transaction_id: int, deleted_by: str = "user") -> bool:
    """
    Move a transaction to the recycle bin instead of deleting it permanently.

    Args:
        transaction_id: ID of the transaction to delete
        deleted_by: Identifier of who deleted the transaction

    Returns:
        True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get the transaction data
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
            row = cursor.fetchone()

            if not row:
                logger.warning(f"Transaction {transaction_id} not found for soft delete")
                return False

            # Convert row to dict
            columns = [description[0] for description in cursor.description]
            transaction_data = dict(zip(columns, row))

            # Calculate expiration date
            expires_at = datetime.datetime.now() + datetime.timedelta(days=RETENTION_DAYS)

            # Insert into recycle bin
            cursor.execute(
                """
                INSERT INTO recycle_bin (
                    original_id, table_name, data, deleted_by, expires_at
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    transaction_id,
                    "transactions",
                    json.dumps(transaction_data, default=str),
                    deleted_by,
                    expires_at.isoformat(),
                ),
            )

            # Mark transaction as deleted (soft delete in main table)
            cursor.execute(
                """
                UPDATE transactions 
                SET status = 'deleted', 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (transaction_id,),
            )

            conn.commit()
            logger.info(f"Transaction {transaction_id} moved to recycle bin")
            return True

    except Exception as e:
        logger.error(f"Error soft deleting transaction {transaction_id}: {e}")
        return False


def restore_transaction(recycle_bin_id: int) -> tuple[bool, str]:
    """
    Restore a transaction from the recycle bin.

    Args:
        recycle_bin_id: ID in the recycle_bin table

    Returns:
        Tuple of (success, message)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get the deleted transaction
            cursor.execute(
                """
                SELECT * FROM recycle_bin 
                WHERE id = ? AND restored = 0
            """,
                (recycle_bin_id,),
            )
            row = cursor.fetchone()

            if not row:
                return False, "Transaction introuvable ou déjà restaurée"

            columns = [description[0] for description in cursor.description]
            bin_data = dict(zip(columns, row))

            # Parse the original data
            original_data = json.loads(bin_data["data"])
            original_id = bin_data["original_id"]

            # Check if transaction still exists (should be marked as deleted)
            cursor.execute("SELECT status FROM transactions WHERE id = ?", (original_id,))
            existing = cursor.fetchone()

            if existing and existing[0] != "deleted":
                return False, "La transaction existe déjà et n'est pas supprimée"

            # Restore the transaction
            if existing:
                # Update existing row
                cursor.execute(
                    """
                    UPDATE transactions 
                    SET status = 'pending',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (original_id,),
                )
            else:
                # Re-insert (shouldn't happen normally)
                # Build INSERT query from original_data
                fields = []
                values = []
                placeholders = []

                for key, value in original_data.items():
                    if key != "id":  # Skip ID, keep original
                        fields.append(key)
                        values.append(value)
                        placeholders.append("?")

                query = f"""
                    INSERT INTO transactions (id, {', '.join(fields)})
                    VALUES (?, {', '.join(placeholders)})
                """
                cursor.execute(query, [original_id] + values)

            # Mark as restored in recycle bin
            cursor.execute(
                """
                UPDATE recycle_bin 
                SET restored = 1,
                    restored_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (recycle_bin_id,),
            )

            conn.commit()
            logger.info(f"Transaction {original_id} restored from recycle bin")
            return True, f"Transaction restaurée avec succès (ID: {original_id})"

    except Exception as e:
        logger.error(f"Error restoring transaction from recycle bin: {e}")
        return False, f"Erreur lors de la restauration: {str(e)}"


def get_recycle_bin_contents(table_name: str = "transactions", limit: int = 50) -> pd.DataFrame:
    """
    Get contents of the recycle bin.

    Args:
        table_name: Filter by table name
        limit: Maximum number of rows to return

    Returns:
        DataFrame with deleted items
    """
    try:
        with get_db_connection() as conn:
            query = """
                SELECT 
                    rb.id as recycle_id,
                    rb.original_id,
                    rb.table_name,
                    rb.deleted_at,
                    rb.deleted_by,
                    rb.expires_at,
                    json_extract(rb.data, '$.label') as label,
                    json_extract(rb.data, '$.amount') as amount,
                    json_extract(rb.data, '$.date') as date,
                    json_extract(rb.data, '$.category_validated') as category
                FROM recycle_bin rb
                WHERE rb.table_name = ?
                    AND rb.restored = 0
                    AND (rb.expires_at IS NULL OR rb.expires_at > datetime('now'))
                ORDER BY rb.deleted_at DESC
                LIMIT ?
            """
            return pd.read_sql(query, conn, params=(table_name, limit))

    except Exception as e:
        logger.error(f"Error getting recycle bin contents: {e}")
        return pd.DataFrame()


def purge_expired_items() -> int:
    """
    Permanently delete items that have exceeded the retention period.

    Returns:
        Number of items purged
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM recycle_bin
                WHERE expires_at < datetime('now')
                    AND restored = 0
            """)

            purged = cursor.rowcount
            conn.commit()

            if purged > 0:
                logger.info(f"Purged {purged} expired items from recycle bin")

            return purged

    except Exception as e:
        logger.error(f"Error purging expired items: {e}")
        return 0


def permanently_delete(recycle_bin_id: int) -> tuple[bool, str]:
    """
    Permanently delete an item from the recycle bin.

    Args:
        recycle_bin_id: ID in the recycle_bin table

    Returns:
        Tuple of (success, message)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM recycle_bin WHERE id = ?", (recycle_bin_id,))
            conn.commit()

            logger.info(f"Permanently deleted item {recycle_bin_id} from recycle bin")
            return True, "Suppression définitive effectuée"

    except Exception as e:
        logger.error(f"Error permanently deleting item: {e}")
        return False, f"Erreur: {str(e)}"


def get_recycle_bin_count() -> int:
    """
    Get the count of active items in the recycle bin.

    Returns:
        Number of non-restored, non-expired items
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM recycle_bin 
                WHERE restored = 0 
                    AND (expires_at IS NULL OR expires_at > datetime('now'))
            """)
            return cursor.fetchone()[0] or 0
    except Exception as e:
        logger.error(f"Error getting recycle bin count: {e}")
        return 0


def hard_delete_transaction(original_id: int) -> tuple[bool, str]:
    """
    Permanently delete a transaction and its recycle bin entry.

    Args:
        original_id: Original transaction ID

    Returns:
        Tuple of (success, message)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete from recycle_bin if exists
            cursor.execute("DELETE FROM recycle_bin WHERE original_id = ?", (original_id,))

            # Delete from transactions
            cursor.execute("DELETE FROM transactions WHERE id = ?", (original_id,))

            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"Permanently deleted transaction {original_id}")
                return True, "Suppression définitive effectuée"
            else:
                return False, "Transaction non trouvée"

    except Exception as e:
        logger.error(f"Error hard deleting transaction {original_id}: {e}")
        return False, f"Erreur: {str(e)}"


def get_recycle_bin_stats() -> dict:
    """Get statistics about the recycle bin."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    COUNT(*) as total_items,
                    COUNT(CASE WHEN expires_at < datetime('now') AND restored = 0 THEN 1 END) as expired,
                    COUNT(CASE WHEN restored = 1 THEN 1 END) as restored
                FROM recycle_bin
            """)

            row = cursor.fetchone()
            return {"total_items": row[0] or 0, "expired": row[1] or 0, "restored": row[2] or 0}

    except Exception as e:
        logger.error(f"Error getting recycle bin stats: {e}")
        return {"total_items": 0, "expired": 0, "restored": 0}
