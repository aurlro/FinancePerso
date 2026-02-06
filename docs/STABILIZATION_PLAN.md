# 🏗️ Plan de Stabilisation - FinancePerso

**Objectif** : Transformer l'app en codebase enterprise-grade sans ajouter de features  
**Durée estimée** : 3-4 semaines à temps partiel  
**Métrique de succès** : Tests >80%, 0 backup dans le repo, CI verte

---

## 📊 État Actuel (Baseline)

| Métrique | Valeur | Objectif |
|----------|--------|----------|
| Fichiers Python | 181 | 120 (après nettoyage) |
| Fichiers backup | 62 | 0 |
| Fichiers test | 33 | 60+ |
| Couverture | ~40% | >80% |
| Imports inline | ~45 | 0 |
| Session state keys | ~80 dispersées | Centralisées |

---

## 🎯 Phase 1 : Fondation Tests (Semaine 1)

### 1.1 Structure des Tests
```
tests/
├── conftest.py              # Fixtures globales
├── unit/                    # Tests unitaires purs
│   ├── test_transaction_types.py
│   ├── test_categorization.py
│   └── test_validators.py
├── integration/             # Tests intégration DB
│   ├── test_db_connection.py
│   ├── test_transactions.py
│   └── test_budgets.py
├── ui/                      # Tests composants UI
│   └── test_dashboard_cleanup.py
└── e2e/                     # Tests bout-en-bout
    └── test_import_flow.py
```

### 1.2 Fixtures Essentielles
- `mock_db()` : Base de données en mémoire
- `sample_transactions()` : Jeu de données de test
- `mock_session_state()` : État de session mocké

### 1.3 Tests Prioritaires
1. **transaction_types.py** (critique - logique métier)
2. **db/stats.py** (critique - KPI)
3. **categorization.py** (critique - IA)
4. **dashboard_cleanup.py** (nouveau - à tester)

---

## 🧹 Phase 2 : Grand Ménage (Semaine 1-2)

### 2.1 Suppression des Backups
```bash
# Script à créer : scripts/cleanup_backups.py
# - Liste tous les *.backup*
# - Vérifie qu'ils sont bien identiques aux fichiers actuels
# - Archive dans legacy/ ou supprime
```

**Critères de suppression** :
- [ ] Fichier backup identique au fichier courant → Supprimer
- [ ] Fichier backup différent mais obsolète → Archiver dans `legacy/`
- [ ] Fichier backup avec code utile → Fusionner puis supprimer

### 2.2 Imports Circulaires
**Audit** : `scripts/check_imports.py`
```python
# Détecte les imports inline (dans les fonctions)
# Liste les dépendances cycliques potentielles
# Propose un ordre de refactoring
```

### 2.3 Dead Code
**Outil** : `vulture` ou `pylint --disable=all --enable=unused`
- Fonctions jamais appelées
- Variables jamais utilisées
- Imports non utilisés

---

## 🏛️ Phase 3 : Architecture (Semaine 2-3)

### 3.1 Centralisation Session State
```python
# modules/state_manager.py

class SessionStateManager:
    """Centralise TOUTES les clés de session state."""
    
    # Audit
    AUDIT_CORRECTED = "audit_corrected"
    AUDIT_HIDDEN = "audit_hidden"
    
    # Dashboard
    DASHBOARD_LAYOUT = "dashboard_layout"
    DASHBOARD_PREVIEW = "dashboard_layout_preview"
    
    # Chat
    CHAT_HISTORY = "chat_history"
    
    @classmethod
    def get(cls, key: str, default=None):
        return st.session_state.get(key, default)
    
    @classmethod
    def set(cls, key: str, value):
        st.session_state[key] = value
```

### 3.2 Standardisation des Pages
Template obligatoire pour chaque page :
```python
"""
Page X - Description courte.

Responsabilités:
- Liste des fonctions principales

Dépendances:
- modules.x.y
"""
# 1. IMPORTS (tous au niveau module)
# 2. CONSTANTES
# 3. FONCTIONS (logique métier)
# 4. MAIN
# 5. FOOTER (scroll_top, app_info)
```

### 3.3 Error Handling Centralisé
```python
# modules/error_handling.py

class AppError(Exception):
    """Exception applicative avec contexte utilisateur."""
    def __init__(self, message: str, user_message: str = None, log_level: str = "error"):
        super().__init__(message)
        self.user_message = user_message or "Une erreur est survenue"
        self.log_level = log_level

def handle_error(func):
    """Décorateur pour catching et logging standardisé."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AppError as e:
            logger.log(e.log_level, e)
            st.error(e.user_message)
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}")
            st.error("Une erreur inattendue est survenue")
    return wrapper
```

---

## 🔧 Phase 4 : Qualité Automatisée (Semaine 3-4)

### 4.1 Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.x
    hooks:
      - id: black
        
  - repo: https://github.com/PyCQA/isort
    rev: 5.x
    hooks:
      - id: isort
        
  - repo: https://github.com/PyCQA/flake8
    rev: 6.x
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--ignore=E203,W503']
        
  - repo: local
    hooks:
      - id: no-backup-files
        name: Check for backup files
        entry: bash -c 'if ls *.backup* 1> /dev/null 2>&1; then exit 1; fi'
        language: system
        
      - id: check-imports
        name: Check inline imports
        entry: python scripts/check_inline_imports.py
        language: system
```

### 4.2 CI GitHub Actions (Minimum)
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
          
      - name: Check code style
        run: |
          black --check .
          isort --check-only .
          flake8 . --max-line-length=100
          
      - name: Check for backup files
        run: |
          if find . -name "*.backup*" -type f | grep -q .; then
            echo "❌ Backup files found!"
            find . -name "*.backup*" -type f
            exit 1
          fi
          
      - name: Run tests
        run: pytest tests/ -v --cov=modules --cov-report=xml
        
      - name: Coverage report
        run: |
          coverage report --fail-under=70
```

### 4.3 Makefile
```makefile
# Makefile pour commandes standardisées

.PHONY: test lint clean backup-check install

test:
	pytest tests/ -v --cov=modules --cov-report=html

lint:
	black .
	isort .
	flake8 . --max-line-length=100

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

backup-check:
	python scripts/check_backups.py

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install
```

---

## 📈 Suivi de Progression

### Checklist Phase 1 (Tests)
- [ ] `tests/conftest.py` avec fixtures de base
- [ ] `tests/unit/test_transaction_types.py` (>90% coverage)
- [ ] `tests/unit/test_categorization.py`
- [ ] `tests/integration/test_db.py`
- [ ] Commande `make test` fonctionne

### Checklist Phase 2 (Ménage)
- [ ] 0 fichiers `*.backup*` dans le repo
- [ ] 0 imports inline dans `modules/`
- [ ] Dead code supprimé (vulture clean)
- [ ] Fichiers <150 lignes (sauf exceptions documentées)

### Checklist Phase 3 (Architecture)
- [ ] `SessionStateManager` implémenté et utilisé
- [ ] Toutes les pages suivent le template standard
- [ ] Error handling centralisé
- [ ] Pas d'imports circulaires détectés

### Checklist Phase 4 (CI)
- [ ] Pre-commit hooks installés
- [ ] GitHub Actions verte
- [ ] Coverage >70% minimum
- [ ] 0 backup files en CI

---

## 🚀 Prochaines Actions Immédiates

1. **Créer les fixtures de test** (je peux le faire maintenant)
2. **Script de nettoyage des backups** (je peux le faire maintenant)
3. **Auditer les imports** (je peux le faire maintenant)

Quel fichier veux-tu que je crée en premier ?