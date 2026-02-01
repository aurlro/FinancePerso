"""
Tag management operations.
Handles tag extraction, manipulation, and tag-related queries.
Tag management functions.
"""
import sqlite3
import pandas as pd
import streamlit as st
from modules.db.connection import get_db_connection
from modules.logger import logger


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_all_tags() -> list[str]:
    """
    Get all unique tags used in transactions.
    
    Returns:
        List of unique tag strings
        
    Note:
        Cached for 5 minutes to improve performance
    """
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT DISTINCT tags FROM transactions WHERE tags IS NOT NULL AND tags != ''", conn)
        
        # Extract and deduplicate tags
        all_tags = set()
        for tags_str in df['tags']:
            if tags_str:
                tags = [t.strip() for t in tags_str.split(',')]
                all_tags.update(tags)
        
        return sorted(list(all_tags))


def remove_tag_from_all_transactions(tag_to_remove: str) -> int:
    """
    Remove a specific tag from all transactions that contain it.
    
    Performs string manipulation on the comma-separated tags field to cleanly
    remove the specified tag while preserving other tags.
    
    Args:
        tag_to_remove: The exact tag to remove
        
    Returns:
        Number of transactions updated
        
    Example:
        count = remove_tag_from_all_transactions("old_tag")
        print(f"Removed tag from {count} transactions")
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Find transactions with this tag
        pattern = f"%{tag_to_remove}%"
        cursor.execute("SELECT id, tags FROM transactions WHERE tags LIKE ?", (pattern,))
        rows = cursor.fetchall()
        
        updated_count = 0
        for tx_id, tags_str in rows:
            if not tags_str:
                continue
            
            current_tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            if tag_to_remove in current_tags:
                current_tags.remove(tag_to_remove)
                new_tags_str = ", ".join(current_tags) if current_tags else ""
                cursor.execute("UPDATE transactions SET tags = ? WHERE id = ?", (new_tags_str, tx_id))
                updated_count += 1
        
        conn.commit()

    from modules.cache_manager import invalidate_tag_caches
    invalidate_tag_caches()

    logger.info(f"Removed tag '{tag_to_remove}' from {updated_count} transactions")
    return updated_count


def learn_tags_from_history() -> int:
    """
    Bootstrap suggested tags by scanning validated transactions.
    
    For each category, identifies frequently used tags and adds them to the
    'suggested_tags' list in the categories table. This helps establish
    tag suggestions for future validations.
    
    Returns:
        Number of new tags learned
        
    Example:
        count = learn_tags_from_history()
        print(f"Learned {count} new tag suggestions")
    """
    count_learned = 0
    with get_db_connection() as conn:
        # Get all tags by category
        df = pd.read_sql(
            "SELECT category_validated, tags FROM transactions WHERE status='validated' AND tags != ''",
            conn
        )
        
        cat_tags_map = {}
        
        for _, row in df.iterrows():
            cat = row['category_validated']
            if not cat or cat == 'Inconnu':
                continue
            
            tags = [t.strip() for t in row['tags'].split(',') if t.strip()]
            if cat not in cat_tags_map:
                cat_tags_map[cat] = set()
            cat_tags_map[cat].update(tags)
        
        # Update database with learned tags
        cursor = conn.cursor()
        for cat, tags in cat_tags_map.items():
            # Get existing suggested tags
            cursor.execute("SELECT id, suggested_tags FROM categories WHERE name = ?", (cat,))
            row = cursor.fetchone()
            if row:
                cat_id, existing_str = row
                existing = set([
                    t.strip() 
                    for t in str(existing_str).split(',') 
                    if t.strip() and t != 'None'
                ])
                
                # Merge with learned tags
                new_set = existing.union(tags)
                if len(new_set) > len(existing):
                    new_str = ", ".join(sorted(list(new_set)))
                    cursor.execute(
                        "UPDATE categories SET suggested_tags = ? WHERE id = ?", 
                        (new_str, cat_id)
                    )
                    count_learned += (len(new_set) - len(existing))
        
        conn.commit()
    
    logger.info(f"Learned {count_learned} new tag suggestions from history")
    return count_learned


def normalize_tags_for_transaction(tags_str: str) -> str:
    """
    Normalize a tag string (lowercase, deduplicate, sort).
    
    Args:
        tags_str: Comma-separated tag string
        
    Returns:
        Normalized tag string
        
    Example:
        normalized = normalize_tags_for_transaction("Courses, essence, Courses")
        # Returns: "courses, essence"
    """
    if not tags_str:
        return ""
    
    tags = [t.strip().lower() for t in tags_str.split(',') if t.strip()]
    return ", ".join(sorted(list(set(tags))))
