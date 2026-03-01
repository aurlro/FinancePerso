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

6. **Feedback UI** : Utiliser uniquement `modules/ui/feedback.py` (les versions `_v2`, `_wrapper`, `enhanced_` ont été supprimées) :
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

### Notifications
> **Note**: La version 3.0 du système de notifications est maintenant active par défaut.
> Pour revenir à la version 2.0, modifiez `NOTIFICATION_SYSTEM_VERSION` dans 
> `modules/notifications/__init__.py`

- Toujours utiliser NotificationService V3 pour les nouvelles notifications
- Les détecteurs s'exécutent automatiquement au démarrage
- Voir docs/MIGRATION_NOTIFICATIONS_V3.md pour la migration depuis V2

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

**Documentation détaillée:**
- Architecture complète: `.kimi/ARCHITECTURE_ORCHESTRATION.md`
- Mapping MCP ↔ Agents: `.kimi/MCP_AGENTS_MAPPING.md`
- Templates de prompts: `.kimi/PROMPT_TEMPLATES.md`
- Démonstration: `.kimi/DEMO_ARCHITECTURE.md`

---

### MCP Servers (Extensions)

| MCP | Capacité | Agents principaux | Usage typique |
|-----|----------|-------------------|---------------|
| `sqlite` | Requêtes SQL sur `finance.db` | AGENT-001, 004, 006, 014 | Analytics, debug DB, KPIs |
| `filesystem` | Exploration fichiers avancée | AGENT-009, 021 | Lister composants, explorer docs |
| `playwright` | Tests navigateur, screenshots | AGENT-006, 010, 012 | Test UI, validation visuelle |
| `github` | Issues, PRs, repo | AGENT-003, 013 | Gestion tickets, releases |
| `fetch` | Requêtes HTTP/API | AGENT-007, 018 | APIs IA, Open Banking |
| `context7` | Documentation libraries | AGENT-005, 007 | Doc pandas, streamlit, etc. |

**Configuration:** `~/.config/kimi/mcp.json`

---

### Skills (Globaux)

| Skill | Rôle | Quand l'utiliser |
|-------|------|------------------|
| `consistency-keeper` | **Gardien de la cohérence** - vérifie DRY, doc sync, rangement, performance | **TOUJOURS en 1er et dernier** |
| `skills-orchestrator` | Coordination des skills entre eux | Quand plusieurs skills collaborent |
| `project-auditor` | Audit global (sécurité, structure) | Avant déploiement |
| `python-app-auditor` | Audit technique Python | Audit code, refactoring |
| `streamlit-app-auditor` | Audit fonctionnel Streamlit | Test app en conditions réelles |
| `ux-product-designer` | Design et UX | Amélioration interface |
| `financeperso-specific` | **Conventions FinancePerso** | **TOUJOURS combiné** avec skill technique |

**Règles:**
1. `consistency-keeper` = **1er et dernier** de chaque workflow
2. `financeperso-specific` = **jamais seul**, toujours combiné
3. `skills-orchestrator` = si plusieurs skills en parallèle

---

### Agents (Spécialisés FinancePerso)

**⚠️ OBLIGATOIRE:** Toujours passer par `AGENT-000` avant tout agent spécialisé !

**Orchestrateur:**
| Agent | Rôle |
|-------|------|
| `AGENT-000` | **Orchestrateur** - Route vers agents spécialisés, coordonne dépendances |

