# 🤖 AGENTS.md - Guide pour Assistants IA
> **Version du projet**: `v5.2.0`
> **Langue**: Français (interface utilisateur)

Ce document est destiné aux agents IA travaillant sur le projet **FinancePerso** (alias MyFinance Companion). Il décrit l'architecture, les conventions et les bonnes pratiques du projet.

---

## 📋 Vue d'ensemble du projet

**FinancePerso** est une application web de gestion financière personnelle développée avec Streamlit. Elle offre une suite complète d'outils pour importer, catégoriser et analyser les transactions bancaires, avec une forte intégration IA.

### Fonctionnalités principales
- **Import automatique** : Importation CSV depuis les relevés bancaires (BoursoBank, CSV générique)
- **Catégorisation IA** : Classification automatique avec apprentissage progressif (multi-providers)
- **Validation rapide** : Interface avec regroupement automatique et validation en masse
- **Analyses visuelles** : Tableaux de bord interactifs et personnalisables
- **Gestion multi-membres** : Attribution des dépenses par membre du foyer avec mapping de cartes
- **Tags personnalisés** : Système de tags intelligent avec suggestions IA
- **Sauvegardes automatiques** : Protection des données avec historique de versions
- **Suite IA complète** : Détection d'anomalies, analyse de tendances, chat IA, prédictions budgétaires
- **ML Local** : Alternative 100% offline avec scikit-learn (optionnel)

---

## 🏗️ Architecture technique


- - fix: Ajoute fixture pour réinitialiser le singleton encryption entre tests
- - ci: Ajoute debug et timeout au workflow de test
- - feat: Introduce comprehensive UI feedback, error handling, and new components for empty states, tooltips, loading, and confirmation dialogs.### Stack technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Framework UI | Streamlit | 1.47.0 |
| Base de données | SQLite | - |
| Manipulation de données | Pandas | 2.3.1 |
| Visualisation | Plotly | 6.2.0 |
| IA / ML | Google GenAI / scikit-learn | 0.8.6 / optionnel |
| Variables d'environnement | python-dotenv | 1.1.1 |
| Tests | pytest + pytest-cov | 8.4.2 |
| Linting | ruff | 0.8.6 |
| Formatage | black | 25.1.0 |
| Sécurité | cryptography (AES-256) | 44.0.0 |
| Monitoring | sentry-sdk | 2.20.0 |

### Structure du projet

