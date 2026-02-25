# AGENT-013: QA Integration Specialist

## 🎯 Mission

Spécialiste de l'assurance qualité et des tests d'intégration. Responsable des tests end-to-end, de la performance, et de la validation fonctionnelle. Garant que l'application fonctionne comme prévu dans des conditions réelles.

---

## 📚 Contexte: Stratégie QA

### Types de Tests QA

```
┌─────────────────────────────────────────────────────────────────────┐
│                      QA TESTING PYRAMID                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  E2E Tests (Playwright)                                             │
│  ├── User Journey: Import → Categorize → Analyze                   │
│  ├── Critical Path: Dashboard KPIs display                         │
│  └── Cross-browser: Chrome, Firefox, Safari                        │
│                                                                      │
│  Performance Tests                                                  │
│  ├── Load: 1000 imports simultanés                                 │
│  ├── Stress: Fichiers 10MB+                                        │
│  └── Benchmark: Query response times                               │
│                                                                      │
│  Security Tests                                                     │
│  ├── SQL Injection prevention                                      │
│  ├── XSS protection                                                │
│  └── File upload validation                                        │
│                                                                      │
│  Accessibility Tests (a11y)                                         │
│  ├── WCAG 2.1 AA compliance                                        │
│  ├── Keyboard navigation                                           │
│  └── Screen reader compatibility                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧱 Module 1: E2E Testing (Playwright)

### Configuration Playwright

```python
# tests/e2e/conftest.py
"""
Configuration Playwright pour tests E2E.
"""

import pytest
from playwright.sync_api import sync_playwright, Page, BrowserContext

@pytest.fixture(scope="session")
def browser():
    """Browser partagé entre tous les tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def context(browser):
    """Nouveau contexte par test (cookies/isolation)."""
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        record_video_dir='test-results/videos/'
    )
    yield context
    context.close()

@pytest.fixture
def page(context):
    """Nouvelle page par test."""
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture(autouse=True)
def streamlit_app():
    """Démarre l'app Streamlit pour les tests."""
    import subprocess
    import time
    
    # Démarrer Streamlit en arrière-plan
    process = subprocess.Popen(
        ['streamlit', 'run', 'app.py', '--server.port', '8501'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Attendre démarrage
    time.sleep(5)
    
    yield 'http://localhost:8501'
    
    process.terminate()
    process.wait()
```

### Tests User Journey

```python
# tests/e2e/test_user_journey.py
"""
Tests du parcours utilisateur complet.
"""

import pytest
from playwright.sync_api import Page, expect

class TestUserJourney:
    """Tests du parcours utilisateur complet."""
    
    def test_complete_import_flow(self, page: Page, streamlit_app):
        """
        Test: Import → Validation → Dashboard.
        
        Steps:
        1. Upload fichier CSV
        2. Sélectionner banque
        3. Valider mapping
        4. Vérifier transactions créées
        5. Vérifier KPIs mis à jour
        """
        # 1. Accéder à la page
        page.goto(streamlit_app)
        
        # 2. Naviguer vers Import
        page.click('text=Importer')
        
        # 3. Upload fichier
        page.set_input_files('input[type="file"]', 'tests/fixtures/sample_transactions.csv')
        
        # 4. Sélectionner banque
        page.select_option('select', 'Société Générale')
        
        # 5. Continuer
        page.click('text=Suivant')
        
        # 6. Valider mapping
        expect(page.locator('text=Mapping détecté')).to_be_visible()
        page.click('text=Valider et importer')
        
        # 7. Attendre fin import
        expect(page.locator('text=Import réussi')).to_be_visible(timeout=30000)
        
        # 8. Vérifier nombre transactions
        page.click('text=Transactions')
        expect(page.locator('text=3 transactions')).to_be_visible()
    
    def test_categorization_workflow(self, page: Page, streamlit_app):
        """
        Test: Validation et catégorisation.
        """
        page.goto(f'{streamlit_app}?page=validation')
        
        # Vérifier présence transactions en attente
        expect(page.locator('text=En attente')).to_be_visible()
        
        # Accepter suggestion AI
        page.click('[data-testid="accept-btn"]').first
        
        # Vérifier message succès
        expect(page.locator('text=Catégorie appliquée')).to_be_visible()
    
    def test_dashboard_kpis(self, page: Page, streamlit_app):
        """
        Test: Vérification des KPIs du dashboard.
        """
        page.goto(streamlit_app)
        
        # Vérifier présence KPIs
        expect(page.locator('text=Solde actuel')).to_be_visible()
        expect(page.locator('text=Dépenses du mois')).to_be_visible()
        expect(page.locator('text=Budget restant')).to_be_visible()
        
        # Vérifier graphiques Plotly
        expect(page.locator('.js-plotly-plot')).to_have_count(4)
    
    def test_navigation_flow(self, page: Page, streamlit_app):
        """
        Test: Navigation entre toutes les pages.
        """
        pages = ['home', 'import', 'validation', 'transactions', 'analytics', 'categories', 'settings']
        
        for page_name in pages:
            page.goto(f'{streamlit_app}?page={page_name}')
            
            # Vérifier pas d'erreur
            expect(page.locator('text=Error')).not_to_be_visible()
            expect(page.locator('text=Exception')).not_to_be_visible()

class TestErrorScenarios:
    """Tests des scénarios d'erreur."""
    
    def test_invalid_file_upload(self, page: Page, streamlit_app):
        """Test: Upload fichier invalide."""
        page.goto(f'{streamlit_app}?page=import')
        
        # Upload fichier texte non-CSV
        page.set_input_files('input[type="file"]', 'tests/fixtures/invalid.txt')
        
        # Vérifier message erreur
        expect(page.locator('text=Format non supporté')).to_be_visible()
    
    def test_empty_validation_queue(self, page: Page, streamlit_app):
        """Test: File validation vide."""
        # Vider les transactions en attente
        page.goto(f'{streamlit_app}?page=validation')
        
        # Vérifier message état vide
        expect(page.locator('text=Aucune transaction en attente')).to_be_visible()
    
    def test_network_error_recovery(self, page: Page, streamlit_app):
        """Test: Récupération erreur réseau (AI)."""
        # Simuler offline
        page.context.set_offline(True)
        
        page.goto(f'{streamlit_app}?page=validation')
        
        # Vérifier fallback local
        expect(page.locator('text=Mode offline')).to_be_visible()
```

---

## 🧱 Module 2: Performance Testing

### Benchmarks

```python
# tests/performance/test_performance.py
"""
Tests de performance et benchmarks.
"""

import pytest
import time
import statistics
from modules.db.transactions import get_transactions

class TestQueryPerformance:
    """Tests des performances de requêtes."""
    
    MAX_QUERY_TIME_MS = 100  # Objectif: < 100ms
    
    def test_transaction_list_performance(self, db_connection):
        """Benchmark: Liste des transactions."""
        times = []
        
        for _ in range(10):
            start = time.perf_counter()
            df = get_transactions(db_connection, limit=100)
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        print(f"Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms")
        
        assert avg_time < self.MAX_QUERY_TIME_MS, f"Query too slow: {avg_time:.2f}ms"
    
    def test_analytics_calculation_speed(self, db_connection):
        """Benchmark: Calculs analytics."""
        from modules.analytics.kpi import calculate_monthly_kpis
        
        start = time.perf_counter()
        kpis = calculate_monthly_kpis(db_connection)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert elapsed_ms < 500, f"Analytics too slow: {elapsed_ms:.2f}ms"

class TestImportPerformance:
    """Tests des performances d'import."""
    
    def test_large_file_import(self, db_connection):
        """Test: Import fichier 1000 lignes."""
        import pandas as pd
        from modules.importers.csv_importer import import_csv
        
        # Générer fichier test
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=1000),
            'label': [f'Transaction {i}' for i in range(1000)],
            'amount': [-i for i in range(1000)]
        })
        
        start = time.perf_counter()
        result = import_csv(db_connection, df, 'Test Bank')
        elapsed_s = time.perf_counter() - start
        
        # Objectif: < 5 secondes pour 1000 lignes
        assert elapsed_s < 5, f"Import too slow: {elapsed_s:.2f}s"
        assert result.imported == 1000