**Agents par domaine:**
| Agent | Domaine | MCP utiles | Fichier |
|-------|---------|------------|---------|
| AGENT-001 | Database Architect | sqlite, filesystem | `.agents/subagents/AGENT-001*.md` |
| AGENT-002 | Security Guardian | github, filesystem | `.agents/subagents/AGENT-002*.md` |
| AGENT-003 | DevOps Engineer | filesystem, shell | `.agents/subagents/AGENT-003*.md` |
| AGENT-004 | Transaction Engine | **sqlite** | `.agents/subagents/AGENT-004*.md` |
| AGENT-005 | Categorization AI | sqlite, context7 | `.agents/subagents/AGENT-005*.md` |
| AGENT-006 | Analytics Dashboard | **sqlite, playwright** | `.agents/subagents/AGENT-006*.md` |
| AGENT-007 | AI Provider Manager | fetch, context7 | `.agents/subagents/AGENT-007*.md` |
| AGENT-008 | AI Features Specialist | sqlite, fetch | `.agents/subagents/AGENT-008*.md` |
| AGENT-009 | UI Component Architect | **filesystem, playwright** | `.agents/subagents/AGENT-009*.md` |
| AGENT-010 | Navigation Experience | **playwright** | `.agents/subagents/AGENT-010*.md` |
| AGENT-011 | Data Validation | sqlite | `.agents/subagents/AGENT-011*.md` |
| AGENT-012 | Test Automation | **playwright, shell** | `.agents/subagents/AGENT-012*.md` |
| AGENT-013 | QA Integration | **playwright, github** | `.agents/subagents/AGENT-013*.md` |
| AGENT-014 | Budget Manager | sqlite | `.agents/subagents/AGENT-014*.md` |
| AGENT-015 | Member Management | sqlite | `.agents/subagents/AGENT-015*.md` |
| AGENT-016 | Notification System | sqlite | `.agents/subagents/AGENT-016*.md` |
| AGENT-017 | Data Pipeline | sqlite, filesystem | `.agents/subagents/AGENT-017*.md` |
| AGENT-018 | Open Banking API | **fetch** | `.agents/subagents/AGENT-018*.md` |
| AGENT-019 | Performance Engineer | **playwright, sqlite** | `.agents/subagents/AGENT-019*.md` |
| AGENT-020 | Accessibility Specialist | **playwright** | `.agents/subagents/AGENT-020*.md` |
| AGENT-021 | Technical Writer | filesystem | `.agents/subagents/AGENT-021*.md` |

---

### Workflow Standard (6 phases)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. ANALYSE (consistency-keeper)                                │
│    └── Check cohérence actuelle                                │
│    └── Identifie patterns existants à réutiliser               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. AUDIT ([Skill] + financeperso-specific)                     │
│    └── python-app-auditor: qualité code                        │
│    └── streamlit-app-auditor: test runtime                     │
│    └── ux-product-designer: design/UX                          │
│    └── + conventions FinancePerso                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. ROUTAGE (AGENT-000)                                         │
│    └── Détermine agent(s) spécialisé(s)                        │
│    └── Planifie ordre d'exécution                              │
│    └── Gère dépendances                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. IMPLÉMENTATION ([Agent] + MCP)                              │
│    └── Agent utilise MCP appropriés:                           │
│        • sqlite → requêtes DB                                  │
│        • filesystem → exploration fichiers                     │
│        • playwright → test UI/screenshots                      │
│        • fetch → APIs externes                                 │
│        • github → gestion repo                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. VALIDATION (consistency-keeper)                             │
│    └── Vérifie DRY respecté                                    │
│    └── Vérifie doc synchronisée                                │
│    └── Vérifie rangement fichiers                              │
│    └── Vérifie performance                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. TESTS (AGENT-012/013)                                       │
│    └── Tests unitaires                                         │
│    └── Tests intégration                                       │
│    └── Tests E2E (playwright)                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Workflow par type de tâche

#### Nouvelle Feature (30-60 min)
```
consistency-keeper → python-app-auditor+financeperso-specific 
→ AGENT-000 → [Agent] → consistency-keeper → AGENT-012
```

#### Bug Fix (10-20 min)
```
AGENT-000 → [Agent] → python-app-auditor quick-check → AGENT-012
```

#### Hotfix Critique (5-10 min)
```
[Agent] → Fix minimal → Tests rapides → (consistency-keeper après)
```

