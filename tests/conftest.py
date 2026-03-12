"""
Pytest configuration and shared fixtures for FinancePerso tests.
"""

import os
import sqlite3
import tempfile
from datetime import date

import pytest
import streamlit as st


@pytest.fixture(autouse=True)
def reset_encryption_singleton():
    """
    Reset the encryption singleton before each test.
    This ensures tests don't interfere with each other via the global
    encryption instance, especially when testing with/without ENCRYPTION_KEY.
    """
    # Reset the singleton instance before test
    import modules.encryption as enc_module

    enc_module._encryption_instance = None

    yield

    # Reset again after test to clean up
    enc_module._encryption_instance = None


@pytest.fixture
def temp_db():
    """
    Create a temporary test database and clean it up after test.
    """
    # Create temp file
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Set env var
    os.environ["DB_PATH"] = db_path

    # Clear Streamlit cache to ensure test isolation
    # This prevents get_all_transactions() from returning stale data from previous tests
    try:
        st.cache_data.clear()
    except Exception:
        pass

    # Initialize schema using the REAL init_db from migrations
    # DB_PATH is already set above, init_db() will use it via get_db_connection()
    from modules.db.migrations import init_db

    init_db()  # Utilise le vrai schéma de production via DB_PATH

    # Appliquer les migrations SQL depuis le dossier migrations/
    import glob

    migrations_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
    if os.path.exists(migrations_dir):
        migration_files = sorted(glob.glob(os.path.join(migrations_dir, "*.sql")))
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for migration_file in migration_files:
            with open(migration_file) as f:
                sql = f.read()
                cursor.executescript(sql)
        conn.commit()
        conn.close()

    # Insert test defaults (categories, members)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert default categories
    default_categories = [
        ("Alimentation", "🛒", 0, ""),
        ("Transport", "🚗", 0, ""),
        ("Logement", "🏠", 1, ""),
        ("Revenus", "💰", 1, ""),
        ("Virement Interne", "🔄", 0, ""),
        ("Contribution Partenaire", "🤝", 0, ""),
        ("Hors Budget", "🚫", 0, ""),
        ("Inconnu", "❓", 0, ""),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO categories (name, emoji, is_fixed, suggested_tags) VALUES (?, ?, ?, ?)",
        default_categories,
    )

    # Insert default members
    default_members = [("Maison", "HOUSEHOLD"), ("Famille", "HOUSEHOLD"), ("Inconnu", "EXTERNAL")]
    cursor.executemany(
        "INSERT OR IGNORE INTO members (name, member_type) VALUES (?, ?)", default_members
    )

    conn.commit()
    conn.close()

    # Set as test database
    original_db = os.environ.get("DB_PATH")
    os.environ["DB_PATH"] = db_path

    yield db_path

    # Cleanup
    if original_db:
        os.environ["DB_PATH"] = original_db
    else:
        os.environ.pop("DB_PATH", None)

    try:
        os.unlink(db_path)
    except (FileNotFoundError, PermissionError, OSError):
        # Ignore cleanup errors in tests
        pass


@pytest.fixture
def sample_transactions():
    """
    Sample transaction data for testing.
    """
    date.today().isoformat()
    return [
        {
            "date": "2024-01-15",
            "label": "CARREFOUR MARKET",
            "amount": -45.50,
            "account_label": "Compte Courant",
            "original_category": "Alimentation",
            "category_validated": "Alimentation",
            "member": "Maison",
            "beneficiary": "Carrefour",
            "tags": "courses,alimentaire",
            "notes": "Test note",
            "status": "validated",
        },
        {
            "date": "2024-01-16",
            "label": "SALAIRE JANVIER",
            "amount": 2500.00,
            "account_label": "Compte Courant",
            "original_category": "Revenus",
            "category_validated": "Revenus",
            "member": "Maison",
            "beneficiary": "Employeur",
            "tags": "salaire",
            "status": "validated",
        },
        {
            "date": "2024-01-17",
            "label": "TOTAL STATION",
            "amount": -60.00,
            "account_label": "Compte Courant",
            "original_category": "Transport",
            "category_validated": "Inconnu",
            "member": "Inconnu",
            "beneficiary": "Total",
            "tags": "",
            "status": "pending",
        },
    ]


@pytest.fixture
def sample_categories():
    """
    Sample category data for testing (beyond defaults).
    """
    return [
        {"name": "Loisirs", "emoji": "🎮", "is_fixed": 0, "suggested_tags": "fun,divertissement"},
        {"name": "Santé", "emoji": "⚕️", "is_fixed": 0, "suggested_tags": "médical,pharmacie"},
        {"name": "Éducation", "emoji": "📚", "is_fixed": 0, "suggested_tags": "école,formation"},
    ]


@pytest.fixture
def sample_members():
    """
    Sample member data for testing (beyond defaults).
    """
    return [
        {"name": "Alice", "type": "HOUSEHOLD"},
        {"name": "Bob", "type": "HOUSEHOLD"},
        {"name": "Amazon", "type": "EXTERNAL"},
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
