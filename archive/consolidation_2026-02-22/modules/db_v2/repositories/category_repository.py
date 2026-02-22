"""
Category Repository
===================

Repository for category CRUD operations.
"""

import sqlite3
from typing import Optional

import pandas as pd
import streamlit as st

from modules.core.events import EventBus
from modules.db.connection import build_filter_clause, get_db_connection
from modules.db_v2.base.repository import BaseRepository
from modules.db_v2.models.category import Category
from modules.logger import logger


class CategoryRepository(BaseRepository[Category]):
    """
    Repository for category operations.

    Provides CRUD operations and domain-specific queries for categories.

    Example:
        >>> repo = CategoryRepository()
        >>> category = repo.get_by_id(1)
        >>> all_names = repo.get_names()
    """

    _table = "categories"
    _entity_class = Category

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

    def get_by_id(self, entity_id: int) -> Optional[Category]:
        """
        Get category by ID.

        Args:
            entity_id: Category ID

        Returns:
            Category if found, None otherwise
        """
        with self._get_connection() as conn:
            df = pd.read_sql(
                f"SELECT * FROM {self._table} WHERE id = ?", conn, params=(entity_id,)
            )
            if df.empty:
                return None
            return Category.from_series(df.iloc[0])

    def get_by_name(self, name: str) -> Optional[Category]:
        """
        Get category by name.

        Args:
            name: Category name

        Returns:
            Category if found, None otherwise

        Example:
            >>> repo = CategoryRepository()
            >>> cat = repo.get_by_name("Alimentation")
        """
        with self._get_connection() as conn:
            df = pd.read_sql(
                f"SELECT * FROM {self._table} WHERE name = ? COLLATE NOCASE",
                conn,
                params=(name,),
            )
            if df.empty:
                return None
            return Category.from_series(df.iloc[0])

    @st.cache_data(ttl=300)
    def get_all(
        self,
        filters: Optional[dict] = None,
        order_by: str = "name",
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> pd.DataFrame:
        """
        Get all categories with optional filtering.

        Args:
            filters: Column-value pairs for filtering
            order_by: SQL ORDER BY clause
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            DataFrame with categories
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

    @st.cache_data(ttl=300)
    def get_names(self) -> list[str]:
        """
        Get list of all category names.

        Returns:
            List of category names sorted alphabetically

        Example:
            >>> repo = CategoryRepository()
            >>> names = repo.get_names()
            >>> print(names)
            ['Alimentation', 'Logement', 'Transport']

        Note:
            Cached for 5 minutes to improve performance
        """
        with self._get_connection() as conn:
            df = pd.read_sql(
                f"SELECT name FROM {self._table} ORDER BY name", conn
            )
            return df["name"].tolist()

    @st.cache_data(ttl=300)
    def get_with_emojis(self) -> dict[str, str]:
        """
        Get dictionary of categories with their emojis.

        Returns:
            Dict mapping category name to emoji

        Example:
            >>> repo = CategoryRepository()
            >>> emojis = repo.get_with_emojis()
            >>> print(emojis)
            {'Alimentation': '🍽️', 'Logement': '🏠'}

        Note:
            Cached for 5 minutes to improve performance
        """
        with self._get_connection() as conn:
            df = pd.read_sql(
                f"SELECT name, emoji FROM {self._table}", conn
            )
            return dict(zip(df["name"], df["emoji"]))

    @st.cache_data(ttl=300)
    def get_suggested_tags(self) -> dict[str, list[str]]:
        """
        Get dictionary of categories with their suggested tags.

        Returns:
            Dict mapping category name to list of suggested tags

        Example:
            >>> repo = CategoryRepository()
            >>> tags = repo.get_suggested_tags()
            >>> print(tags)
            {'Alimentation': ['courses', 'restaurant']}

        Note:
            Cached for 5 minutes to improve performance
        """
        with self._get_connection() as conn:
            df = pd.read_sql(
                f"SELECT name, suggested_tags FROM {self._table}", conn
            )
            result = {}
            for _, row in df.iterrows():
                if row["suggested_tags"]:
                    result[row["name"]] = [
                        tag.strip()
                        for tag in str(row["suggested_tags"]).split(",")
                        if tag.strip()
                    ]
                else:
                    result[row["name"]] = []
            return result

    def get_ghost_categories(self) -> list[dict]:
        """
        Get ghost categories (categories used in transactions but not in official list).

        Ghost categories are categories used in transactions but not defined in
        the categories table. Useful for detecting inconsistencies.

        Returns:
            List of dicts with keys: 'name', 'type'
            Type is 'OFFICIAL' or 'GHOST'

        Example:
            >>> repo = CategoryRepository()
            >>> cats = repo.get_ghost_categories()
            >>> ghosts = [c for c in cats if c['type'] == 'GHOST']
        """
        with self._get_connection() as conn:
            # Official categories
            official_df = pd.read_sql(
                f"SELECT name FROM {self._table}", conn
            )
            official_set = set(official_df["name"].tolist())

            # Categories actually used in transactions
            used_df = pd.read_sql(
                """
                SELECT DISTINCT category_validated FROM transactions
                WHERE category_validated IS NOT NULL AND category_validated != 'Inconnu'
                """,
                conn,
            )
            used_set = set(used_df["category_validated"].tolist())

            # Union of both
            all_names = sorted(list(official_set.union(used_set)))

            all_cats = []
            for name in all_names:
                all_cats.append(
                    {"name": name, "type": "OFFICIAL" if name in official_set else "GHOST"}
                )

            return all_cats

    def create(self, entity: Category) -> int:
        """
        Create a new category.

        Args:
            entity: Category to create

        Returns:
            ID of created category

        Raises:
            sqlite3.IntegrityError: If category name already exists

        Example:
            >>> repo = CategoryRepository()
            >>> cat = Category(name="Épargne", emoji="💰", is_fixed=True)
            >>> cat_id = repo.create(cat)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO {self._table} (name, emoji, is_fixed, suggested_tags)
                VALUES (?, ?, ?, ?)
            """,
                (
                    entity.name,
                    entity.emoji,
                    1 if entity.is_fixed else 0,
                    entity.suggested_tags,
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid

        # Clear cached data
        st.cache_data.clear()

        EventBus.emit("categories.changed", id=new_id, action="created", name=entity.name)
        logger.info(f"Category added: {entity.emoji} {entity.name}")
        return new_id

    def update(self, entity_id: int, data: dict) -> bool:
        """
        Update category fields.

        Args:
            entity_id: Category ID
            data: Field-value pairs to update

        Returns:
            True if updated, False if not found

        Example:
            >>> repo = CategoryRepository()
            >>> repo.update(1, {"emoji": "🍽️"})
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
            st.cache_data.clear()
            EventBus.emit("categories.changed", id=entity_id, action="updated")
        return updated

    def update_emoji(self, entity_id: int, emoji: str) -> bool:
        """
        Update category emoji.

        Args:
            entity_id: Category ID
            emoji: New emoji

        Returns:
            True if updated

        Example:
            >>> repo = CategoryRepository()
            >>> repo.update_emoji(1, "🍽️")
        """
        updated = self.update(entity_id, {"emoji": emoji})
        if updated:
            EventBus.emit("categories.changed", action="emoji_updated")
        return updated

    def update_fixed_status(self, entity_id: int, is_fixed: bool) -> bool:
        """
        Update category fixed status.

        Args:
            entity_id: Category ID
            is_fixed: Whether category is fixed/recurring

        Returns:
            True if updated

        Example:
            >>> repo = CategoryRepository()
            >>> repo.update_fixed_status(1, True)
        """
        updated = self.update(entity_id, {"is_fixed": 1 if is_fixed else 0})
        if updated:
            EventBus.emit("categories.changed", action="fixed_updated")
        return updated

    def update_suggested_tags(self, entity_id: int, tags: list[str]) -> bool:
        """
        Update category suggested tags.

        Args:
            entity_id: Category ID
            tags: List of tags to set

        Returns:
            True if updated

        Example:
            >>> repo = CategoryRepository()
            >>> repo.update_suggested_tags(1, ["courses", "restaurant"])
        """
        tags_str = ", ".join(sorted(tags)) if tags else None
        updated = self.update(entity_id, {"suggested_tags": tags_str})
        if updated:
            EventBus.emit("categories.changed", action="tags_updated")
        return updated

    def add_suggested_tag(self, entity_id: int, tag: str) -> bool:
        """
        Add a suggested tag to a category.

        Args:
            entity_id: Category ID
            tag: Tag to add

        Returns:
            True if tag was added, False if category not found or tag already exists

        Example:
            >>> repo = CategoryRepository()
            >>> repo.add_suggested_tag(1, "supermarché")
        """
        category = self.get_by_id(entity_id)
        if not category:
            return False

        tags = category.get_suggested_tags_list()
        if tag in tags:
            return True  # Already exists

        tags.append(tag)
        return self.update_suggested_tags(entity_id, tags)

    def delete(self, entity_id: int) -> bool:
        """
        Delete category by ID.

        Warning: This may leave transactions with orphaned category references.
        Consider using merge_categories() instead.

        Args:
            entity_id: Category ID

        Returns:
            True if deleted, False if not found

        Example:
            >>> repo = CategoryRepository()
            >>> repo.delete(1)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self._table} WHERE id = ?", (entity_id,))
            conn.commit()
            deleted = cursor.rowcount > 0

        if deleted:
            st.cache_data.clear()
            EventBus.emit("categories.changed", id=entity_id, action="deleted")
            logger.info(f"Category {entity_id} deleted")
        return deleted

    def exists(self, entity_id: int) -> bool:
        """
        Check if category exists.

        Args:
            entity_id: Category ID

        Returns:
            True if exists

        Example:
            >>> repo = CategoryRepository()
            >>> if repo.exists(1):
            ...     print("Category exists")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM {self._table} WHERE id = ?", (entity_id,)
            )
            return cursor.fetchone() is not None

    def merge_categories(self, source_name: str, target_name: str) -> dict:
        """
        Merge source category into target category.

        Transfers all transactions from source_category to target_category,
        updates learning rules, transfers budgets, and deletes the source category.

        Args:
            source_name: Category to merge from (will be deleted)
            target_name: Category to merge into (will remain)

        Returns:
            Dict with counts: {
                'transactions': int,
                'rules': int,
                'budgets_transferred': bool,
                'category_deleted': bool
            }

        Example:
            >>> repo = CategoryRepository()
            >>> result = repo.merge_categories("Courses", "Alimentation")
            >>> print(f"Merged {result['transactions']} transactions")
            >>> if result['category_deleted']:
            ...     print("Source category deleted successfully")
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Update transactions (validated category)
            cursor.execute(
                """
                UPDATE transactions
                SET category_validated = ?
                WHERE category_validated = ? COLLATE NOCASE
            """,
                (target_name, source_name),
            )
            tx_updated = cursor.rowcount

            # Update transactions (original category)
            cursor.execute(
                """
                UPDATE transactions
                SET original_category = ?
                WHERE original_category = ? COLLATE NOCASE
            """,
                (target_name, source_name),
            )

            # Update learning rules
            cursor.execute(
                """
                UPDATE learning_rules
                SET category = ?
                WHERE category = ? COLLATE NOCASE
            """,
                (target_name, source_name),
            )
            rule_count = cursor.rowcount

            # Transfer budget if exists
            budget_transferred = False
            cursor.execute(
                "SELECT amount FROM budgets WHERE category = ? COLLATE NOCASE",
                (source_name,),
            )
            source_budget = cursor.fetchone()

            if source_budget:
                source_amount = source_budget[0]

                # Check if target has a budget
                cursor.execute(
                    "SELECT amount FROM budgets WHERE category = ? COLLATE NOCASE",
                    (target_name,),
                )
                target_budget = cursor.fetchone()

                if target_budget:
                    # Add to existing budget
                    new_amount = target_budget[0] + source_amount
                    cursor.execute(
                        "UPDATE budgets SET amount = ? WHERE category = ? COLLATE NOCASE",
                        (new_amount, target_name),
                    )
                else:
                    # Create new budget entry for target
                    cursor.execute(
                        "INSERT INTO budgets (category, amount) VALUES (?, ?)",
                        (target_name, source_amount),
                    )

                # Delete source budget
                cursor.execute(
                    "DELETE FROM budgets WHERE category = ? COLLATE NOCASE",
                    (source_name,),
                )
                budget_transferred = True

            # Delete the source category from categories table
            cursor.execute(
                "DELETE FROM categories WHERE name = ? COLLATE NOCASE",
                (source_name,),
            )
            category_deleted = cursor.rowcount > 0

            conn.commit()

        # Clear cached data
        st.cache_data.clear()

        EventBus.emit("categories.changed", action="merged")
        logger.info(
            f"Merged '{source_name}' → '{target_name}': "
            f"{tx_updated} transactions, {rule_count} rules, "
            f"budget transferred: {budget_transferred}, "
            f"category deleted: {category_deleted}"
        )

        return {
            "transactions": tx_updated,
            "rules": rule_count,
            "budgets_transferred": budget_transferred,
            "category_deleted": category_deleted,
        }

    def count(self, filters: Optional[dict] = None) -> int:
        """
        Count categories matching filters.

        Args:
            filters: Column-value pairs for filtering

        Returns:
            Count of matching categories

        Example:
            >>> repo = CategoryRepository()
            >>> fixed_count = repo.count({"is_fixed": 1})
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