```
FinancePerso/
├── app.py                          # Point d'entrée principal (onboarding + dashboard)
├── pages/                          # Pages Streamlit (routing automatique par numéro)
│   ├── 1_Opérations.py            # Import et validation des transactions
│   ├── 3_Synthese.py              # Tableaux de bord et analyses
│   ├── 4_Intelligence.py          # Règles, budgets, récurrences, audit IA
│   ├── 5_Assistant.py             # Assistant IA conversationnel
│   ├── 6_Recherche.py             # Recherche globale et exploration
│   ├── 9_Configuration.py         # Paramètres système
│   ├── 10_Nouveautés.py           # Changelog interactif
│   └── 99_Système.py              # Diagnostics et maintenance
├── modules/                        # Modules métier
│   ├── ai/                        # Suite IA complète
│   │   ├── anomaly_detector.py    # Détection d'anomalies
│   │   ├── audit_engine.py        # Audit de qualité des règles
│   │   ├── budget_predictor.py    # Prédictions budgétaires
│   │   ├── category_insights.py   # Insights par catégorie
│   │   ├── conversational_assistant.py  # Chat IA
│   │   ├── rules_auditor.py       # Audit des règles d'apprentissage
│   │   ├── smart_suggestions.py   # Suggestions intelligentes (12+ types d'analyses)
│   │   ├── smart_tagger.py        # Suggestion intelligente de tags
│   │   └── trend_analyzer.py      # Analyse de tendances
│   ├── ai_manager.py              # Abstraction multi-provider IA (gestion erreurs améliorée)
│   ├── analytics.py               # Analyses et statistiques
│   ├── analytics_v2.py            # Analyse des récurrences V2
│   ├── backup_manager.py          # Gestion des sauvegardes
│   ├── cache_manager.py           # Gestion du cache
│   ├── categorization.py          # Logique de catégorisation (règles + IA + ML local)
│   ├── constants.py               # Constantes de l'application
│   ├── data_manager.py            # DEPRECATED - Compatibilité arrière
│   ├── encryption.py              # Chiffrement AES-256 des données sensibles
│   ├── error_handlers.py          # Gestion centralisée des erreurs UX
│   ├── error_tracking.py          # Intégration Sentry
│   ├── exceptions.py              # Classes d'exceptions personnalisées
│   ├── gamification.py            # Système de gamification
│   ├── ingestion.py               # Import et parsing CSV
│   ├── local_ml.py                # ML local avec scikit-learn (optionnel)
│   ├── logger.py                  # Système de logging
│   ├── notifications.py           # Système de notifications
│   ├── update_manager.py          # Gestion des mises à jour
│   ├── utils.py                   # Fonctions utilitaires
│   ├── validators.py              # Validation des entrées
│   ├── db/                        # Couche d'accès données (modulaire)
│   │   ├── connection.py          # Gestion des connexions SQLite
│   │   ├── migrations.py          # Schéma et migrations DB
│   │   ├── transactions.py        # CRUD transactions
│   │   ├── transactions_batch.py  # Opérations en batch
│   │   ├── categories.py          # Gestion des catégories
│   │   ├── members.py             # Gestion des membres
│   │   ├── rules.py               # Règles d'apprentissage
│   │   ├── budgets.py             # Gestion des budgets
│   │   ├── tags.py                # Gestion des tags
│   │   ├── stats.py               # Statistiques globales
│   │   ├── settings.py            # Paramètres utilisateur
│   │   ├── audit.py               # Audit de qualité des données
│   │   ├── dashboard_layouts.py   # Dashboards personnalisables
│   │   ├── dashboard_cleanup.py   # Nettoyage automatique
│   │   ├── maintenance.py         # Maintenance automatique
│   │   └── recurrence_feedback.py # Feedback sur récurrences
│   └── ui/                        # Composants UI
│       ├── layout.py              # Layouts réutilisables
│       ├── feedback.py            # Système de feedback visuel
│       ├── feedback_wrapper.py    # Wrapper de feedback pour actions
│       ├── global_search.py       # Recherche globale
│       ├── components/            # Composants spécifiques
│       │   ├── empty_states.py    # Empty states engageants (Score UX: 96/100)
│       │   ├── loading_states.py  # Skeletons et loading indicators
│       │   ├── confirm_dialog.py  # Dialogs de confirmation
│       │   ├── tooltips.py        # Tooltips et aide contextuelle
│       │   ├── quick_actions.py   # Actions rapides dashboard
│       │   ├── smart_actions.py   # Actions intelligentes contextuelles
│       │   └── ...
│       ├── config/                # UI de configuration
│       ├── dashboard/             # Widgets de dashboard
│       ├── validation/            # UI de validation
│       ├── assistant/             # UI de l'assistant IA
│       ├── explorer/              # UI de l'explorateur
│       ├── intelligence/          # UI Intelligence (suggestions)
│       │   └── suggestions_panel.py  # Panel suggestions intelligentes
│       └── notifications/         # UI des notifications
├── tests/                          # Tests unitaires et d'intégration
│   ├── ai/                        # Tests IA
│   ├── db/                        # Tests base de données
│   ├── ui/                        # Tests UI
│   ├── unit/                      # Tests unitaires
│   ├── conftest.py                # Fixtures pytest
│   └── test_integration.py        # Tests d'intégration
├── Data/                          # Données (non versionnées)
│   ├── finance.db                 # Base SQLite
│   ├── backups/                   # Sauvegardes automatiques
│   └── local_ml_model.pkl         # Modèle ML local (optionnel)
├── assets/                        # Ressources statiques
│   └── style.css                  # Styles CSS personnalisés
├── docs/                          # Documentation technique
├── scripts/                       # Scripts utilitaires
├── .streamlit/config.toml         # Configuration Streamlit
├── pyproject.toml                 # Configuration Black/Ruff/pytest
├── pytest.ini                     # Configuration pytest
├── requirements.txt               # Dépendances production
└── requirements-ml.txt            # Dépendances ML (optionnel)
```

---

## 🚀 Commandes de build et test

### Installation

```bash
# Cloner le dépôt
git clone <repository-url>
cd FinancePerso

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Outils de développement

# Optionnel: ML local (100% offline)
pip install -r requirements-ml.txt
```

### Configuration environnement

```bash
# Copier le template de configuration
cp .env.example .env

# Éditer .env avec vos clés API et paramètres
# - GEMINI_API_KEY ou autre provider IA
# - ENCRYPTION_KEY (générer avec: openssl rand -base64 32)
# - SENTRY_DSN (optionnel)
```

### Lancer l'application

```bash
# Mode production
streamlit run app.py

# Mode développement (rechargement automatique)
streamlit run app.py --server.runOnSave true

# Via le script macOS (si disponible)
./MyFinance.command
```

### Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture détaillée
coverage run -m pytest
coverage report
coverage html

# Tests spécifiques
pytest tests/db/test_transactions.py -v
pytest tests/ai/test_anomaly_detector.py -v
pytest tests/test_integration.py -v
```

### Linting et formatage

```bash
# Formater le code (line-length: 100)
black modules/ pages/ tests/

