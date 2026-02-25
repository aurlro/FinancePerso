"""
Category management operations.
Handles CRUD operations for transaction categories and their metadata (emojis, suggested tags).
"""

import sqlite3

import pandas as pd
import streamlit as st

from modules.core.events import EventBus
from modules.db.connection import clear_db_cache, get_db_connection
from modules.logger import logger


def add_category(name: str, emoji: str = "🏷️", is_fixed: int = 0) -> bool:
    """
    Add a new category.

    Args:
        name: Category name (must be unique)
        emoji: Emoji icon for the category
        is_fixed: Whether category appears in monthly expenses (1) or variable (0)

    Returns:
        True if category was added, False if it already exists

    Example:
        add_category("Épargne", "💰", is_fixed=1)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO categories (name, emoji, is_fixed) VALUES (?, ?, ?)",
                (name, emoji, is_fixed),
            )
            conn.commit()
            logger.info(f"Category added: {emoji} {name}")
            EventBus.emit("categories.changed", action="added", name=name)
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Category '{name}' already exists")
            return False


def update_category_emoji(cat_id: int, new_emoji: str) -> None:
    """Update the emoji for a category."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE categories SET emoji = ? WHERE id = ?", (new_emoji, cat_id))
        conn.commit()

    EventBus.emit("categories.changed", action="emoji_updated")


def update_category_fixed(cat_id: int, is_fixed: int) -> None:
    """Set whether a category is fixed (monthly) or variable."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE categories SET is_fixed = ? WHERE id = ?", (is_fixed, cat_id))
        conn.commit()

    EventBus.emit("categories.changed", action="fixed_updated")
    clear_db_cache()


def update_category_suggested_tags(cat_id: int, tags_list_str: str) -> None:
    """
    Update the suggested tags for a category.

    Args:
        cat_id: Category ID
        tags_list_str: Comma-separated string of tags
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE categories SET suggested_tags = ? WHERE id = ?", (tags_list_str, cat_id)
        )
        conn.commit()

    EventBus.emit("categories.changed", action="tags_updated")


def delete_category(cat_id: int) -> None:
    """
    Delete a category.

    Warning: This may leave transactions with orphaned category references.
    Consider using merge_categories() instead.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()
        logger.info(f"Category {cat_id} deleted")

    EventBus.emit("categories.changed", action="deleted", cat_id=cat_id)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_categories() -> list[str]:
    """
    Get list of all category names.

    Returns:
        List of category names sorted alphabetically

    Note:
        Cached for 5 minutes to improve performance
    """
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT name FROM categories ORDER BY name", conn)
        return df["name"].tolist()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_categories_with_emojis() -> dict[str, str]:
    """
    Get dictionary of categories with their emojis.

    Returns:
        Dict mapping category name to emoji

    Note:
        Cached for 5 minutes to improve performance
    """
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT name, emoji FROM categories", conn)
        return dict(zip(df["name"], df["emoji"]))


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_categories_suggested_tags() -> dict[str, list[str]]:
    """
    Get dictionary of categories with their suggested tags.

    Returns:
        Dict mapping category name to list of suggested tags

    Note:
        Cached for 5 minutes to improve performance
    """
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT name, suggested_tags FROM categories", conn)
        result = {}
        for _, row in df.iterrows():
            if row["suggested_tags"]:
                result[row["name"]] = [
                    tag.strip() for tag in str(row["suggested_tags"]).split(",") if tag.strip()
                ]
            else:
                result[row["name"]] = []
        return result


@st.cache_data(ttl="1h")
def get_categories_df() -> pd.DataFrame:
    """
    Get all category data as DataFrame.

    Returns:
        DataFrame with columns: id, name, emoji, is_fixed, suggested_tags, created_at
    """
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM categories ORDER BY name", conn)


@st.cache_data(ttl="1h")
def get_all_categories_including_ghosts() -> list[dict]:
    """
    Get all categories, including 'ghost' categories.

    Ghost categories are categories used in transactions but not defined in
    the categories table. Useful for detecting inconsistencies.

    Returns:
        List of dicts with keys: 'name', 'type'
        Type is 'OFFICIAL' or 'GHOST'

    Example:
        cats = get_all_categories_including_ghosts()
        ghosts = [c for c in cats if c['type'] == 'GHOST']
    """
    with get_db_connection() as conn:
        # Official categories
        official_df = pd.read_sql("SELECT name FROM categories", conn)
        official_set = set(official_df["name"].tolist())

        # Categories actually used in transactions
        used_df = pd.read_sql(
            "SELECT DISTINCT category_validated FROM transactions "
            "WHERE category_validated IS NOT NULL AND category_validated != 'Inconnu'",
            conn,
        )
        used_set = set(used_df["category_validated"].tolist())

        # Union of both
        all_names = sorted(list(official_set.union(used_set)))

        all_cats = []
        for name in all_names:
            all_cats.append({"name": name, "type": "OFFICIAL" if name in official_set else "GHOST"})

        return all_cats


def add_tag_to_category(cat_name: str, new_tag: str) -> bool:
    """
    Add a tag to the suggested tags list of a category.

    Args:
        cat_name: Category name
        new_tag: Tag to add

    Returns:
        True if tag was added, False if category doesn't exist or tag already present
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, suggested_tags FROM categories WHERE name = ?", (cat_name,))
        row = cursor.fetchone()
        if not row:
            return False  # Category doesn't exist

        cat_id, current_tags_str = row
        current_tags = [
            t.strip() for t in str(current_tags_str).split(",") if t.strip() and t != "None"
        ]

        if new_tag not in current_tags:
            current_tags.append(new_tag)
            new_tags_str = ", ".join(sorted(current_tags))
            cursor.execute(
                "UPDATE categories SET suggested_tags = ? WHERE id = ?", (new_tags_str, cat_id)
            )
            conn.commit()
            logger.info(f"Added tag '{new_tag}' to category '{cat_name}'")
            return True

        return True  # Already exists


def merge_categories(source_category: str, target_category: str) -> dict:
    """
    Merge source category into target category.

    Transfers all transactions from source_category to target_category,
    updates learning rules, transfers budgets, and deletes the source category.

    Args:
        source_category: Category to merge from (will be deleted)
        target_category: Category to merge into (will remain)

    Returns:
        Dict with counts: {
            'transactions': int,
            'rules': int,
            'budgets_transferred': bool,
            'category_deleted': bool
        }

    Example:
        result = merge_categories("Courses", "Alimentation")
        print(f"Merged {result['transactions']} transactions")
        if result['category_deleted']:
            print("Source category deleted successfully")
    """
    from modules.db.merge_utils import merge_categories_atomic

    result = merge_categories_atomic(source_category, target_category)

    # Emit event for UI refresh
    EventBus.emit("categories.changed", action="merged")

    # Convert budget count to boolean for backward compatibility
    return {
        "transactions": result["transactions"],
        "rules": result["rules"],
        "budgets_transferred": result["budgets"] > 0,
        "category_deleted": result["transactions"] > 0 or result["rules"] > 0 or result["budgets"] > 0,
    }
