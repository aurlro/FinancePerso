# AGENT-012: Test Automation Engineer

## 🎯 Mission

Ingénieur en automatisation des tests pour FinancePerso. Responsable de la stratégie de test, de la couverture de code, et de la qualité logicielle. Garant de la fiabilité du codebase à travers les tests unitaires, d'intégration, et end-to-end.

---

## 📚 Contexte: Stratégie de Test

### Philosophie
> "Un code non testé est un code qui ne fonctionne pas."

### Pyramide de Test

```
                    ╱╲
                   ╱  ╲
                  ╱ E2E╲         ← 10% - Tests end-to-end (Playwright)
                 ╱────────╲
                ╱          ╲
               ╱ Integration ╲    ← 30% - Tests d'intégration
              ╱────────────────╲
             ╱                  ╲
            ╱     Unit Tests      ╲  ← 60% - Tests unitaires (pytest)
           ╱────────────────────────╲
```

### Architecture Test

```
tests/
├── conftest.py                 # Fixtures globales pytest
├── unit/                       # Tests unitaires isolés
│   ├── test_encryption.py
│   ├── test_categorization.py
│   ├── test_transactions.py
│   └── test_analytics.py
├── integration/                # Tests d'intégration
│   ├── test_db_operations.py
│   ├── test_ai_providers.py
│   └── test_import_flow.py
├── e2e/                        # Tests end-to-end
│   └── test_user_journey.py
├── fixtures/                   # Données de test
│   ├── transactions.csv
│   ├── sample_bank_export.qif
│   └── mock_categories.json
└── __init__.py
```

---

## 🧱 Module 1: Unit Testing

### Fixtures Pytest

```python
# tests/conftest.py
"""
Configuration globale des tests pytest.
"""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Fixtures de base de données
@pytest.fixture
def temp_db_path():
    """Crée une base de données temporaire."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    yield str(db_path)
    shutil.rmtree(temp_dir)

@pytest.fixture
def db_connection(temp_db_path):
    """Connection DB isolée par test."""
    conn = sqlite3.connect(temp_db_path)
    conn.row_factory = sqlite3.Row
    
    # Créer schéma
    init_test_schema(conn)
    
    yield conn
    conn.close()

@pytest.fixture
def sample_transactions():
    """Transactions de test."""
    return [
        {
            'id': 1,
            'date': '2024-01-15',
            'label': 'SUPERMARKET PARIS',
            'amount': -45.67,
            'category_validated': 'Alimentation',
            'status': 'validated',
            'tx_hash': 'hash_001'
        },
        {
            'id': 2,
            'date': '2024-01-14',
            'label': 'SALAIRE JANVIER',
            'amount': 2500.00,
            'category_validated': 'Revenus',
            'status': 'validated',
            'tx_hash': 'hash_002'
        },
        {
            'id': 3,
            'date': '2024-01-16',
            'label': 'PHARMACIE CENTRALE',
            'amount': -23.50,
            'category_validated': 'Sante',
            'status': 'pending',
            'tx_hash': 'hash_003'
        }
    ]

@pytest.fixture
def mock_encryption_key():
    """Clé de chiffrement de test."""
    return "test_encryption_key_32_chars_long"

@pytest.fixture(autouse=True)
def reset_singletons():
    """Réinitialise les singletons avant chaque test."""
    # Reset cache Streamlit
    import streamlit as st
    st.cache_data.clear()
    st.cache_resource.clear()
    yield
```

### Tests Encryption

```python
# tests/unit/test_encryption.py
"""
Tests du module de chiffrement.
"""

import pytest
from modules.encryption import FieldEncryption, encrypt_field, decrypt_field

class TestFieldEncryption:
    """Tests de la classe FieldEncryption."""
    
    def test_encrypt_decrypt_roundtrip(self, mock_encryption_key):
        """Test chiffrement/déchiffrement réversible."""
        original = "Données sensibles"
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        
        assert decrypted == original
    
    def test_encrypted_prefix(self, mock_encryption_key):
        """Vérifie que les données chiffrées ont le préfixe ENC:"""
        original = "Test data"
        encrypted = encrypt_field(original)
        
        assert encrypted.startswith("ENC:")
    
    def test_decrypt_plain_text(self, mock_encryption_key):
        """Test déchiffrement de texte non chiffré."""
        plain = "Texte en clair"
        
        # Devrait retourner tel quel sans préfixe
        result = decrypt_field(plain)
        assert result == plain
    
    def test_encrypt_empty_string(self, mock_encryption_key):
        """Test chiffrement chaîne vide."""
        encrypted = encrypt_field("")
        decrypted = decrypt_field(encrypted)
        
        assert decrypted == ""
    
    def test_encryption_deterministic(self, mock_encryption_key):
        """Vérifie que le même texte donne des résultats différents (IV aléatoire)."""
        text = "Test"
        encrypted1 = encrypt_field(text)
        encrypted2 = encrypt_field(text)
        
        # Même texte chiffré différemment
        assert encrypted1 != encrypted2
        # Mais déchiffre pareil
        assert decrypt_field(encrypted1) == decrypt_field(encrypted2)
    
    def test_decrypt_invalid_data(self, mock_encryption_key):
        """Test déchiffrement de données invalides."""
        with pytest.raises(Exception):
            decrypt_field("ENC:invalid_base64!!!")
```