# Linter avec autofix
ruff check modules/ pages/ tests/ --fix

# Vérification sans modification
ruff check modules/ pages/ tests/
```

---

## 📐 Conventions de code

### Style Python

- **Longueur de ligne** : 100 caractères maximum (configuré dans pyproject.toml)
- **Version Python cible** : 3.12
- **Docstrings** : Style Google, obligatoires pour les fonctions publiques
- **Type hints** : Recommandés pour les fonctions publiques

### Conventions Streamlit

- **Clés de widgets uniques** : Utiliser le format `f"{type}_{id}"` (ex: `f"btn_ext_{group_id}"`)
- **Session state** : Toujours initialiser avec `if 'key' not in st.session_state`
- **Fragments** : Utiliser `@st.fragment` pour les listes longues (performance)
- **Cache** : Invalider avec `st.cache_data.clear()` après modification DB

### Organisation des imports

```python
# 1. Imports standard library
import os
import re
from datetime import datetime
from typing import Optional, Tuple

# 2. Imports tiers
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# 3. Imports locaux
from modules.db.connection import get_db_connection
from modules.logger import logger
from modules.utils import clean_label
```

### Gestion des erreurs

```python
from modules.exceptions import ValidationError, DatabaseError
from modules.logger import logger

try:
    risky_operation()
except (ValueError, TypeError) as e:
    logger.error(f"Operation failed: {e}")
    raise ValidationError(f"Invalid input: {e}")
```

---

## 🗄️ Schéma de base de données

### Tables principales

| Table | Description | Colonnes clés |
|-------|-------------|---------------|
| `transactions` | Opérations bancaires | id, date, label, amount, category_validated, status, member, tags, tx_hash, beneficiary, notes |
| `transaction_history` | Historique pour undo | action_group_id, tx_ids, prev_*, timestamp |
| `categories` | Catégories de dépenses | id, name, emoji, is_fixed, suggested_tags |
| `members` | Membres du foyer | id, name, member_type (HOUSEHOLD/EXTERNAL) |
| `member_mappings` | Association cartes → membres | id, card_suffix, member_name |
| `learning_rules` | Règles d'apprentissage | id, pattern, category, priority |
| `budgets` | Objectifs budgétaires | category, amount, updated_at |
| `settings` | Configuration utilisateur | key, value, description |
| `dashboard_layouts` | Layouts personnalisables | name, layout_json, is_active |
| `import_history` | Historique des imports | account_label, import_date, file_hash |

### Connexion à la base de données

```python
from modules.db.connection import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions LIMIT 10")
    results = cursor.fetchall()
```

---

## 🤖 Architecture IA

### Providers supportés

| Provider | Variable d'environnement | Configuration |
|----------|-------------------------|---------------|
| Google Gemini | `GEMINI_API_KEY` | Recommandé, gratuit, défaut |
| Ollama (local) | `OLLAMA_URL` | 100% offline |
| DeepSeek | `DEEPSEEK_API_KEY` | Bon rapport qualité/prix |
| OpenAI | `OPENAI_API_KEY` | Standard industriel |
| KIMI (Moonshot) | `KIMI_API_KEY` | Alternative chinoise |

### Configuration IA

```python
from modules.ai_manager import get_ai_provider, get_active_model_name, is_ai_available

provider = get_ai_provider()
model_name = get_active_model_name()

# Vérifier disponibilité
if is_ai_available():
    result = provider.generate_json(prompt, model_name=model_name)
```

### Modes de catégorisation

1. **AUTO** (défaut) : Local ML si disponible, sinon Cloud
2. **ML Local** : 100% offline avec scikit-learn
3. **IA Cloud** : Via API externe (meilleure précision)
4. **Règles uniquement** : Pas d'IA, uniquement règles définies

### Modules IA disponibles

```python
from modules.ai import (
    detect_amount_anomalies,      # Détection d'anomalies
    predict_budget_overruns,      # Prédictions budgétaires
    chat_with_assistant,          # Chat IA
    analyze_spending_trends,      # Analyse de tendances
    suggest_tags_for_transaction, # Suggestion de tags
    audit_rules_health            # Audit des règles
)
```

---

## 🧪 Stratégie de tests

### Organisation des tests

- **tests/db/** : Tests de la couche d'accès données
- **tests/ai/** : Tests des modules IA
- **tests/ui/** : Tests des composants UI
- **tests/unit/** : Tests unitaires
- **tests/test_integration.py** : Tests d'intégration

### Fixtures principales (conftest.py)

| Fixture | Description |
|---------|-------------|
| `temp_db` | Base de données temporaire isolée |
| `sample_transactions` | Données de transactions de test |
| `sample_categories` | Catégories de test |
| `sample_members` | Membres de test |
| `db_connection` | Connexion DB pour requêtes directes |
| `reset_encryption_singleton` | Réinitialise l'encryption entre tests |

### Exécution des tests

```bash
# Tous les tests avec rapport détaillé
pytest --cov=modules --cov-report=html --cov-report=term-missing -v

