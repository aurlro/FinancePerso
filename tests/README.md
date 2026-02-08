# Stratégie de Tests - FinancePerso

## Structure des Tests

```
tests/
├── conftest.py              # Fixtures pytest partagées
├── README.md                # Ce fichier
│
├── essential/               # ⚡ Tests critiques (doivent TOUJOURS passer)
│   └── test_core.py         # Tests des fonctions core (DB, sécurité, métier)
│
├── unit/                    # 🧪 Tests unitaires
│   ├── test_db/             # Tests base de données
│   ├── test_ai/             # Tests IA/ML
│   ├── test_services/       # Tests services/utilitaires
│   └── test_types.py        # Tests types/transactions
│
├── integration/             # 🔗 Tests d'intégration
│   └── test_flows.py        # Tests de flux complets
│
└── e2e/                     # 🎭 Tests end-to-end (optionnel)
    └── test_app.py          # Tests Streamlit (lourds)
```

## Commandes de Test

```bash
# Tests essentiels (rapide - 5s)
pytest tests/essential/ -v

# Tests unitaires (moyen - 30s)
pytest tests/unit/ -v

# Tous les tests (complet - 2min)
pytest tests/ --cov=modules

# CI/CD (comme GitHub Actions)
pytest tests/essential tests/unit -v --tb=short
```

## Conventions

### Nommage
- `test_<fonction>_should_<comportement>.py`
- Ex: `test_save_transaction_should_create_hash.py`

### Fixtures
Mettre les fixtures dans `conftest.py` du dossier approprié.

### Mocking
- DB: Utiliser `temp_db` fixture
- IA: Mocker `ai_manager.generate_json()`
- Streamlit: Mocker `st.session_state`

## Couverture Minimale

| Module | Couverture |
|--------|------------|
| `modules/db/` | 80% |
| `modules/ai/` | 60% |
| `modules/ui/` | 40% |
| `modules/utils.py` | 90% |
