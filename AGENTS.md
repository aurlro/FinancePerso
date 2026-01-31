# 🤖 AGENTS.md - Guide pour Assistants IA

> Ce document est destiné aux agents IA (Gemini, Claude, etc.) travaillant sur le projet FinancePerso.
> Il décrit l'architecture, les conventions et les bonnes pratiques du projet.

---

## 📋 Vue d'ensemble du projet

**FinancePerso** (alias MyFinance Companion) est une application web de gestion financière personnelle développée avec Streamlit.

### Fonctionnalités principales
- Import automatique de transactions CSV depuis les relevés bancaires
- Catégorisation IA des transactions avec apprentissage progressif
- Validation rapide avec regroupement automatique et validation en masse
- Analyses visuelles et tableaux de bord interactifs
- Gestion multi-membres du foyer avec mapping de cartes
- Tags personnalisés et catégories configurables
- Sauvegardes automatiques avec historique de versions
- Suite IA complète : détection d'anomalies, analyse de tendances, chat IA, prédictions budgétaires

---

## 🏗️ Architecture technique

### Stack technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Framework UI | Streamlit | 1.47.0 |
| Base de données | SQLite | - |
| Manipulation de données | Pandas | 2.3.1 |
| IA / ML | Google Generative AI | 0.8.6 |
| Visualisation | Plotly | 6.2.0 |
| Variables d'environnement | python-dotenv | 1.1.1 |
| Tests | pytest | 8.4.2 |
| Linting | ruff | 0.8.6 |
| Formatage | black | 25.1.0 |

### Structure du projet

```
FinancePerso/
├── app.py                          # Point d'entrée principal (onboarding + dashboard)
├── pages/                          # Pages Streamlit (routing automatique)
│   ├── 1_Import.py                # Import CSV de transactions
│   ├── 2_Validation.py            # Validation et catégorisation
│   ├── 3_Synthese.py              # Tableaux de bord et analyses
│   ├── 4_Recurrence.py            # Analyse des paiements récurrents
│   ├── 4_Regles.py                # Gestion des règles d'apprentissage
│   ├── 5_Assistant.py             # Assistant IA conversationnel
│   ├── 9_Configuration.py         # Paramètres système
│   ├── 10_Nouveautés.py           # Changelog interactif
│   └── 98_Tests.py                # Interface de tests
├── modules/                        # Modules métier
│   ├── ai/                        # Suite IA complète
│   │   ├── anomaly_detector.py
│   │   ├── budget_predictor.py
│   │   ├── conversational_assistant.py
│   │   ├── rules_auditor.py
│   │   ├── smart_tagger.py
│   │   └── trend_analyzer.py
│   ├── ai_manager.py              # Abstraction multi-provider IA
│   ├── analytics.py               # Analyses et statistiques
│   ├── analytics_v2.py            # Analyse des récurrences V2
│   ├── backup_manager.py          # Gestion des sauvegardes
│   ├── cache_manager.py           # Gestion du cache
│   ├── categorization.py          # Logique de catégorisation IA
│   ├── data_manager.py            # DEPRECATED - Compatibilité arrière
│   ├── exceptions.py              # Classes d'exceptions personnalisées
│   ├── ingestion.py               # Import et parsing CSV
│   ├── logger.py                  # Système de logging
│   ├── utils.py                   # Fonctions utilitaires
│   ├── db/                        # Couche d'accès données (modulaire)
│   │   ├── connection.py          # Gestion des connexions
│   │   ├── migrations.py          # Schéma et migrations
│   │   ├── transactions.py        # CRUD transactions
│   │   ├── categories.py          # Gestion des catégories
│   │   ├── members.py             # Gestion des membres
│   │   ├── rules.py               # Règles d'apprentissage
│   │   ├── budgets.py             # Gestion des budgets
│   │   ├── tags.py                # Gestion des tags
│   │   ├── stats.py               # Statistiques globales
│   │   ├── settings.py            # Paramètres utilisateur
│   │   └── audit.py               # Audit de qualité des données
│   └── ui/                        # Composants UI
│       ├── layout.py              # Layouts réutilisables
│       ├── components/            # Composants spécifiques
│       ├── config/                # UI de configuration
│       ├── dashboard/             # Widgets de dashboard
│       └── validation/            # UI de validation
├── tests/                          # Tests unitaires et d'intégration
│   ├── ai/                        # Tests IA
│   ├── db/                        # Tests base de données
│   └── ui/                        # Tests UI
├── Data/                          # Données (non versionnées)
│   ├── finance.db                 # Base SQLite
│   └── backups/                   # Sauvegardes automatiques
├── docs/                          # Documentation technique
├── scripts/                       # Scripts utilitaires
├── pyproject.toml                 # Configuration outils Python
├── pytest.ini                    # Configuration tests
├── requirements.txt              # Dépendances production
├── requirements-dev.txt          # Dépendances développement
└── .streamlit/config.toml        # Configuration Streamlit
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
pip install -r requirements-dev.txt
```

### Lancer l'application

```bash
# Mode production
streamlit run app.py

# Mode développement (rechargement automatique)
streamlit run app.py --server.runOnSave true

# Via le script macOS
./Lancer_App.command
```

### Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
coverage run -m pytest
coverage report
coverage html

# Tests spécifiques
pytest tests/db/test_transactions.py
pytest tests/test_integration.py
```

### Linting et formatage

```bash
# Formater le code
black modules/ pages/ tests/

