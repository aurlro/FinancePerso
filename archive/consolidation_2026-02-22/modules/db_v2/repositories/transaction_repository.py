"""
Transaction Repository
======================

Repository for transaction CRUD operations.
"""

from typing import Optional

import pandas as pd
import streamlit as st

from modules.core.events import EventBus
from modules.db.connection import build_filter_clause, get_db_connection
from modules.db_v2.base.repository import BaseRepository
from modules.db_v2.models.transaction import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    """
    Repository for transaction operations.

    Provides CRUD operations and domain-specific queries for transactions.

    Example:
        >>> repo = TransactionRepository()
        >>> tx = repo.get_by_id(1)
        >>> pending = repo.get_pending(limit=10)
    """

    _table = "transactions"
    _entity_class = Transaction

    def __init__(self, connection=None):
        """
        Initialize repository.

        Args:
            connection: Optional database connection (for Unit of Work)
        """
        self._external_conn = connection

    def _get_connection(self):
        """Get database connection (external or new)."""
        if self._external_conn:
            return self._external_conn
        return get_db_connection()

    def get_by_id(self, entity_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID.

        Args:
            entity_id: Transaction ID

        Returns:
            Transaction if found, None otherwise
        """
        with self._get_connection() as conn:
            df = pd.read_sql(
                f"SELECT * FROM {self._table} WHERE id = ?", conn, params=(entity_id,)
            )
            if df.empty:
                return None
            return Transaction.from_series(df.iloc[0])

    def get_by_hash(self, tx_hash: str) -> Optional[Transaction]:
        """
        Get transaction by hash.

        Args:
            tx_hash: Transaction hash

        Returns:
            Transaction if found, None otherwise
        """
        with self._get_connection() as conn:
            df = pd.read_sql(
                f"SELECT * FROM {self._table} WHERE tx_hash = ?",
                conn,
                params=(tx_hash,),
            )
            if df.empty:
                return None
            return Transaction.from_series(df.iloc[0])

    @st.cache_data(ttl=60)
    def get_all(
        self,
        filters: Optional[dict] = None,
        order_by: str = "date DESC",
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> pd.DataFrame:
        """
        Get all transactions with optional filtering.

        Args:
            filters: Column-value pairs for filtering
            order_by: SQL ORDER BY clause
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            DataFrame with transactions
        """
        query = f"SELECT * FROM {self._table} WHERE 1=1"
        params = []

        if filters:
            where_clause, filter_params = build_filter_clause(filters)
            query += where_clause
            params.extend(filter_params)

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"

        with self._get_connection() as conn:
            return pd.read_sql(query, conn, params=params)

    def get_pending(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get pending transactions.

        Args:
            limit: Maximum number of results

        Returns:
            DataFrame with pending transactions
        """
        return self.get_all(
            filters={"status": "pending"}, order_by="date DESC", limit=limit
        )

    def get_by_category(self, category: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get transactions by category.

        Args:
            category: Category name
            limit: Maximum number of results

        Returns:
            DataFrame with matching transactions
        """
        return self.get_all(
            filters={"category_validated": category}, order_by="date DESC", limit=limit
        )

    def get_by_member(self, member: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get transactions by member.

        Args:
            member: Member name
            limit: Maximum number of results

        Returns:
            DataFrame with matching transactions
        """
        return self.get_all(filters={"member": member}, order_by="date DESC", limit=limit)

    def create(self, entity: Transaction) -> int:
        """
        Create a new transaction.

        Args:
            entity: Transaction to create

        Returns:
            ID of created transaction
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO {self._table} 
                (date, label, amount, category, category_validated, status, 
                 member, tags, tx_hash, account_label, beneficiary, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entity.date,
                    entity.label,
                    entity.amount,
                    entity.category,
                    entity.category_validated,
                    entity.status,
                    entity.member,
                    entity.tags,
                    entity.tx_hash,
                    entity.account_label,
                    entity.beneficiary,
                    entity.notes,
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid

        EventBus.emit("transactions.changed", id=new_id, action="created")
        return new_id

    def update(self, entity_id: int, data: dict) -> bool:
        """
        Update transaction fields.

        Args:
            entity_id: Transaction ID
            data: Field-value pairs to update

        Returns:
            True if updated, False if not found
        """
        if not data:
            return False

        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [entity_id]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table} SET {set_clause} WHERE id = ?", values
            )
            conn.commit()
            updated = cursor.rowcount > 0

        if updated:
            EventBus.emit("transactions.changed", id=entity_id, action="updated")
        return updated

    def update_category(self, entity_id: int, category: str) -> bool:
        """
        Update transaction category.

        Args:
            entity_id: Transaction ID
            category: New category

        Returns:
            True if updated
        """
        return self.update(
            entity_id, {"category": category, "category_validated": category}
        )

    def update_tags(self, entity_id: int, tags: list[str]) -> bool:
        """
        Update transaction tags.

        Args:
            entity_id: Transaction ID
            tags: List of tags

        Returns:
            True if updated
        """
        tags_str = ", ".join(tags) if tags else None
        return self.update(entity_id, {"tags": tags_str})

    def update_status(self, entity_id: int, status: str) -> bool:
        """
        Update transaction status.

        Args:
            entity_id: Transaction ID
            status: New status (pending, validated)

        Returns:
            True if updated
        """
        return self.update(entity_id, {"status": status})

    def delete(self, entity_id: int) -> bool:
        """
        Delete transaction by ID.

        Args:
            entity_id: Transaction ID

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self._table} WHERE id = ?", (entity_id,))
            conn.commit()
            deleted = cursor.rowcount > 0

        if deleted:
            EventBus.emit("transactions.changed", id=entity_id, action="deleted")
        return deleted

    def exists(self, entity_id: int) -> bool:
        """
        Check if transaction exists.

        Args:
            entity_id: Transaction ID

        Returns:
            True if exists
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM {self._table} WHERE id = ?", (entity_id,)
            )
            return cursor.fetchone() is not None

    def exists_by_hash(self, tx_hash: str) -> bool:
        """
        Check if transaction exists by hash.

        Args:
            tx_hash: Transaction hash

        Returns:
            True if exists
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM {self._table} WHERE tx_hash = ?", (tx_hash,)
            )
            return cursor.fetchone() is not None

    def count(self, filters: Optional[dict] = None) -> int:
        """
        Count transactions matching filters.

        Args:
            filters: Column-value pairs for filtering

        Returns:
            Count of matching transactions
        """
        query = f"SELECT COUNT(*) FROM {self._table} WHERE 1=1"
        params = []

        if filters:
            where_clause, filter_params = build_filter_clause(filters)
            query += where_clause
            params.extend(filter_params)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()[0]

    def bulk_create(self, entities: list[Transaction]) -> int:
        """
        Create multiple transactions.

        Args:
            entities: List of transactions

        Returns:
            Number of transactions created
        """
        if not entities:
            return 0

        with self._get_connection() as conn:
            cursor = conn.cursor()

            data = [
                (
                    tx.date,
                    tx.label,
                    tx.amount,
                    tx.category,
                    tx.category_validated,
                    tx.status,
                    tx.member,
                    tx.tags,
                    tx.tx_hash,
                    tx.account_label,
                    tx.beneficiary,
                    tx.notes,
                )
                for tx in entities
            ]

            cursor.executemany(
                f"""
                INSERT INTO {self._table} 
                (date, label, amount, category, category_validated, status,
                 member, tags, tx_hash, account_label, beneficiary, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                data,
            )
            conn.commit()
            count = cursor.rowcount

        EventBus.emit("transactions.batch_changed", count=count)
        return count

    def bulk_update_status(self, entity_ids: list[int], status: str) -> int:
        """
        Update status for multiple transactions.

        Args:
            entity_ids: List of transaction IDs
            status: New status

        Returns:
            Number of transactions updated
        """
        if not entity_ids:
            return 0

        placeholders = ", ".join(["?"] * len(entity_ids))

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self._table} 
                SET status = ? 
                WHERE id IN ({placeholders})
            """,
                [status] + entity_ids,
            )
            conn.commit()
            updated = cursor.rowcount

        if updated:
            EventBus.emit("transactions.batch_changed", ids=entity_ids, action="updated")
        return updated

    def bulk_delete(self, entity_ids: list[int]) -> int:
        """
        Delete multiple transactions.

        Args:
            entity_ids: List of transaction IDs

        Returns:
            Number of transactions deleted
        """
        if not entity_ids:
            return 0

        placeholders = ", ".join(["?"] * len(entity_ids))

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self._table} WHERE id IN ({placeholders})",
                entity_ids,
            )
            conn.commit()
            deleted = cursor.rowcount

        if deleted:
            EventBus.emit("transactions.batch_changed", ids=entity_ids, action="deleted")
        return deleted
