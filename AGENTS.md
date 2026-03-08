# AGENTS.md - Guide pour les Agents de Codage

> Ce fichier est destiné aux agents de codage AI. Il contient les informations essentielles pour comprendre et travailler sur ce projet.

---

## Vue d'ensemble du projet

**MyFinance Companion** (aussi appelé FinancePerso) est une application web de gestion financière personnelle développée avec Streamlit. Elle permet :

- L'import automatique de transactions bancaires (CSV)
- La catégorisation automatique par IA (cloud ou ML local offline)
- La validation rapide avec regroupement intelligent
- L'analyse visuelle avec tableaux de bord et graphiques
- La gestion budgétaire par catégorie
- Le suivi multi-membres du foyer
- Les projections de patrimoine et prêts

**Version actuelle** : 5.6.0 (voir `modules/constants.py`)

---

## Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Langage | Python | 3.12+ (cible), 3.11+ (supporté) |
| Framework Web | Streamlit | 1.54.0 |
| Base de données | SQLite | 3.x |
| Data Science | pandas, plotly | 2.3.3, 6.5.2 |
| IA Cloud | Google GenAI | ≥0.3.0 |
| ML Local | scikit-learn | ≥1.3.0 (optionnel) |
| Sécurité | cryptography | 44.0.3 |
| Monitoring | sentry-sdk | 2.53.0 |

---

## Structure du projet

```
FinancePerso/
├── app.py                      # Point d'entrée principal (page d'accueil)
├── pages/                      # Pages Streamlit (navigation automatique)
│   ├── 01_Import.py           # Import de transactions CSV
│   ├── 02_Dashboard.py        # Tableau de bord et analyses (V5.5)
│   ├── 03_Intelligence.py     # Règles, budgets, audit IA
│   ├── 04_Budgets.py          # Gestion budgétaire
│   ├── 05_Audit.py            # Audit des transactions
│   ├── 06_Assistant.py        # Chat IA conversationnel
│   ├── 07_Recherche.py        # Recherche globale
│   ├── 08_Configuration.py    # Paramètres système
│   ├── 09_Badges.py           # Gamification et défis
│   ├── 10_Projections.py      # Projections de trésorerie
│   ├── 11_Abonnements.py      # Gestion des abonnements
│   ├── 12_Patrimoine.py       # Suivi du patrimoine
│   ├── 13_Nouveautes.py       # Nouveautés et changelog
│   ├── 14_Notifications.py    # Centre de notifications
│   └── ...
├── modules/                    # Logique métier (~28,000 lignes)
│   ├── ai/                    # Suite IA (anomalies, prédictions, tags)
│   ├── analytics/             # Métriques et événements
│   ├── cache/                 # Gestion du cache multi-niveaux
│   ├── cashflow/              # Prédiction de trésorerie
│   ├── core/                  # Événements et bus de messages
│   ├── couple/                # Gestion des membres du foyer
│   ├── db/                    # Couche données (SQLite)
│   │   ├── migrations.py      # Schéma et migrations
│   │   ├── transactions.py    # CRUD transactions
│   │   ├── categories.py      # Gestion catégories
│   │   ├── members.py         # Gestion membres
│   │   ├── budgets.py         # Gestion budgets
│   │   ├── rules.py           # Règles d'apprentissage
│   │   └── repositories/      # Pattern Repository
│   ├── gamification/          # Système de défis et badges
│   ├── ingestion/             # Import et parsing CSV
│   ├── notifications/         # Système de notifications V3
│   ├── privacy/               # Gestion GDPR et confidentialité
│   ├── ui/                    # Composants UI
│   │   ├── components/        # Composants réutilisables
│   │   ├── dashboard/         # Widgets dashboard
│   │   ├── atoms/             # Design System - Atomes
│   │   ├── molecules/         # Design System - Molécules
│   │   ├── tokens/            # Design System - Tokens
│   │   └── v5_5/              # Interface V5.5 (FinCouple)
│   ├── wealth/                # Gestion du patrimoine
│   ├── ai_manager.py          # Gestionnaire IA unifié
│   ├── categorization.py      # Logique de catégorisation
│   ├── encryption.py          # Chiffrement AES-256
│   ├── logger.py              # Système de logs
│   └── constants.py           # Constantes et feature flags
├── tests/                      # Tests pytest (~7,000 lignes)
│   ├── test_essential.py      # Tests critiques (rapides)
│   ├── db/                    # Tests couche données
│   ├── ui/                    # Tests composants UI
│   ├── ai/                    # Tests modules IA
│   ├── integration/           # Tests d'intégration
│   ├── e2e/                   # Tests end-to-end
│   └── conftest.py            # Fixtures partagées
├── Data/                       # Données locales (gitignored)
│   ├── finance.db             # Base SQLite principale
│   └── backups/               # Sauvegardes automatiques
├── docs/                       # Documentation
│   ├── README.md              # Point d'entrée documentation
│   ├── INDEX.md               # Index de navigation
│   ├── ACTIVE/                # Documentation maintenue
│   ├── PLANNING/              # Plans et roadmaps
│   ├── REFERENCE/             # Référence technique
│   └── archive/               # Documentation historique
├── migrations/                 # Scripts de migration SQL
├── scripts/                    # Scripts utilitaires
└── .streamlit/config.toml     # Configuration Streamlit
```

