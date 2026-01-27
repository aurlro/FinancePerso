"""
Statistics and application-level queries.
Provides high-level stats for dashboards and initialization checks.
"""
import pandas as pd
import datetime
from modules.db.connection import get_db_connection
from modules.logger import logger


def is_app_initialized() -> bool:
    """
    Check if the app has any data.
    
    Returns:
        True if at least one transaction exists, False otherwise
        
    Example:
        if not is_app_initialized():
            show_welcome_screen()
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Check for transactions table existence first to avoid error on fresh init
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'"
        )
        if not cursor.fetchone():
            return False
        
        cursor.execute("SELECT 1 FROM transactions LIMIT 1")
        return cursor.fetchone() is not None


def get_global_stats() -> dict:
    """
    Get high-level stats for the homepage dashboard.
    
    Returns:
        Dict with keys:
            - total_transactions: Total number of transactions
            - last_import: Date of last import
            - current_month_savings: Monthly savings (income - expenses)
            - current_month_rate: Savings rate percentage
            - initialized: Whether app has data
            
    Example:
        stats = get_global_stats()
        st.metric("Transactions", stats['total_transactions'])
        st.metric("Épargne", f"{stats['current_month_savings']:.2f}€")
    """
    with get_db_connection() as conn:
        try:
            # 1. Total Transactions
            df_count = pd.read_sql("SELECT COUNT(*) as c FROM transactions", conn)
            total_tx = int(df_count.iloc[0]['c'])
            
            # 2. Last Import Date
            df_last = pd.read_sql("SELECT MAX(import_date) as last_imp FROM transactions", conn)
            last_import = df_last.iloc[0]['last_imp']
            
            # 3. Current Month Savings
            today = datetime.date.today()
            month_str = today.strftime('%Y-%m')
            
            query_month = f"SELECT amount FROM transactions WHERE strftime('%Y-%m', date) = ?"
            df_curr = pd.read_sql(query_month, conn, params=(month_str,))
            
            if not df_curr.empty:
                inc = df_curr[df_curr['amount'] > 0]['amount'].sum()
                exp = abs(df_curr[df_curr['amount'] < 0]['amount'].sum())
                savings = inc - exp
                savings_rate = (savings / inc * 100) if inc > 0 else 0.0
            else:
                inc, exp, savings, savings_rate = 0.0, 0.0, 0.0, 0.0
            
            return {
                "total_transactions": total_tx,
                "last_import": last_import,
                "current_month_savings": savings,
                "current_month_rate": savings_rate,
                "initialized": True
            }
        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            return {"initialized": False}


def get_available_months() -> list[str]:
    """
    Get list of months that have transactions.
    
    Returns:
        List of month strings in 'YYYY-MM' format, sorted descending
        
    Example:
        months = get_available_months()
        # ['2026-01', '2025-12', '2025-11']
    """
    with get_db_connection() as conn:
        df = pd.read_sql(
            "SELECT DISTINCT strftime('%Y-%m', date) as month FROM transactions ORDER BY month DESC",
            conn
        )
        return df['month'].tolist()


def get_all_account_labels() -> list[str]:
    """
    Retrieve all unique account labels used in transactions.
    
    Returns:
        List of unique account names
        
    Example:
        accounts = get_all_account_labels()
        # ['Compte Principal', 'Livret A', 'Compte Joint']
    """
    with get_db_connection() as conn:
        df = pd.read_sql(
            "SELECT DISTINCT account_label FROM transactions WHERE account_label IS NOT NULL",
            conn
        )
        return df['account_label'].tolist()


def get_recent_imports(limit: int = 3) -> pd.DataFrame:
    """
    Get summary of the latest import sessions.
    
    Args:
        limit: Maximum number of import sessions to return
        
    Returns:
        DataFrame with columns: account_label, count, import_date
        
    Example:
        imports = get_recent_imports(limit=5)
        for _, imp in imports.iterrows():
            print(f"{imp['account_label']}: {imp['count']} transactions on {imp['import_date']}")
    """
    with get_db_connection() as conn:
        query = """
        SELECT account_label, COUNT(*) as count, import_date 
        FROM transactions 
        GROUP BY import_date, account_label 
        ORDER BY import_date DESC 
        LIMIT ?
        """
        return pd.read_sql(query, conn, params=(limit,))
