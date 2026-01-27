"""
Budget management operations.
Handles CRUD operations for category budgets.
"""
import pandas as pd
from modules.db.connection import get_db_connection
from modules.logger import logger


def set_budget(category: str, amount: float) -> None:
    """
    Set or update the budget for a category.
    
    Args:
        category: Category name
        amount: Budget amount
        
    Example:
        set_budget("Alimentation", 500.0)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", 
            (category, amount)
        )
        conn.commit()
        logger.info(f"Budget set for {category}: {amount}")


def get_budgets() -> pd.DataFrame:
    """
    Retrieve all budgets.
    
    Returns:
        DataFrame with columns: category, amount, updated_at
        Empty DataFrame if no budgets exist
        
    Example:
        budgets = get_budgets()
        print(budgets[['category', 'amount']])
    """
    with get_db_connection() as conn:
        try:
            return pd.read_sql("SELECT * FROM budgets", conn)
        except Exception as e:
            logger.warning(f"Error fetching budgets: {e}")
            return pd.DataFrame(columns=['category', 'amount'])


def delete_budget(category: str) -> bool:
    """
    Delete the budget for a specific category.
    
    Args:
        category: Category name
        
    Returns:
        True if budget was deleted, False if it didn't exist
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budgets WHERE category = ?", (category,))
        conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Budget deleted for {category}")
        return deleted