#### Refactoring (45-90 min)
```
consistency-keeper --baseline → Plan → AGENT-000 coordonne 
→ Étapes migration → consistency-keeper --compare → Tests
```

#### UI Maquette V5.5 (30-45 min)
```
consistency-keeper+ux-product-designer → streamlit-app-auditor 
→ AGENT-000 → AGENT-009 → AGENT-006 → playwright validation
```

#### Analytics/KPI (20-30 min)
```
consistency-keeper → AGENT-000 → AGENT-001(sqlite) 
→ AGENT-006 → AGENT-012
```

---

### Exemples de prompts

**Feature complète:**
```
"consistency-keeper analyse les patterns existants, puis 
 python-app-auditor+financeperso-specific auditent le code. 
 AGENT-000 route vers AGENT-009 pour créer un composant BudgetAlert. 
 AGENT-006 intègre avec sqlite pour les données. 
 consistency-keeper valide à la fin."
```

**Bug fix:**
```
"AGENT-000: Bug dans la catégorisation, route vers AGENT-005. 
 Utilise MCP sqlite pour debug les transactions concernées. 
 python-app-auditor vérifie pas d'impact négatif."
```

**UI maquette:**
```
"Implémente maquette V5.5: consistency-keeper+ux-product-designer 
 analysent, AGENT-000 coordonne AGENT-009. 
 Validation avec streamlit-app-auditor+playwright."
```

---

### Checklist Consistency Keeper

Avant de finaliser une tâche, vérifier :

- [ ] **DRY** - Pas de code dupliqué, composants réutilisés
- [ ] **Doc Sync** - AGENTS.md, README.md, CHANGELOG.md à jour
- [ ] **Rangement** - Fichiers au bon endroit, pas d'orphelins
- [ ] **Performance** - Cache utilisé, pas de requêtes N+1
- [ ] **MCP** - Utilisés efficacement (pas de `cat` quand `sqlite/read_query` existe)

### Anti-patterns à éviter

❌ **Ne jamais:**
- Appeler un agent spécialisé sans passer par AGENT-000
- Utiliser `Shell` pour `cat fichier` quand `filesystem/read_file` existe
- Faire des requêtes SQL via `Shell(sqlite3...)` quand `sqlite/read_query` existe
- Lancer consistency-keeper seul (sans skill technique combiné)
- Oublier financeperso-specific sur du code FinancePerso

✅ **Toujours:**
- Passer par AGENT-000 avant tout agent spécialisé
- Utiliser MCP quand disponible pour la capacité
- Combiner financeperso-specific avec skill technique
- Débuter et terminer par consistency-keeper

---

## Historique des changements majeurs (Consistency Keeper)

### 2026-03-01 - Architecture d'Orchestration complète
**Nouvelle organisation 5 couches: Outils → MCP → Skills → Agents → Sous-Agents**

**Documentation créée:**
- ✅ `.kimi/ARCHITECTURE_ORCHESTRATION.md` - Architecture 5 couches complète
- ✅ `.kimi/MCP_AGENTS_MAPPING.md` - Mapping MCP ↔ Agents
- ✅ `.kimi/PROMPT_TEMPLATES.md` - Templates de prompts par type de tâche
- ✅ `.kimi/DEMO_ARCHITECTURE.md` - Démonstration sur feature réelle

**MCP Servers configurés:**
- ✅ `sqlite` - Requêtes SQL directes sur `Data/finance.db`
- ✅ `filesystem` - Exploration fichiers avancée
- ✅ `fetch` - Requêtes HTTP/API
- ✅ Configuration: `~/.config/kimi/mcp.json`

**Workflow standardisé (6 phases):**
1. consistency-keeper (analyse)
2. Skills techniques + financeperso-specific (audit)
3. AGENT-000 (routage)
4. Agent spécialisé + MCP (implémentation)
5. consistency-keeper (validation)
6. AGENT-012/013 (tests)