```

### Load Testing

```python
# tests/performance/test_load.py
"""
Tests de charge simulée.
"""

import pytest
import concurrent.futures
import requests

class TestLoad:
    """Tests de charge."""
    
    def test_concurrent_imports(self):
        """Test: Imports concurrents."""
        def import_request(i):
            files = {'file': open('tests/fixtures/sample.csv', 'rb')}
            return requests.post('http://localhost:8501/import', files=files)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(import_request, i) for i in range(10)]
            results = [f.result() for f in futures]
        
        # Tous les imports doivent réussir
        assert all(r.status_code == 200 for r in results)
```

---

## 🧱 Module 3: Security Testing

### Tests de Sécurité

```python
# tests/security/test_security.py
"""
Tests de sécurité.
"""

import pytest
from modules.encryption import encrypt_field, decrypt_field
from modules.db.transactions import create_transaction

class TestSQLInjection:
    """Tests injection SQL."""
    
    def test_sql_injection_in_label(self, db_connection):
        """Test: Protection injection dans label."""
        malicious_label = "'; DROP TABLE transactions; --"
        
        tx_data = {
            'date': '2024-01-15',
            'label': malicious_label,
            'amount': -50,
            'tx_hash': 'test_hash_secure'
        }
        
        # Doit créer sans erreur
        tx_id = create_transaction(db_connection, tx_data)
        assert tx_id is not None
        
        # Table doit toujours exister
        cursor = db_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        assert cursor.fetchone() is not None

class TestXSS:
    """Tests XSS."""
    
    def test_xss_in_transaction_label(self, db_connection):
        """Test: Protection XSS dans affichage."""
        xss_payload = "<script>alert('XSS')</script>"
        
        tx_data = {
            'date': '2024-01-15',
            'label': xss_payload,
            'amount': -50,
            'tx_hash': 'test_hash_xss'
        }
        
        create_transaction(db_connection, tx_data)
        
        # Vérifier que le payload est échappé dans l'affichage
        # (Test visuel via Playwright)
```

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRÊT À L'EMPLOI
