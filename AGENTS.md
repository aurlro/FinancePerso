# AGENTS.md - Guide pour les Agents de Codage

> Ce fichier est destiné aux agents de codage AI. Il contient les informations essentielles pour comprendre et travailler sur ce projet.

---

## Vue d'ensemble du projet

**FinancePerso** (aussi appelé MyFinance Companion) est une application web de gestion financière personnelle développée avec Streamlit. Elle permet :

- L'import automatique de transactions bancaires (CSV)
- La catégorisation automatique par IA (cloud ou ML local offline)
- La validation rapide avec regroupement intelligent
- L'analyse visuelle avec tableaux de bord et graphiques
- La gestion budgétaire par catégorie
- Le suivi multi-membres du foyer

**Version actuelle** : 5.2.1 (voir `modules/constants.py`)

---

## Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Langage | Python | 3.12+ (cible), 3.11+ (supporté) |
| Framework Web | Streamlit | 1.47.0 |
| Base de données | SQLite | 3.x |
| Data Science | pandas, plotly | 2.3.1, 6.2.0 |
| IA Cloud | Google GenAI | ≥0.3.0 |
| ML Local | scikit-learn | ≥1.3.0 (optionnel) |
| Sécurité | cryptography | 44.0.0 |
| Monitoring | sentry-sdk | 2.20.0 |

---

## Structure du projet

```
FinancePerso/
├── app.py                      # Point d'entrée principal (page d'accueil)
├── pages/                      # Pages Streamlit (navigation automatique)
│   ├── 1_Opérations.py        # Import + Validation
│   ├── 3_Synthèse.py          # Dashboard et analyses
│   ├── 4_Intelligence.py      # Règles, budgets, audit IA
│   ├── 5_Budgets.py           # Gestion budgétaire
│   ├── 7_Assistant.py         # Chat IA conversationnel
│   ├── 8_Recherche.py         # Recherche globale
│   ├── 9_Configuration.py     # Paramètres système
│   └── ...
├── modules/                    # Logique métier
│   ├── ai/                    # Suite IA (anomalies, prédictions, tags)
│   ├── core/                  # Événements et bus de messages
│   ├── db/                    # Couche données (SQLite)
│   │   ├── migrations.py      # Schéma et migrations
│   │   ├── transactions.py    # CRUD transactions
│   │   ├── categories.py      # Gestion catégories
│   │   └── ...
│   ├── ui/                    # Composants UI
│   │   ├── components/        # Composants réutilisables
│   │   ├── dashboard/         # Widgets dashboard
│   │   └── ...
│   ├── ai_manager_v2.py       # Gestionnaire IA unifié
│   ├── categorization.py      # Logique de catégorisation
│   ├── encryption.py          # Chiffrement AES-256
│   ├── logger.py              # Système de logs
│   └── notifications/         # NOUVEAU - Système de notifications V3
│       ├── __init__.py
│       ├── models.py
│       ├── service.py
│       ├── repository.py
│       ├── detectors.py
│       └── ui.py
├── tests/                      # Tests pytest
│   ├── test_essential.py      # Tests critiques (rapides)
│   ├── db/                    # Tests couche données
│   ├── ui/                    # Tests composants UI
│   └── conftest.py            # Fixtures partagées
├── Data/                       # Données locales (gitignored)
│   ├── finance.db             # Base SQLite principale
│   └── backups/               # Sauvegardes automatiques
├── docs/                       # Documentation
│   ├── archive/               # Anciens documents
│   └── *.md                   # Guides et spécifications
├── scripts/                    # Scripts utilitaires
├── migrations/                 # Scripts de migration SQL
└── .streamlit/config.toml     # Configuration Streamlit
```

**Points clés d'architecture :**

- **~21,000 lignes de code** (modules + pages + tests)
- **Pattern Repository** : Couche `modules/db/` abstrait l'accès aux données
- **Composants UI modulaires** : `modules/ui/components/` pour la réutilisabilité
- **Session State Streamlit** : Gestion d'état via `st.session_state`
- **Cache multi-niveaux** : `@st.cache_data` + disque + mémoire

---

## Commandes de build et test

Toutes les commandes sont disponibles via le `Makefile` :

```bash
# Setup environnement de développement
make setup                    # Crée .venv + installe dépendances

# Tests
make test                     # Tests essentiels (~5s) - À LANCER AVANT CHAQUE COMMIT
make test-all                 # Tous les tests + couverture (~30s)

# Qualité de code
make lint                     # Vérification Ruff
make format                   # Formatage Black
make check                    # Lint + Tests essentiels (~10s) - AVANT CHAQUE PUSH
make ci                       # Simulation CI complète

# Lancement
make run                      # Démarrage Streamlit (équivalent: streamlit run app.py)

# Nettoyage
make clean                    # Supprime cache Python, coverage, etc.
```

