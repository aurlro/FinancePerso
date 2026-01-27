"""
Tests for migrations.py module.
"""
import pytest
import sqlite3
from modules.db.migrations import init_db

class TestMigrations:
    """Tests for database migrations."""
    
    def test_init_db_fresh_db(self, temp_db):
        """Test initializing fresh database."""
        # Initialize DB (runs all migrations)
        init_db()
        
        # Verify tables exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='transactions'
        """)
        assert cursor.fetchone() is not None
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='categories'
        """)
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_idempotent_init_db(self, temp_db):
        """Test that running init_db multiple times is safe."""
        # First run
        init_db()
        
        # Second run should not error
        init_db()
    
    def test_migration_adds_columns(self, temp_db, db_connection):
        """Test that init_db ensures columns exist."""
        init_db()
        
        cursor = db_connection.cursor()
        
        # Check transactions table has new columns
        cursor.execute("PRAGMA table_info(transactions)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Verify schema
        assert 'tags' in column_names
        assert 'card_suffix' in column_names
        assert 'ai_confidence' in column_names