**Règles établies:**
- AGENT-000 OBLIGATOIRE avant tout agent spécialisé
- consistency-keeper en 1er et dernier
- financeperso-specific TOUJOURS combiné
- MCP préférés aux outils natifs quand pertinent

### 2026-03-01 - Implémentation V5.5 (Maquettes FinCouple)
**Nouvelle interface light mode avec design épuré**

**Phase 0 - Design System:**
- ✅ Création `modules/ui/v5_5/theme.py` (thème light mode)
- ✅ Palette Emerald (#10B981) comme maquette
- ✅ CSS global 9,812 caractères
- ✅ Boutons style maquette (primaire foncé, secondaire bordure)

**Phase 1 - Welcome Component:**
- ✅ `modules/ui/v5_5/components/welcome_card.py`
- ✅ Card centrée avec ombre
- ✅ Icône 💰 dans cercle vert (#D1FAE5)
- ✅ "👋 Bonjour [Nom] !"
- ✅ 2 boutons : Importer + Guide
- ✅ Modal guide intégré

**Phase 2 - Dashboard:**
- ✅ `modules/ui/v5_5/components/kpi_card.py` - 4 KPIs style maquette
- ✅ `modules/ui/v5_5/components/dashboard_header.py` - "Bonjour, Alex 👋"
- ✅ `modules/ui/v5_5/dashboard/dashboard_v5.py` - Dashboard complet
- ✅ `modules/ui/v5_5/dashboard/kpi_grid.py` - Calcul KPIs depuis DB
- ✅ `modules/ui/v5_5/dashboard/empty_state.py` - Onboarding 3 étapes
- ✅ Graphique donut répartition dépenses
- ✅ Liste transactions récentes

**Phase 3 - Intégration:**
- ✅ `app_v5_5.py` - Point d'entrée V5.5
- ✅ Feature flag `USE_V5_5_INTERFACE` dans constants.py
- ✅ Sidebar navigation moderne
- ✅ Détection automatique welcome ↔ dashboard

**Fichiers créés:**
- `modules/ui/v5_5/` (2,249+ lignes)
- `pages/test_v5_*.py` (pages de test)
- `.agents/skills/SKILLS_AGENTS_COORDINATION.md`

### 2026-03-01 - Consolidation des modules feedback
**Problème** : 4 modules de feedback coexistaient (`feedback.py`, `feedback_v2.py`, `feedback_wrapper.py`, `enhanced_feedback.py`)

**Solution** :
- ✅ Suppression de `modules/ui/feedback_v2.py` (non utilisé, dépendances manquantes)
- ✅ Suppression de `modules/ui/feedback_wrapper.py` (non utilisé)
- ✅ Suppression de `modules/ui/enhanced_feedback.py` (non utilisé)
- ✅ Conservation de `modules/ui/feedback.py` (seul utilisé dans le codebase)

**Impact** : -3 fichiers, API unique, moins de confusion

### 2026-03-01 - Nettoyage des dossiers vides
- ✅ Suppression de `views/` (vide)
- ✅ Suppression de `modules/ui/charts/` (vide)
- ✅ Suppression des dossiers malformés `tests/{ui,unit,integration}/{helpers}/`
- ✅ Nettoyage des caches Python (~2000 fichiers .pyc)

### 2026-03-01 - Uniformisation validate_sql_identifier
- ✅ Fusion des deux implémentations dans `modules/db/connection.py`
- ✅ API cohérente avec paramètre `allowed` optionnel

### 2026-03-01 - Page Test_Dashboard V5.5 (Phase 1 & 2)
**Migration du bac à sable vers production**

**Phase 1 - Fondations:**
- ✅ Création `modules/ui/v5_5/pages/` (controllers)
- ✅ `dashboard_controller.py` - Logique métier centralisée
- ✅ Feature flag `TEST_DASHBOARD_ENABLED` dans constants.py
- ✅ Structure modulaire prête pour production

**Phase 2 - Core Dashboard:**
- ✅ `pages/Test_Dashboard.py` - Page production complète
- ✅ Détection auto données (welcome ↔ dashboard)
- ✅ Mode démo avec données fictives
- ✅ Navigation depuis app.py ("✨ Tester le nouveau dashboard")
- ✅ Intégration thème V5.5, notifications V3
- ✅ Gestion erreurs et retry

**URLs:**
- Production: `http://localhost:8501/Test_Dashboard`
- Bac à sable: `http://localhost:8501/99_Test_Dashboard` (legacy)

**Architecture controller:**
```python
DashboardController(
    user_name="Alex",
    test_mode="auto",  # auto|dashboard|welcome
    force_view=False
)
```

---

## Ressources utiles

- **Documentation utilisateur** : `docs/USER_GUIDE.md`
- **Guide contribution** : `CONTRIBUTING.md`
- **Changelog** : `CHANGELOG.md`
- **Architecture détaillée** : `docs/ARCHITECTURE.md`
- **Guide Consistency Keeper** : `~/.config/agents/skills/consistency-keeper/SKILL.md`

---

### 2026-03-01 - Dashboard V5.5 Phase 3 (Feature Parity)
**Ajout des fonctionnalités manquantes pour parité avec dashboard legacy**

**Nouveaux composants:**
- ✅ `DonutChart` - Graphique donut avec couleurs par catégorie
- ✅ `TransactionList` - Liste avec icônes par catégorie (25 catégories)
- ✅ `SavingsGoalsWidget` - Objectifs d'épargne
- ✅ `render_period_filter` - Filtres de période
- ✅ `render_couple_summary` - Vue couple

**Structure:**
```
modules/ui/v5_5/components/
├── charts/donut.py          ✅
├── filters/period_filter.py ✅
├── transactions/            ✅
└── savings_goals.py         ✅
```

### 2026-03-01 - Dashboard V5.5 Phase 4 (Tests & Intégration)
**Préparation au remplacement du dashboard legacy**

**Tests créés:**
- `tests/v5_5/test_components.py` - 13 tests unitaires
- `tests/v5_5/test_kpi_calculations.py` - 8 tests de calculs
- `tests/e2e/test_dashboard_beta.py` - Tests E2E Playwright

**Outils de migration:**
- `scripts/migrate_to_v5_5.py` - Script avec --check / --apply / --rollback
- `docs/MIGRATION_V5_5.md` - Guide de migration complet

**Validation:** 21/21 tests passent ✅

### 2026-03-01 - MIGRATION TERMINÉE ✅
**Dashboard V5.5 en production**

**Migration exécutée:**
- ✅ `02_Dashboard.py` remplacé par version V5.5 (8,302 octets)
- ✅ Sauvegarde créée: `02_Dashboard_backup.py`
- ✅ `Dashboard_Beta.py` → `Dashboard_Beta.deprecated`
- ✅ `99_Test_Dashboard.py` supprimé
- ✅ Application fonctionnelle sur http://localhost:8501/Dashboard

**Nouveau dashboard actif:**
- URL: `http://localhost:8501/Dashboard`
- Design: Light mode FinCouple
- Features: 4 KPIs, Donut chart, Transactions, Objectifs épargne

### 2026-03-01 - CI/CD VALIDÉ ✅
**Correction et validation pour GitHub Actions**

**Corrections appliquées:**
- ✅ Formatage Black sur tous les fichiers V5.5
- ✅ Linting Ruff: 0 erreurs
- ✅ Lignes trop longues (E501) corrigées
- ✅ Variables inutilisées (F841) supprimées
- ✅ Imports manquants dans `__all__` ajoutés
- ✅ Import pandas manquant ajouté dans dashboard_v5.py

**Validation:**
- ✅ 21/21 tests passent
- ✅ CI/CD configuré dans `.github/workflows/ci.yml`
- ✅ Tests exécutés sur Python 3.11 et 3.12

---

Dernière mise à jour : 2026-03-01 (v5.5.6) - CI/CD VALIDÉ ✅
