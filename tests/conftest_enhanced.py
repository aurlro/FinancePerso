"""
Fixtures de test améliorées pour FinancePerso.
À fusionner avec conftest.py existant.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
import streamlit as st


@pytest.fixture
def sample_transactions_df():
    """
    DataFrame de transactions de test complet.
    Couvre tous les cas : revenus, dépenses, remboursements, virements internes.
    """
    data = {
        'id': ['tx_001', 'tx_002', 'tx_003', 'tx_004', 'tx_005', 'tx_006', 'tx_007'],
        'date': [
            '2026-01-15', '2026-01-14', '2026-01-13', 
            '2026-01-12', '2026-01-11', '2026-01-10', '2026-01-09'
        ],
        'label': [
            'SALAIRE JANVIER',
            'CARREFOU PARIS',
            'REMB MUTUELLE',
            'VIR SEPA AURELIEN',
            'EDF PRELEVEMENT',
            'NETFLIX SUBSCRIPTION',
            'LIVRAISON UBEREATS'
        ],
        'amount': [2500.00, -45.20, 25.50, -500.00, -78.00, -15.99, -23.50],
        'category_validated': [
            'Salaire',
            'Alimentation', 
            'Remboursement',
            'Virement Interne',
            'Factures',
            'Abonnements',
            'Alimentation'
        ],
        'account_label': ['Compte Principal'] * 7,
        'member': ['Moi'] * 7,
        'status': ['validated'] * 7,
        'tags': ['', '', 'Santé', '', 'Energie', 'Streaming', 'Livraison']
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_income_transactions():
    """Transactions de revenus uniquement."""
    return pd.DataFrame({
        'id': ['inc_001', 'inc_002'],
        'amount': [2500.00, 150.00],
        'category_validated': ['Salaire', 'Remboursement'],
        'date': ['2026-01-15', '2026-01-14'],
    })


@pytest.fixture
def sample_expense_transactions():
    """Transactions de dépenses uniquement."""
    return pd.DataFrame({
        'id': ['exp_001', 'exp_002', 'exp_003', 'exp_004'],
        'amount': [-45.20, -78.00, -15.99, -23.50],
        'category_validated': ['Alimentation', 'Factures', 'Abonnements', 'Alimentation'],
        'date': ['2026-01-14', '2026-01-12', '2026-01-10', '2026-01-09'],
    })


@pytest.fixture
def mock_session_state():
    """Mock de st.session_state pour les tests."""
    state = {}
    
    def mock_get(key, default=None):
        return state.get(key, default)
    
    def mock_set(key, value):
        state[key] = value
    
    return MagicMock(
        get=mock_get,
        __setitem__=lambda s, k, v: mock_set(k, v),
        __getitem__=lambda s, k: state[k] if k in state else None,
        __contains__=lambda s, k: k in state
    )


@pytest.fixture
def empty_dataframe():
    """DataFrame vide avec les bonnes colonnes."""
    return pd.DataFrame(columns=[
        'id', 'date', 'label', 'amount', 'category_validated',
        'account_label', 'member', 'status', 'tags'
    ])


@pytest.fixture
def inconsistent_transactions_df():
    """
    Transactions avec incohérences montant/catégorie.
    Pour tester la détection d'erreurs.
    """
    return pd.DataFrame({
        'id': ['bad_001', 'bad_002', 'good_001'],
        'date': ['2026-01-15'] * 3,
        'label': ['Salaire erroné', 'Alimentation erronée', 'Transaction OK'],
        'amount': [-2500.00, 45.20, -30.00],  # Salaire négatif = erreur
        'category_validated': ['Salaire', 'Alimentation', 'Transport'],
    })


@pytest.fixture
def sample_categories():
    """Liste de catégories de test."""
    return [
        'Alimentation',
        'Transport', 
        'Logement',
        'Santé',
        'Salaire',
        'Remboursement',
        'Virement Interne',
        'Loisirs'
    ]


@pytest.fixture
def sample_budgets_df():
    """DataFrame de budgets de test."""
    return pd.DataFrame({
        'category': ['Alimentation', 'Transport', 'Loisirs'],
        'amount': [500.0, 200.0, 100.0],
        'updated_at': ['2026-01-01'] * 3
    })


# ============================================================================
# Fixtures pour les tests d'intégration
# ============================================================================

@pytest.fixture(scope="function")
def clean_database(tmp_path):
    """
    Base de données SQLite temporaire propre pour chaque test.
    """
    import sqlite3
    from modules.db.migrations import init_db
    
    db_path = tmp_path / "test.db"
    
    # Override DB path
    import os
    original_db = os.environ.get('DB_PATH')
    os.environ['DB_PATH'] = str(db_path)
    
    # Initialize
    init_db()
    
    conn = sqlite3.connect(str(db_path))
    
    yield conn
    
    # Cleanup
    conn.close()
    if original_db:
        os.environ['DB_PATH'] = original_db
    else:
        del os.environ['DB_PATH']


@pytest.fixture
def populated_database(clean_database):
    """Base de données avec données de test."""
    conn = clean_database
    cursor = conn.cursor()
    
    # Insert test transactions
    transactions = [
        ('2026-01-15', 'SALAIRE', 2500.00, 'Salaire', 'validated'),
        ('2026-01-14', 'CARREFOUR', -45.20, 'Alimentation', 'validated'),
        ('2026-01-13', 'EDF', -78.00, 'Factures', 'validated'),
    ]
    
    cursor.executemany(
        """INSERT INTO transactions (date, label, amount, category_validated, status)
           VALUES (?, ?, ?, ?, ?)""",
        transactions
    )
    
    conn.commit()
    return conn


# ============================================================================
# Fixtures pour les tests UI
# ============================================================================

@pytest.fixture
def mock_streamlit(monkeypatch):
    """Mock complet de Streamlit pour les tests UI."""
    
    class MockSt:
        def __init__(self):
            self.session_state = {}
            self.calls = []
        
        def button(self, label, **kwargs):
            self.calls.append(('button', label, kwargs))
            return False
        
        def write(self, text):
            self.calls.append(('write', text))
        
        def warning(self, text):
            self.calls.append(('warning', text))
        
        def success(self, text):
            self.calls.append(('success', text))
        
        def metric(self, label, value, **kwargs):
            self.calls.append(('metric', label, value))
    
    mock = MockSt()
    
    monkeypatch.setattr(st, 'button', mock.button)
    monkeypatch.setattr(st, 'write', mock.write)
    monkeypatch.setattr(st, 'warning', mock.warning)
    monkeypatch.setattr(st, 'success', mock.success)
    monkeypatch.setattr(st, 'metric', mock.metric)
    
    return mock


# ============================================================================
# Configuration pytest
# ============================================================================

def pytest_configure(config):
    """Configuration globale des tests."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