### Tests Catégorisation

```python
# tests/unit/test_categorization.py
"""
Tests du moteur de catégorisation.
"""

import pytest
from modules.categorization import RuleBasedCategorizer, categorize_transaction

class TestRuleBasedCategorizer:
    """Tests du catégoriseur basé sur règles."""
    
    def test_exact_match_rule(self):
        """Test correspondance exacte."""
        rules = {'SUPERMARKET': 'Alimentation'}
        categorizer = RuleBasedCategorizer(rules)
        
        result = categorizer.categorize('SUPERMARKET PARIS', -45.0)
        
        assert result['category'] == 'Alimentation'
        assert result['confidence'] == 1.0
    
    def test_regex_rule(self):
        """Test règle regex."""
        rules = {r'PHARMACIE.*': 'Sante'}
        categorizer = RuleBasedCategorizer(rules)
        
        result = categorizer.categorize('PHARMACIE CENTRALE', -23.0)
        
        assert result['category'] == 'Sante'
    
    def test_no_match(self):
        """Test absence de correspondance."""
        rules = {'UNKNOWN': 'Category'}
        categorizer = RuleBasedCategorizer(rules)
        
        result = categorizer.categorize('RANDOM LABEL', -10.0)
        
        assert result['category'] is None
        assert result['confidence'] == 0.0
    
    def test_priority_rules(self):
        """Test priorité des règles."""
        rules = [
            {'pattern': 'CARREFOUR', 'category': 'Alimentation', 'priority': 1},
            {'pattern': '.*', 'category': 'Divers', 'priority': 0}
        ]
        categorizer = RuleBasedCategorizer(rules)
        
        result = categorizer.categorize('CARREFOUR', -30.0)
        
        assert result['category'] == 'Alimentation'
    
    def test_amount_sign_detection(self):
        """Test détection signe montant."""
        rules = {'VIREMENT': 'Revenus'}
        categorizer = RuleBasedCategorizer(rules)
        
        # Dépense négative
        result_neg = categorizer.categorize('VIREMENT EMPLOI', 2500.0)
        # Revenu positif
        result_pos = categorizer.categorize('VIREMENT EMPLOI', -50.0)
        
        assert result_neg['category'] == 'Revenus'
```

### Tests Transactions

```python
# tests/unit/test_transactions.py
"""
Tests des opérations sur transactions.
"""

import pytest
from modules.db.transactions import (
    create_transaction, 
    update_transaction,
    get_transaction_by_hash,
    calculate_tx_hash
)

class TestTransactionHash:
    """Tests de la génération de hash."""
    
    def test_hash_consistency(self):
        """Mêmes données = même hash."""
        hash1 = calculate_tx_hash('2024-01-15', 'SUPER U', -45.67, 1)
        hash2 = calculate_tx_hash('2024-01-15', 'SUPER U', -45.67, 1)
        
        assert hash1 == hash2
    
    def test_hash_uniqueness(self):
        """Données différentes = hash différent."""
        hash1 = calculate_tx_hash('2024-01-15', 'SUPER U', -45.67, 1)
        hash2 = calculate_tx_hash('2024-01-15', 'SUPER U', -45.67, 2)
        
        assert hash1 != hash2
    
    def test_hash_normalization(self):
        """Espaces et casse normalisés."""
        hash1 = calculate_tx_hash('2024-01-15', 'SUPER U', -45.67, 1)
        hash2 = calculate_tx_hash('2024-01-15', '  super u  ', -45.67, 1)
        
        assert hash1 == hash2

class TestTransactionCRUD:
    """Tests CRUD transactions."""
    
    def test_create_transaction(self, db_connection):
        """Création transaction."""
        tx_data = {
            'date': '2024-01-15',
            'label': 'TEST TRANSACTION',
            'amount': -50.00,
            'tx_hash': 'test_hash_123'
        }
        
        tx_id = create_transaction(db_connection, tx_data)
        
        assert tx_id is not None
        assert isinstance(tx_id, int)
    
    def test_duplicate_hash_rejection(self, db_connection):
        """Rejet des doublons par hash."""
        tx_data = {
            'date': '2024-01-15',
            'label': 'TEST',
            'amount': -50.00,
            'tx_hash': 'duplicate_hash'
        }
        
        create_transaction(db_connection, tx_data)
        
        # Second avec même hash doit échouer
        with pytest.raises(Exception):
            create_transaction(db_connection, tx_data)
    
    def test_update_transaction(self, db_connection, sample_transactions):
        """Mise à jour transaction."""
        # Créer puis modifier
        tx_id = create_transaction(db_connection, sample_transactions[0])
        
        updated = update_transaction(
            db_connection, 
            tx_id, 
            {'category_validated': 'Nouvelle Cat'}
        )
        
        assert updated['category_validated'] == 'Nouvelle Cat'
```