**Workflow quotidien recommandé :**

```bash
# Avant chaque commit (rapide)
make test

# Avant chaque push (complet)
make check

# CI complet (comme GitHub Actions)
make ci
```

---

## Guidelines de style de code

### Outils configurés

- **Black** : Formatage automatique (line-length: 100)
- **Ruff** : Linting et tri des imports
- **Target Python** : 3.12

### Conventions

```python
# Docstrings style Google
"""
Description courte de la fonction.

Args:
    param1: Description du paramètre
    param2: Autre paramètre

Returns:
    Description de la valeur retournée

Raises:
    ValueError: Quand cette erreur est levée
"""

# Type hints recommandés pour les fonctions publiques
def categorize_transaction(
    transaction: Transaction,
    rules: list[Rule] | None = None,
) -> Category:
    ...

# Imports triés automatiquement par Ruff (isort)
import os
from datetime import date

import pandas as pd
import streamlit as st

from modules.db.transactions import get_transactions
```

### Exclusions de formatage

Les dossiers suivants sont exclus de Black/Ruff (voir `pyproject.toml`) :
- `.git`, `__pycache__`
- `Data` (données utilisateur)
- `docs`

---

## Architecture de la base de données

**SQLite** avec schéma géré par `modules/db/migrations.py`.

### Tables principales

| Table | Description | Clés importantes |
|-------|-------------|------------------|
| `transactions` | Opérations bancaires | `tx_hash` (unique), `status`, `category_validated` |
| `categories` | Catégories de dépenses | `name` (unique), `emoji`, `is_fixed` |
| `members` | Membres du foyer | `name` (unique), `member_type` |
| `learning_rules` | Règles d'apprentissage IA | `pattern` (unique), `priority` |
| `budgets` | Budgets par catégorie | `category` (PK), `amount` |
| `dashboard_layouts` | Configurations dashboard | `name`, `layout_json` |
| `recycle_bin` | Corbeille (soft delete) | `original_id`, `expires_at` |
| `transaction_history` | Historique pour undo | `action_group_id` |

### Connexion

Toujours utiliser le context manager :

```python
from modules.db.connection import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE status = ?", ("pending",))
    results = cursor.fetchall()
```

Le chemin de la base est configurable via `DB_PATH` dans `.env` (défaut: `Data/finance.db`).

---

## Modules clés

### Catégorisation (`modules/categorization.py`)

Cascade de catégorisation :
1. Règles exactes (`learning_rules`)
2. Règles partielles (pattern matching)
3. ML Local (si activé et disponible)
4. IA Cloud (Gemini/OpenAI/DeepSeek/Ollama)
5. Catégorie par défaut ("Inconnu")

### Gestionnaire IA (`modules/ai_manager_v2.py`)

Abstraction unifiée pour tous les providers IA :
- `gemini` (recommandé, gratuit)
- `ollama` (100% offline/local)
- `deepseek` (bon rapport qualité/prix)
- `openai` (standard industrie)
- `local_ml` (scikit-learn offline)

### Chiffrement (`modules/encryption.py`)

Chiffrement AES-256 des champs sensibles (notes, beneficiary) :
- Clé dérivée de `ENCRYPTION_KEY` dans `.env`
- Pattern singleton avec réinitialisation pour les tests

### UI (`modules/ui/`)

- **Composants** : Boutons, sélecteurs, modales réutilisables
- **Feedback** : Toasts, messages flash, états de chargement
- **Layout** : Structure de page, navigation

### Notifications V3 (`modules/notifications/`)

Nouveau système unifié avec persistance DB:

```python
from modules.notifications import NotificationService, NotificationType

service = NotificationService()
service.notify(
    type=NotificationType.BUDGET_WARNING,
    title="Budget",
    message="Message..."
)
```

- **models.py** : Dataclasses Notification, NotificationLevel, NotificationType
- **service.py** : NotificationService (singleton)
- **repository.py** : Accès DB SQLite
- **detectors.py** : 6 détecteurs de notifications
- **ui.py** : Composants UI avec Design System

Migration SQL: `migrations/007_notifications.sql`

---

## Configuration environnement

Créer un fichier `.env` à la racine (copier depuis `.env.example`) :