# Linter
ruff check modules/ pages/ tests/
ruff check --fix modules/ pages/ tests/
```

---

## 📐 Conventions de code

### Style Python

- **Longueur de ligne** : 100 caractères maximum (configuré dans pyproject.toml)
- **Version Python cible** : 3.12
- **Docstrings** : Obligatoires pour toutes les fonctions publiques
- **Type hints** : Recommandés là où c'est utile

### Conventions Streamlit

- **Clés de widgets uniques** : Utiliser le format `f"{type}_{id}"` (ex: `f"btn_ext_{group_id}"`)
- **Session state** : Toujours initialiser avec `if 'key' not in st.session_state`
- **Fragments** : Utiliser `@st.fragment` pour les listes longues (performance)

### Conventions CSS

- Préfixer les classes personnalisées par `fp-` (ex: `fp-card`)
- Utiliser `data-testid` pour un ciblage robuste

### Organisation des imports

```python
# 1. Imports standard library
import os
import re
from datetime import datetime

# 2. Imports tiers
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# 3. Imports locaux
from modules.db.connection import get_db_connection
from modules.logger import logger
from modules.utils import clean_label
```

---

## 🗄️ Schéma de base de données

### Tables principales

| Table | Description | Colonnes clés |
|-------|-------------|---------------|
| `transactions` | Opérations bancaires | id, date, label, amount, category_validated, status, member, tags, tx_hash |
| `categories` | Catégories de dépenses | id, name, emoji, is_fixed, suggested_tags |
| `members` | Membres du foyer | id, name, member_type |
| `member_mappings` | Association cartes → membres | id, card_suffix, member_name |
| `learning_rules` | Règles d'apprentissage | id, pattern, category, priority |
| `budgets` | Objectifs budgétaires | category, amount |
| `settings` | Configuration utilisateur | key, value, description |
| `transaction_history` | Historique pour undo | action_group_id, tx_ids, prev_* |

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
| Google Gemini | `GEMINI_API_KEY` | Recommandé, gratuit |
| Ollama (local) | `OLLAMA_URL` | 100% offline |
| DeepSeek | `DEEPSEEK_API_KEY` | Bon rapport qualité/prix |
| OpenAI | `OPENAI_API_KEY` | Standard industriel |

### Utilisation

```python
from modules.ai_manager import get_ai_provider, get_active_model_name

provider = get_ai_provider()
model_name = get_active_model_name()

# Générer du JSON
result = provider.generate_json(prompt, model_name=model_name)

# Générer du texte
text = provider.generate_text(prompt, model_name=model_name)
```

### Modules IA disponibles

```python
from modules.ai import (
    detect_amount_anomalies,      # Détection d'anomalies
    predict_budget_overruns,      # Prédictions budgétaires
    chat_with_assistant,          # Chat IA
    analyze_spending_trends,      # Analyse de tendances
    suggest_tags_for_transaction  # Suggestion de tags
)
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

### Validation des entrées

- Toujours valider les entrées utilisateur avant traitement
- Vérifier les patterns regex avec `re.compile()`
- Détecter les patterns dangereux (catastrophic backtracking)

```python
from modules.utils import validate_regex_pattern

is_valid, error = validate_regex_pattern(pattern)
if not is_valid:
    raise ValidationError(error)
```

### Gestion d'erreurs

- **JAMAIS** utiliser `except:` nu - toujours spécifier le type
- Utiliser les classes d'exceptions de `modules/exceptions.py`
- Logger les erreurs avec contexte

```python
from modules.exceptions import ValidationError, DatabaseError
from modules.logger import logger

try:
    risky_operation()
except (ValueError, TypeError) as e:
    logger.error(f"Operation failed: {e}")
    raise ValidationError(f"Invalid input: {e}")
```

### Protection XSS

- Utiliser `escape_html()` pour tout contenu utilisateur dans HTML
- Préférer `safe_html_template()` pour interpolation complexe

```python
from modules.utils import safe_html_template

safe_html = safe_html_template(
    "<div class='item'><h3>{title}</h3></div>",
    title=user_title  # Automatiquement échappé
)
```

---

## 🧪 Stratégie de tests

### Organisation des tests

- **tests/db/** : Tests de la couche d'accès données
- **tests/ai/** : Tests des modules IA
- **tests/ui/** : Tests des composants UI
- **tests/test_integration.py** : Tests d'intégration

### Fixtures principales (conftest.py)

| Fixture | Description |
|---------|-------------|
| `temp_db` | Base de données temporaire isolée |
| `sample_transactions` | Données de transactions de test |
| `sample_categories` | Catégories de test |
| `sample_members` | Membres de test |
| `db_connection` | Connexion DB pour requêtes directes |

### Exécution des tests

```bash
# Tous les tests
pytest

# Avec rapport de couverture
pytest --cov=modules --cov-report=html --cov-report=term-missing

# Tests spécifiques
pytest tests/db/ -v
pytest tests/ai/test_anomaly_detector.py -v
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

---

## 📚 Documentation complémentaire

- **docs/gemini.md** : Guidelines de développement détaillées
- **docs/1. PROJET.md** : Vision produit
- **docs/3.x Page : *.md** : Spécifications des pages
- **CHANGELOG.md** : Historique des versions

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

---

**Dernière mise à jour** : 2026-01-30
**Version du projet** : 3.1.0
**Langue principale** : Français
