# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures for FinancePerso tests.
"""
import pytest
import sqlite3
import os
import tempfile
import streamlit as st
from datetime import datetime, date

@pytest.fixture
def temp_db():
    """
    Create a temporary test database and clean it up after test.
    """
    # Create temp file
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Set env var
    os.environ['DB_PATH'] = db_path
    
    # Clear Streamlit cache to ensure test isolation
    # This prevents get_all_transactions() from returning stale data from previous tests
    try:
        st.cache_data.clear()
    except Exception:
        pass
    
    # Initialize schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create all tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            label TEXT NOT NULL,
            amount REAL NOT NULL,
            account_label TEXT,
            original_category TEXT,
            category_validated TEXT DEFAULT 'Inconnu',
            member TEXT DEFAULT 'Inconnu',
            beneficiary TEXT DEFAULT 'Inconnu',
            card_suffix TEXT,
            tags TEXT,
            notes TEXT,
            status TEXT DEFAULT 'PENDING',
            import_date TEXT,
            dedup_hash TEXT,
            occurrence_index INTEGER DEFAULT 0,
            is_manually_ungrouped INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_group_id TEXT NOT NULL,
            tx_ids TEXT NOT NULL,
            prev_status TEXT,
            prev_category TEXT,
            prev_member TEXT,
            prev_tags TEXT,
            prev_beneficiary TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )

    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            emoji TEXT DEFAULT '🏷️',
            is_fixed INTEGER DEFAULT 0,
            suggested_tags TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            member_type TEXT DEFAULT 'HOUSEHOLD'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            category TEXT NOT NULL,
            priority INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT UNIQUE NOT NULL,
            type TEXT DEFAULT 'CHECKING'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS member_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_suffix TEXT UNIQUE NOT NULL,
            member_name TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS import_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_label TEXT NOT NULL,
            import_date TEXT NOT NULL,
            num_lines INTEGER,
            file_hash TEXT
        )
    """)
    
    # Insert default categories
    default_categories = [
        ('Alimentation', '🛒', 0, ''),
        ('Transport', '🚗', 0, ''),
        ('Logement', '🏠', 1, ''),
        ('Revenus', '💰', 1, ''),
        ('Virement Interne', '🔄', 0, ''),
        ('Hors Budget', '🚫', 0, ''),
        ('Inconnu', '❓', 0, '')
    ]
    cursor.executemany(
        "INSERT INTO categories (name, emoji, is_fixed, suggested_tags) VALUES (?, ?, ?, ?)",
        default_categories
    )
    
    # Insert default members
    default_members = [
        ('Maison', 'HOUSEHOLD'),
        ('Famille', 'HOUSEHOLD'),
        ('Inconnu', 'EXTERNAL')
    ]
    cursor.executemany(
        "INSERT INTO members (name, member_type) VALUES (?, ?)",
        default_members
    )
    
    conn.commit()
    conn.close()
    
    # Set as test database
    original_db = os.environ.get('DB_PATH')
    os.environ['DB_PATH'] = db_path
    
    yield db_path
    
    # Cleanup
    if original_db:
        os.environ['DB_PATH'] = original_db
    else:
        os.environ.pop('DB_PATH', None)
    
    try:
        os.unlink(db_path)
    except (FileNotFoundError, PermissionError, OSError) as e:
        # Ignore cleanup errors in tests
        pass

@pytest.fixture
def sample_transactions():
    """
    Sample transaction data for testing.
    """
    today = date.today().isoformat()
    return [
        {
            'date': '2024-01-15',
            'label': 'CARREFOUR MARKET',
            'amount': -45.50,
            'account_label': 'Compte Courant',
            'original_category': 'Alimentation',
            'category_validated': 'Alimentation',
            'member': 'Maison',
            'beneficiary': 'Carrefour',
            'tags': 'courses,alimentaire',
            'status': 'VALIDATED'
        },
        {
            'date': '2024-01-16',
            'label': 'SALAIRE JANVIER',
            'amount': 2500.00,
            'account_label': 'Compte Courant',
            'original_category': 'Revenus',
            'category_validated': 'Revenus',
            'member': 'Maison',
            'beneficiary': 'Employeur',
            'tags': 'salaire',
            'status': 'VALIDATED'
        },
        {
            'date': '2024-01-17',
            'label': 'TOTAL STATION',
            'amount': -60.00,
            'account_label': 'Compte Courant',
            'original_category': 'Transport',
            'category_validated': 'Inconnu',
            'member': 'Inconnu',
            'beneficiary': 'Total',
            'tags': '',
            'status': 'PENDING'
        }
    ]

@pytest.fixture
def sample_categories():
    """
    Sample category data for testing (beyond defaults).
    """
    return [
        {'name': 'Loisirs', 'emoji': '🎮', 'is_fixed': 0, 'suggested_tags': 'fun,divertissement'},
        {'name': 'Santé', 'emoji': '⚕️', 'is_fixed': 0, 'suggested_tags': 'médical,pharmacie'},
        {'name': 'Éducation', 'emoji': '📚', 'is_fixed': 0, 'suggested_tags': 'école,formation'}
    ]

@pytest.fixture
def sample_members():
    """
    Sample member data for testing (beyond defaults).
    """
    return [
        {'name': 'Alice', 'type': 'HOUSEHOLD'},
        {'name': 'Bob', 'type': 'HOUSEHOLD'},
        {'name': 'Amazon', 'type': 'EXTERNAL'}
    ]

@pytest.fixture
def db_connection(temp_db):
    """
    Create a database connection for direct queries in tests.
    """
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