**Points clés d'architecture :**

- **~40,000 lignes de code** (modules + pages + tests)
- **Pattern Repository** : Couche `modules/db/` abstrait l'accès aux données
- **Design System Atomic** : `modules/ui/atoms/`, `molecules/`, `tokens/`
- **Session State Streamlit** : Gestion d'état via `st.session_state`
- **Cache multi-niveaux** : `@st.cache_data` + disque + mémoire
- **Feature Flags** : Défini dans `modules/constants.py`

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
- **Ruff** : Linting et tri des imports (line-length: 120)
- **Bandit** : Analyse de sécurité
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
| `savings_goals` | Objectifs d'épargne | `name`, `target_amount` |
| `notifications` | Notifications V3 | `type`, `level`, `is_read` |

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

### Gestionnaire IA (`modules/ai_manager.py`)

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
- **detectors.py** : Détecteurs de notifications
- **ui.py** : Composants UI avec Design System

### UI V5.5 (`modules/ui/v5_5/`)

Interface moderne light mode (design FinCouple) :
- **theme.py** : Thème Emerald avec CSS global
- **components/** : Composants spécifiques V5.5 (KPI cards, charts, transactions)
- **dashboard/** : Dashboard complet V5.5
- **pages/** : Controllers pour les pages

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
├── e2e/                       # Tests end-to-end
└── v5_5/                      # Tests interface V5.5
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
- Build et test de démarrage de l'app Docker

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

1. **Numérotation des pages** : Les fichiers dans `pages/` utilisent un préfixe numérique pour l'ordre (01_, 02_, 03_, etc.)

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

6. **Feedback UI** : Utiliser uniquement `modules/ui/feedback.py` :
```python
from modules.ui.feedback import toast_success, toast_error, show_success, confirm_dialog

# Toasts éphémères
toast_success("Opération réussie!")
toast_error("Une erreur s'est produite")

# Banners persistants
show_success("Titre", "Message détaillé")

# Dialogues de confirmation
if confirm_dialog("Êtes-vous sûr ?", "Cette action est irréversible", danger=True):
    delete_item()
```

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

### Feature Flags

Les fonctionnalités sont contrôlées via `modules/constants.py` :

```python
USE_NOTIFICATIONS_V3 = True      # Système de notifications V3
USE_V5_5_INTERFACE = True        # Interface V5.5 (light mode)
TEST_DASHBOARD_ENABLED = True    # Page Test_Dashboard V5.5
```

---

## Skills, Agents & MCP - Architecture d'Orchestration

Le projet utilise une architecture **5 couches** pour garantir qualité, cohérence et efficacité :

```
┌─────────────────────────────────────────────────────────────────┐
│  COUCHE 1: OUTILS NATIFS (ReadFile, Shell, Grep...)            │
│  → Actions simples et directes                                 │
├─────────────────────────────────────────────────────────────────┤
│  COUCHE 2: MCP SERVERS (sqlite, filesystem, playwright...)     │
│  → Capacités spécialisées avec état persistant                 │
├─────────────────────────────────────────────────────────────────┤
│  COUCHE 3: SKILLS (consistency-keeper, financeperso-...)       │
│  → Connaissances contextuelles et conventions                  │
├─────────────────────────────────────────────────────────────────┤
│  COUCHE 4: AGENT-000 (Orchestrator)                            │
│  → Routeur central - OBLIGATOIRE avant agents                  │
├─────────────────────────────────────────────────────────────────┤
│  COUCHE 5: SOUS-AGENTS (AGENT-001 à 021)                       │
│  → Exécution spécialisée par domaine                           │
└─────────────────────────────────────────────────────────────────┘
```

### MCP Servers (Extensions)

| MCP | Capacité | Agents principaux | Usage typique |
|-----|----------|-------------------|---------------|
| `sqlite` | Requêtes SQL sur `finance.db` | AGENT-001, 004, 006, 014 | Analytics, debug DB, KPIs |
| `filesystem` | Exploration fichiers avancée | AGENT-009, 021 | Lister composants, explorer docs |
| `playwright` | Tests navigateur, screenshots | AGENT-006, 010, 012 | Test UI, validation visuelle |
| `github` | Issues, PRs, repo | AGENT-003, 013 | Gestion tickets, releases |
| `fetch` | Requêtes HTTP/API | AGENT-007, 018 | APIs IA, Open Banking |
| `context7` | Documentation libraries | AGENT-005, 007 | Doc pandas, streamlit, etc. |

### Skills (Globaux)

| Skill | Rôle | Quand l'utiliser |
|-------|------|------------------|
| `consistency-keeper` | **Gardien de la cohérence** - vérifie DRY, doc sync, rangement, performance | **TOUJOURS en 1er et dernier** |
| `financeperso-specific` | **Conventions FinancePerso** | **TOUJOURS combiné** avec skill technique |

**Règles:**
1. `consistency-keeper` = **1er et dernier** de chaque workflow
2. `financeperso-specific` = **jamais seul**, toujours combiné

### Agents (Spécialisés FinancePerso)

**⚠️ OBLIGATOIRE:** Toujours passer par `AGENT-000` avant tout agent spécialisé !

| Agent | Domaine | Fichier |
|-------|---------|---------|
| AGENT-000 | **Orchestrateur** | `.agents/subagents/AGENT-000-Orchestrator.md` |
| AGENT-001 | Database Architect | `.agents/subagents/AGENT-001-Database-Architect.md` |
| AGENT-002 | Security Guardian | `.agents/subagents/AGENT-002-Security-Guardian.md` |
| AGENT-003 | DevOps Engineer | `.agents/subagents/AGENT-003-DevOps-Engineer.md` |
| AGENT-004 | Transaction Engine | `.agents/subagents/AGENT-004-Transaction-Engine-Specialist.md` |
| AGENT-005 | Categorization AI | `.agents/subagents/AGENT-005-Categorization-AI-Specialist.md` |
| AGENT-006 | Analytics Dashboard | `.agents/subagents/AGENT-006-Analytics-Dashboard-Engineer.md` |
| AGENT-007 | AI Provider Manager | `.agents/subagents/AGENT-007-AI-Provider-Manager.md` |
| AGENT-008 | AI Features Specialist | `.agents/subagents/AGENT-008-AI-Features-Specialist.md` |
| AGENT-009 | UI Component Architect | `.agents/subagents/AGENT-009-UI-Component-Architect.md` |
| AGENT-010 | Navigation Experience | `.agents/subagents/AGENT-010-Navigation-Experience-Designer.md` |
| AGENT-011 | Data Validation | `.agents/subagents/AGENT-011-Data-Validation-Interface.md` |
| AGENT-012 | Test Automation | `.agents/subagents/AGENT-012-Test-Automation-Engineer.md` |
| AGENT-013 | QA Integration | `.agents/subagents/AGENT-013-QA-Integration-Specialist.md` |
| AGENT-014 | Budget Wealth Manager | `.agents/subagents/AGENT-014-Budget-Wealth-Manager.md` |
| AGENT-015 | Member Management | `.agents/subagents/AGENT-015-Member-Management-Specialist.md` |
| AGENT-016 | Notification System | `.agents/subagents/AGENT-016-Notification-System-Architect.md` |
| AGENT-017 | Data Pipeline | `.agents/subagents/AGENT-017-Data-Pipeline-Migration-Specialist.md` |
| AGENT-018 | Open Banking API | `.agents/subagents/AGENT-018-Open-Banking-API-Specialist.md` |
| AGENT-019 | Performance Engineer | `.agents/subagents/AGENT-019-Performance-Engineer.md` |
| AGENT-020 | Accessibility Specialist | `.agents/subagents/AGENT-020-Accessibility-Specialist.md` |
| AGENT-021 | Technical Writer | `.agents/subagents/AGENT-021-Technical-Writer.md` |

---

## Ressources utiles

### Documentation

- **Point d'entrée** : `docs/README.md` - Vue d'ensemble et navigation
- **Index global** : `docs/INDEX.md` - Index de tous les documents
- **Documentation active** : `docs/ACTIVE/` - Guides maintenus à jour
- **Planification** : `docs/PLANNING/` - Roadmaps et specs
- **Référence** : `docs/REFERENCE/` - ADRs et architecture
- **Guide utilisateur** : `docs/USER_GUIDE.md`
- **Architecture** : `docs/ARCHITECTURE.md`

### Ressources projet

- **Guide contribution** : `CONTRIBUTING.md`
- **Changelog** : `CHANGELOG.md`
- **Code de conduite** : `CODE_OF_CONDUCT.md`

---

Dernière mise à jour : 2026-03-05 (v5.6.0)