---

## 🧱 Module 2: Integration Testing

### Tests Base de Données

```python
# tests/integration/test_db_operations.py
"""
Tests d'intégration base de données.
"""

import pytest
import pandas as pd
from modules.db.transactions import get_transactions, batch_insert_transactions

class TestBatchOperations:
    """Tests des opérations batch."""
    
    def test_batch_insert(self, db_connection):
        """Insertion batch de transactions."""
        transactions = [
            {'date': f'2024-01-{i:02d}', 'label': f'TX {i}', 'amount': -i*10, 'tx_hash': f'hash_{i}'}
            for i in range(1, 101)
        ]
        
        inserted = batch_insert_transactions(db_connection, transactions)
        
        assert inserted == 100
    
    def test_transaction_rollback(self, db_connection):
        """Rollback en cas d'erreur."""
        transactions = [
            {'date': '2024-01-01', 'label': 'OK', 'amount': -10, 'tx_hash': 'hash_ok'},
            {'date': '2024-01-01', 'label': 'DUPLICATE', 'amount': -10, 'tx_hash': 'hash_ok'},  # Doublon
        ]
        
        with pytest.raises(Exception):
            batch_insert_transactions(db_connection, transactions, atomic=True)
        
        # Aucune transaction ne doit être présente
        result = get_transactions(db_connection)
        assert len(result) == 0
    
    def test_concurrent_access(self, db_connection):
        """Test accès concurrents (simulé)."""
        import threading
        
        errors = []
        
        def insert_batch(start_idx):
            try:
                transactions = [
                    {'date': '2024-01-01', 'label': f'TX {i}', 'amount': -10, 'tx_hash': f'hash_{start_idx}_{i}'}
                    for i in range(10)
                ]
                batch_insert_transactions(db_connection, transactions)
            except Exception as e:
                errors.append(e)
        
        # Lancer threads
        threads = [threading.Thread(target=insert_batch, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
```

### Tests AI Providers

```python
# tests/integration/test_ai_providers.py
"""
Tests des providers AI (avec mocking).
"""

import pytest
from unittest.mock import Mock, patch
from modules.ai.providers import GeminiProvider, OpenAIProvider, MultiProviderManager

class TestGeminiProvider:
    """Tests Gemini provider."""
    
    @patch('modules.ai.providers.requests.post')
    def test_generate_text_success(self, mock_post):
        """Génération texte réussie."""
        mock_post.return_value.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'Résultat AI'}]}}]
        }
        mock_post.return_value.status_code = 200
        
        provider = GeminiProvider(api_key='test_key')
        result = provider.generate_text('Prompt test')
        
        assert result == 'Résultat AI'
    
    @patch('modules.ai.providers.requests.post')
    def test_generate_text_api_error(self, mock_post):
        """Gestion erreur API."""
        mock_post.return_value.status_code = 429
        mock_post.return_value.json.return_value = {'error': 'Rate limited'}
        
        provider = GeminiProvider(api_key='test_key')
        
        with pytest.raises(Exception):
            provider.generate_text('Prompt test')
    
    def test_fallback_chain(self):
        """Test chaîne de fallback."""
        manager = MultiProviderManager()
        
        # Simuler premier provider down
        manager.providers['gemini'].is_available = Mock(return_value=False)
        manager.providers['openai'].generate_text = Mock(return_value='Fallback result')
        
        result = manager.generate_with_fallback('Prompt')
        
        assert result == 'Fallback result'
```

---

## 🔧 Configuration Testing

### pytest.ini

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=modules
    --cov-report=term-missing
    --cov-report=html:coverage_html
    --cov-fail-under=80
markers =
    slow: Tests lents (à skipper en mode rapide)
    integration: Tests d'intégration
    e2e: Tests end-to-end
    requires_ai: Tests nécessitant API AI (coût)
```

### Makefile Commands

```makefile
# Makefile - Section Test
.PHONY: test test-unit test-integration test-e2e coverage

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest tests/unit -v

test-integration: ## Run integration tests
	pytest tests/integration -v -m integration

test-e2e: ## Run E2E tests
	pytest tests/e2e -v -m e2e

test-fast: ## Run fast tests only (skip slow)
	pytest -m "not slow"

coverage: ## Generate coverage report
	pytest --cov=modules --cov-report=html --cov-report=term

coverage-view: coverage ## View coverage report
	open coverage_html/index.html
```

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRÊT À L'EMPLOI
