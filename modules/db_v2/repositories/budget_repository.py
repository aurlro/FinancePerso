"""
Budget Repository
=================

Repository for budget CRUD operations.
"""

from typing import Optional

import pandas as pd
import streamlit as st

from modules.core.events import EventBus
from modules.db.connection import build_filter_clause, get_db_connection
from modules.db_v2.base.repository import BaseRepository
from modules.db_v2.models.budget import Budget


class BudgetRepository(BaseRepository[Budget]):
    """
    Repository for budget operations.

    Provides CRUD operations and domain-specific queries for budgets.
    Budgets are unique by category name.

    Example:
        >>> repo = BudgetRepository()
        >>> budget = repo.get_by_id(1)
        >>> food_budget = repo.get_by_category("Alimentation")
    """

    _table = "budgets"
    _entity_class = Budget

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

    def get_by_id(self, entity_id: int) -> Optional[Budget]:
        """
        Get budget by ID.

        Args:
            entity_id: Budget ID

        Returns:
            Budget if found, None otherwise

        Example:
            >>> repo = BudgetRepository()
            >>> budget = repo.get_by_id(1)
            >>> if budget:
            ...     print(f"Budget: {budget.category} = {budget.amount}")
        """
        with self._get_connection() as conn:
            df = pd.read_sql(
                f"SELECT * FROM {self._table} WHERE id = ?", conn, params=(entity_id,)
            )
            if df.empty:
                return None
            return Budget.from_series(df.iloc[0])

    def get_by_category(self, category: str) -> Optional[Budget]:
        """
        Get budget by category name.

        Args:
            category: Category name

        Returns:
            Budget if found, None otherwise

        Example:
            >>> repo = BudgetRepository()
            >>> budget = repo.get_by_category("Alimentation")
            >>> if budget:
            ...     print(f"Budget: {budget.amount}")
        """
        with self._get_connection() as conn:
            df = pd.read_sql(
                f"SELECT * FROM {self._table} WHERE category = ?",
                conn,
                params=(category,),
            )
            if df.empty:
                return None
            return Budget.from_series(df.iloc[0])

    @st.cache_data(ttl=300)
    def get_all(
        self,
        filters: Optional[dict] = None,
        order_by: str = "category",
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> pd.DataFrame:
        """
        Get all budgets with optional filtering.

        Args:
            filters: Column-value pairs for filtering
            order_by: SQL ORDER BY clause
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            DataFrame with budgets

        Example:
            >>> repo = BudgetRepository()
            >>> budgets = repo.get_all(order_by="amount DESC")
            >>> print(budgets[["category", "amount"]])
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

    def create(self, entity: Budget) -> int:
        """
        Create a new budget.

        Args:
            entity: Budget to create

        Returns:
            ID of created budget

        Example:
            >>> repo = BudgetRepository()
            >>> budget = Budget(category="Alimentation", amount=500.0)
            >>> budget_id = repo.create(budget)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO {self._table} 
                (category, amount, period, alert_threshold, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    entity.category,
                    entity.amount,
                    entity.period,
                    entity.alert_threshold,
                    entity.created_at,
                    entity.updated_at,
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid

        EventBus.emit("budgets.changed", id=new_id, action="created")
        return new_id

    def update(self, entity_id: int, data: dict) -> bool:
        """
        Update budget fields.

        Args:
            entity_id: Budget ID
            data: Field-value pairs to update

        Returns:
            True if updated, False if not found

        Example:
            >>> repo = BudgetRepository()
            >>> updated = repo.update(1, {"amount": 600.0, "alert_threshold": 90.0})
        """
        if not data:
            return False

        # Always update updated_at
        if "updated_at" not in data:
            from datetime import datetime
            data["updated_at"] = datetime.now()

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
            EventBus.emit("budgets.changed", id=entity_id, action="updated")
        return updated

    def delete(self, entity_id: int) -> bool:
        """
        Delete budget by ID.

        Args:
            entity_id: Budget ID

        Returns:
            True if deleted, False if not found

        Example:
            >>> repo = BudgetRepository()
            >>> deleted = repo.delete(1)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self._table} WHERE id = ?", (entity_id,))
            conn.commit()
            deleted = cursor.rowcount > 0

        if deleted:
            EventBus.emit("budgets.changed", id=entity_id, action="deleted")
        return deleted

    def exists(self, entity_id: int) -> bool:
        """
        Check if budget exists.

        Args:
            entity_id: Budget ID

        Returns:
            True if exists

        Example:
            >>> repo = BudgetRepository()
            >>> if repo.exists(1):
            ...     print("Budget exists")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM {self._table} WHERE id = ?", (entity_id,)
            )
            return cursor.fetchone() is not None

    def set_budget_amount(self, category: str, amount: float) -> bool:
        """
        Create or update budget amount for a category.

        Uses INSERT OR REPLACE to handle the unique constraint on category.

        Args:
            category: Category name
            amount: Budget amount

        Returns:
            True if operation succeeded

        Example:
            >>> repo = BudgetRepository()
            >>> repo.set_budget_amount("Alimentation", 500.0)
            True
        """
        from datetime import datetime

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT OR REPLACE INTO {self._table} 
                (category, amount, updated_at)
                VALUES (?, ?, ?)
            """,
                (category, amount, datetime.now()),
            )
            conn.commit()
            success = cursor.rowcount > 0

        if success:
            EventBus.emit("budgets.changed", category=category, action="set")
        return success

    def delete_by_category(self, category: str) -> bool:
        """
        Delete budget by category name.

        Args:
            category: Category name

        Returns:
            True if budget was deleted, False if it didn't exist

        Example:
            >>> repo = BudgetRepository()
            >>> deleted = repo.delete_by_category("Alimentation")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self._table} WHERE category = ?", (category,)
            )
            conn.commit()
            deleted = cursor.rowcount > 0

        if deleted:
            EventBus.emit("budgets.changed", category=category, action="deleted")
        return deleted

    def get_total_budget(self) -> float:
        """
        Get sum of all budget amounts.

        Returns:
            Total budget amount

        Example:
            >>> repo = BudgetRepository()
            >>> total = repo.get_total_budget()
            >>> print(f"Total budget: {total}")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COALESCE(SUM(amount), 0) FROM {self._table}")
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0

    def get_budget_stats(self, actual_spending: dict[str, float]) -> list[dict]:
        """
        Get budget statistics with actual spending.

        Args:
            actual_spending: Dict mapping category to amount spent

        Returns:
            List of dicts with keys: category, budget, spent, remaining, percentage, alert

        Example:
            >>> repo = BudgetRepository()
            >>> spending = {"Alimentation": 450.0, "Transport": 120.0}
            >>> stats = repo.get_budget_stats(spending)
            >>> for stat in stats:
            ...     print(f"{stat['category']}: {stat['percentage']:.1f}%")
        """
        budgets = self.get_all()
        stats = []
        for _, row in budgets.iterrows():
            category = row["category"]
            budget = row["amount"]
            spent = actual_spending.get(category, 0)
            remaining = budget - spent
            percentage = (spent / budget * 100) if budget > 0 else 0
            alert_threshold = row.get("alert_threshold", 80.0)
            alert = percentage >= alert_threshold
            stats.append({
                "category": category,
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "percentage": percentage,
                "alert": alert
            })
        return stats
