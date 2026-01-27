"""
Database connection management.
Provides context manager for SQLite connections.
"""
import sqlite3
import os
from contextlib import contextmanager
from modules.logger import logger


# Get absolute path to the database
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "Data", "finance.db")


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    
    Ensures proper connection handling with automatic cleanup.
    
    Yields:
        sqlite3.Connection: Database connection object
        
    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions")
    """
    conn = None
    try:
        # Check for environment variable (used in tests)
        db_path = os.environ.get("DB_PATH", DB_PATH)
        conn = sqlite3.connect(db_path, timeout=10.0)
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()