```bash
# Clés API IA (au moins une requise pour le mode cloud)
GEMINI_API_KEY=votre_cle
OPENAI_API_KEY=votre_cle
DEEPSEEK_API_KEY=votre_cle
OLLAMA_URL=http://localhost:11434

# Configuration IA
AI_PROVIDER=gemini
AI_MODEL_NAME=gemini-2.0-flash

# Sécurité (recommandé pour production)
ENCRYPTION_KEY=votre_cle_fernet
ENVIRONMENT=development

# Monitoring (optionnel)
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

**⚠️ Ne jamais commiter `.env` !** (déjà dans `.gitignore`)

---

## Stratégie de tests

### Organisation

```
tests/
├── test_essential.py          # Tests critiques (rapides, ~5s)
├── db/                        # Tests couche données
├── ui/                        # Tests composants UI
├── ai/                        # Tests modules IA
├── integration/               # Tests d'intégration
└── e2e/                       # Tests end-to-end
```

### Fixtures importantes (`tests/conftest.py`)

- `temp_db` : Base SQLite temporaire isolée par test
- `sample_transactions` : Données de test prêtes à l'emploi
- `reset_encryption_singleton` : Réinitialise le chiffrement entre tests

### Commandes

```bash
# Tests essentiels (à lancer fréquemment)
pytest tests/test_essential.py -v

# Tous les tests avec couverture
pytest tests/ --cov=modules --cov-report=html --cov-report=term-missing

# Un fichier spécifique
pytest tests/db/test_transactions.py -v
```

### CI/CD

GitHub Actions (`.github/workflows/ci.yml`) :
- Tests sur Python 3.11 et 3.12
- Lint Ruff + format check Black
- Scan de sécurité Bandit
- Vérification des dépendances Safety
- Build et test de démarrage de l'app

---

## Considérations de sécurité

### Données sensibles

- **Jamais** de credentials dans le code source
- Utiliser `.env` pour les variables sensibles
- Chiffrement AES-256 pour les données sensibles en base (notes, beneficiary)

### Protection contre les attaques

- **XSS** : Échappement HTML via `modules.utils.escape_html`
- **SQL Injection** : Toujours utiliser des paramètres bind (`?`)
- **Validation** : Utiliser `modules.validators.validate_sql_identifier`

### Fichiers critiques à ne pas exposer

```
.env              # Clés API et secrets
Data/finance.db   # Base de données utilisateur
Data/backups/     # Sauvegardes
logs/*.log        # Fichiers de log
```

---

## Déploiement

### Docker

```bash
# Build
docker build -t financeperso .

# Run avec docker-compose
docker-compose up -d
```

### Manuel

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Accès

Par défaut : http://localhost:8501

---

## Notes de développement

### Conventions spécifiques au projet

1. **Numérotation des pages** : Les fichiers dans `pages/` utilisent un préfixe numérique pour l'ordre (1_, 3_, 4_, etc.)

2. **Session State** : Toujours initialiser les clés au début des pages :
```python
if "ma_cle" not in st.session_state:
    st.session_state["ma_cle"] = valeur_defaut
```

3. **Cache** : Utiliser `@st.cache_data` pour les appels DB coûteux, `@st.cache_resource` pour les connexions

4. **Logs** : Utiliser `modules.logger` au lieu de `print()` :
```python
from modules.logger import logger
logger.info("Message informatif")
logger.error("Erreur: %s", erreur)
```

5. **Gestion des erreurs** : Toujours capturer les erreurs critiques au démarrage (voir `app.py` pour l'exemple macOS permission)

### Patterns courants

```python
# Récupération de transactions avec cache
@st.cache_data(ttl=300)
def get_cached_transactions(status=None):
    return get_transactions(status=status)

# Formulaire avec validation
with st.form("mon_form"):
    valeur = st.text_input("Label")
    submit = st.form_submit_button("Valider")
    if submit and valeur:
        # Traitement
        pass
```

### Notifications
> **Note**: La version 3.0 du système de notifications est maintenant active par défaut.
> Pour revenir à la version 2.0, modifiez `NOTIFICATION_SYSTEM_VERSION` dans 
> `modules/notifications/__init__.py`

- Toujours utiliser NotificationService V3 pour les nouvelles notifications
- Les détecteurs s'exécutent automatiquement au démarrage
- Voir docs/MIGRATION_NOTIFICATIONS_V3.md pour la migration depuis V2

---

## Ressources utiles

- **Documentation utilisateur** : `docs/USER_GUIDE.md`
- **Guide contribution** : `CONTRIBUTING.md`
- **Changelog** : `CHANGELOG.md`
- **Architecture détaillée** : `docs/ARCHITECTURE.md`

---

Dernière mise à jour : 2026-02-28 (v5.2.1)
