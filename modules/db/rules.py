"""
Learning rules management.
Handles pattern-based categorization rules.
"""
import pandas as pd
from modules.db.connection import get_db_connection
from modules.logger import logger


def add_learning_rule(pattern: str, category: str, priority: int = 1) -> bool:
    """
    Add or update a learning rule for automatic categorization.
    
    Args:
        pattern: Text pattern to match in transaction labels
        category: Category to assign when pattern matches
        priority: Rule priority (higher = more important). Default: 1
        
    Returns:
        True if rule was added successfully, False otherwise
        
    Example:
        add_learning_rule("CARREFOUR", "Alimentation", priority=5)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO learning_rules (pattern, category, priority) VALUES (?, ?, ?)", 
                (pattern, category, priority)
            )
            conn.commit()
            logger.info(f"Learning rule added: '{pattern}' → {category} (priority={priority})")
            return True
        except Exception as e:
            logger.error(f"Error adding rule: {e}")
            return False


def get_learning_rules() -> pd.DataFrame:
    """
    Retrieve all learning rules.
    
    Returns:
        DataFrame with columns: id, pattern, category, priority, created_at
        Sorted by creation date (most recent first)
        
    Example:
        rules = get_learning_rules()
        for _, rule in rules.iterrows():
            print(f"{rule['pattern']} → {rule['category']}")
    """
    with get_db_connection() as conn:
        return pd.read_sql(
            "SELECT * FROM learning_rules ORDER BY priority DESC, created_at DESC", 
            conn
        )


def delete_learning_rule(rule_id: int) -> bool:
    """
    Delete a learning rule by ID.
    
    Args:
        rule_id: ID of the rule to delete
        
    Returns:
        True if rule was deleted, False if it didn't exist
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM learning_rules WHERE id = ?", (rule_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Learning rule {rule_id} deleted")
        return deleted


def get_rules_for_category(category: str) -> pd.DataFrame:
    """
    Get all learning rules for a specific category.
    
    Args:
        category: Category name
        
    Returns:
        DataFrame with matching rules
    """
    with get_db_connection() as conn:
        return pd.read_sql(
            "SELECT * FROM learning_rules WHERE category = ? ORDER BY priority DESC",
            conn,
            params=(category,)
        )