# Tests spécifiques
pytest tests/db/ -v
pytest tests/ai/ -v
pytest tests/test_integration.py::test_end_to_end_import -v
```

---

## 🔒 Sécurité et bonnes pratiques

### Gestion des secrets

- **JAMAIS** hardcoder de clés API ou données personnelles
- Utiliser `python-dotenv` pour charger les variables d'environnement
- Le fichier `.env` doit avoir les permissions 0600

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

### Chiffrement des données sensibles

Les champs sensibles (`notes`, `beneficiary`) sont chiffrés avec AES-256:

```python
from modules.encryption import encrypt_field, decrypt_field, get_encryption

# Chiffrer
encrypted = encrypt_field(sensitive_data)

# Déchiffrer
decrypted = decrypt_field(encrypted_value)

# Vérifier si actif
if get_encryption().is_enabled():
    logger.info("Chiffrement actif")
```

### Validation des entrées

```python
from modules.utils import validate_regex_pattern

is_valid, error = validate_regex_pattern(pattern)
if not is_valid:
    raise ValidationError(error)
```

### Protection XSS

```python
from modules.utils import escape_html, safe_html_template

# Échapper le HTML
safe_text = escape_html(user_input)

# Template sécurisé
safe_html = safe_html_template(
    "<div class='item'><h3>{title}</h3></div>",
    title=user_title  # Automatiquement échappé
)
```

---

## 🎨 Composants UX (Score: 95/100)

### Empty States

```python
from modules.ui.components.empty_states import (
    render_no_transactions_state,
    render_no_budgets_state,
    render_error_state
)

# Usage
render_no_transactions_state(key="dashboard_empty")
```

### Loading States

```python
from modules.ui.components.loading_states import (
    render_skeleton_card,
    loading_spinner,
    render_progress_steps
)

# Usage avec context manager
with loading_spinner("Import en cours..."):
    result = long_operation()
```

### Confirmation Dialogs

```python
from modules.ui.components.confirm_dialog import confirm_delete, confirm_dialog

# Usage
if confirm_delete("Ma catégorie", "catégorie", key="del_cat_1"):
    delete_category(category_id)
```

### Tooltips et Aide

```python
from modules.ui.components.tooltips import (
    render_info_box,
    render_contextual_help,
    IMPORT_HELP
)

# Usage
render_info_box(
    title="Bienvenue !",
    content="Commencez par importer vos données.",
    type="info"
)

render_contextual_help({"Guide": IMPORT_HELP})
```

### Gestion des Erreurs

```python
from modules.error_handlers import (
    handle_error,
    with_error_handling,
    ErrorContext
)

# Usage avec context manager
with ErrorContext("import de fichier"):
    df = load_transaction_file(file)

# Usage avec décorateur
@with_error_handling("création de catégorie", default_return=False)
def create_category(name):
    # ...
    pass
```

---

## ⚠️ Anti-patterns à éviter

| ❌ Anti-pattern | ✅ Bonne pratique |
|----------------|------------------|
| `except:` nu | `except (ValueError, TypeError) as e:` |
| Modifier session_state sans rerun | Utiliser `st.rerun()` après modification |
| Requêtes DB dans des boucles | Utiliser `bulk_*` ou `executemany` |
| Clés de widgets non-uniques | Format `f"{type}_{unique_id}"` |
| Oublier `st.cache_data.clear()` | Invalider le cache après modif DB |
| Hardcoder des données personnelles | Utiliser la table `settings` |
| Import circulaires | Structure modulaire avec imports locaux |
| `print()` en production | Utiliser `from modules.logger import logger` |

---

## 📚 Documentation complémentaire

- **docs/** : Documentation technique du projet
- **CONTRIBUTING.md** : Guide de contribution
- **CHANGELOG.md** : Historique des versions
- **README.md** : Vue d'ensemble utilisateur

---

## 🎯 Checklist avant commit

- [ ] Code formaté avec Black (`black modules/ pages/ tests/`)
- [ ] Linting OK (`ruff check modules/ pages/ tests/`)
- [ ] Tests passent (`pytest`)
- [ ] Pas de `print()` ou code debug
- [ ] Migrations DB testées (si applicable)
- [ ] Pas de données personnelles hardcodées
- [ ] Messages utilisateur en français
- [ ] Cache Streamlit invalidé si modif DB
- [ ] Docstrings ajoutées pour fonctions publiques

---

**Dernière mise à jour** : 2026-02-08
**Version du projet** : 5.1.0
**Langue principale** : Français
**Score UX** : 95/100 🌟
