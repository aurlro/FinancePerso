# 📊 Rapport d'Audit des Imports - FinancePerso

**Date:** 2026-02-18  
**Modules analysés:** 148  
**Total d'imports internes:** 374  
**Moyenne par module:** 2.5 imports

---

## 🚨 1. IMPORTS CIRCULAIRES DÉTECTÉS

### 1.1 Circulaires Directs (Résolus par imports locaux)

| Module A | Module B | Statut | Explication |
|----------|----------|--------|-------------|
| `cache_manager` | `db.transactions` | ⚠️ **RISQUE** | cache_manager importe db.transactions pour invalider le cache, mais db.transactions importe cache_manager pour invalider après modification |
| `cache_manager` | `db.categories` | ⚠️ **RISQUE** | Même pattern - appels croisés |
| `cache_manager` | `db.members` | ⚠️ **RISQUE** | Même pattern - appels croisés |

**Détail technique:**
```python
# Dans cache_manager.py (ligne 17)
from modules.db.transactions import get_all_hashes, get_all_transactions, get_transactions_count

# Dans db/transactions.py (ligne 160, 291, 340, etc.)
from modules.cache_manager import invalidate_transaction_caches
```

> ⚠️ Ces imports circulaires sont **actuellement tolérés** car `cache_manager` fait ses imports au niveau module, mais les invalidations dans `db/transactions` sont faites à l'intérieur des fonctions (import différé). C'est un pattern risqué qui pourrait échouer lors de refactorings.

### 1.2 Modules avec imports locaux fréquents (Code smell)

Les imports à l'intérieur des fonctions sont souvent des signes de tentative pour éviter les imports circulaires:

| Fichier | Import local | Ligne | Impact |
|---------|-------------|-------|--------|
| `categorization.py` | `modules.db.rules` | 68 | Appelé à chaque catégorisation |
| `categorization.py` | `modules.db.settings` | 24 | Cache transferts internes |
| `categorization.py` | `modules.feature_flags` | 189 | Vérification offline mode |
| `db/transactions.py` | `modules.ingestion` | 63 | Génération tx_hash |
| `db/categories.py` | `modules.cache_manager` | 40,56,68... | Multiple - refacto nécessaire |
| `analytics.py` | `modules.db.connection` | 243 | Import fonctionnel |
| `ui.py` | `modules.constants` | 36 | Import tardif |

---

## 🔗 2. MODULES AVEC COUPLAGE FORT (À REFACTORER)

### 2.1 Top 10 - Trop de dépendances sortantes (High Coupling)

| Rang | Module | Imports | Problème |
|------|--------|---------|----------|
| 1 | `ui.dashboard.sections` | 13 | Mélange UI/métier/AI - trop de responsabilités |
| 2 | `ui.dashboard.customizable_dashboard` | 11 | Idem - UI trop complexe |
| 3 | `ui.validation.main` | 11 | Mélange validation, data_manager, feedback |
| 4 | `ui.config.audit_tools` | 10 | UI config ne devrait pas importer backup_manager |
| 5 | `categorization` | 8 | Cœur métier avec dépendances multiples |
| 6 | `notifications` | 8 | Système transverse avec trop de déps |
| 7 | `ui.assistant.audit_tab` | 8 | Mélange UI, cache, drill-down |
| 8 | `ui.assistant.config_tab` | 8 | Config tab trop grosse |
| 9 | `ui.config.config_dashboard` | 8 | Dashboard de config trop couplé |
| 10 | `ui.components.transaction_drill_down` | 8 | Composant UI avec logique métier |

### 2.2 Top 10 - Trop de dépendances entrantes (God Modules)

| Rang | Module | Importé par | Problème |
|------|--------|-------------|----------|
| 1 | `logger` | 51 modules | ✅ **Normal** - utilitaire universel |
| 2 | `db.transactions` | 30 modules | ⚠️ **GOD MODULE** - trop central |
| 3 | `transaction_types` | 26 modules | ⚠️ **GOD MODULE** - utilisé partout |
| 4 | `db.categories` | 22 modules | ⚠️ Couplage élevé |
| 5 | `db.connection` | 20 modules | ✅ **Acceptable** - base de données |
| 6 | `db.rules` | 19 modules | ⚠️ Couplage élevé |
| 7 | `ui.feedback` | 19 modules | ⚠️ UI transverse |
| 8 | `db.budgets` | 14 modules | Couplage modéré |
| 9 | `utils` | 12 modules | ✅ **Normal** - utilitaire |
| 10 | `db.members` | 11 modules | Couplage modéré |

---

## 📋 3. ANALYSE DÉTAILLÉE DES FICHIERS PRIORITAIRES

### 3.1 `modules/categorization.py`

**Imports:**
- `modules.ai_manager` (ligne 6) - ✅ OK
- `modules.db.categories` (ligne 7) - ⚠️ Pour cache
- `modules.local_ml` (ligne 8) - ✅ OK
- `modules.logger` (ligne 9) - ✅ OK
- `modules.utils` (ligne 10) - ✅ OK
- `modules.db.rules` (ligne 68 - LOCAL) - ⚠️ Import fonctionnel
- `modules.feature_flags` (ligne 189 - LOCAL) - ⚠️ Import fonctionnel

**Problèmes:**
- 2 imports locaux dans les fonctions (code smell)
- Dépendance circulaire indirecte avec `db.rules` via `cache_manager`

### 3.2 `modules/ai_manager.py`

**Imports:**
- `modules.logger` (ligne 11) - ✅ OK
- `modules.exceptions` (ligne 403 - LOCAL) - ✅ OK

**État:** ✅ **BIEN** - Module propre, faible couplage

### 3.3 `modules/db/transactions.py`

**Imports:**
- `modules.db.connection` - ✅ OK
- `modules.db.members` - ⚠️ Dépendance DB interne
- `modules.logger` - ✅ OK
- `modules.ingestion` (ligne 63 - LOCAL) - ⚠️ Import fonctionnel
- `modules.cache_manager` (lignes 160, 291, 340, 559, 570, 580, 600 - LOCAL) - 🚨 **IMPORTS CIRCULAIRES**

**Problèmes:**
- 7 imports locaux de `cache_manager` - signe de couplage circulaire
- Import local de `ingestion` pour éviter un autre cycle

### 3.4 `modules/ui.py`

**Imports:**
- `modules.constants` (ligne 36 - LOCAL) - ⚠️ Import tardif inutile

**État:** ✅ **TRÈS BIEN** - Module UI simple et propre

### 3.5 `modules/utils.py`

**Imports:** Aucun import interne

**État:** ✅ **EXCELLENT** - Module utilitaire autonome

---

## 🎯 4. RECOMMANDATIONS DE DÉCOUPLAGE

### 4.1 Haute Priorité - Résoudre les imports circulaires

#### Problème: `cache_manager` ↔ `db.*`

**Solution: Pattern Observer / Events**

Créer un module `db/events.py` pour la communication:

```python
# modules/db/events.py
"""Event system for database changes."""
from typing import Callable, List

_listeners: dict[str, List[Callable]] = {}

def on_db_change(table_name: str, callback: Callable):
    """Register a callback for DB changes."""
    _listeners.setdefault(table_name, []).append(callback)

def emit_change(table_name: str):
    """Notify all listeners of a change."""
    for callback in _listeners.get(table_name, []):
        callback()
```

**Refactor `db/transactions.py`:**
```python
# Remplacer:
from modules.cache_manager import invalidate_transaction_caches
invalidate_transaction_caches()

# Par:
from modules.db.events import emit_change
emit_change('transactions')
```

**Refactor `cache_manager.py`:**
```python
# Dans __init__ ou au chargement:
from modules.db.events import on_db_change
from modules.db.transactions import get_all_transactions, get_all_hashes

on_db_change('transactions', lambda: get_all_transactions.clear())
on_db_change('transactions', lambda: get_all_hashes.clear())
```

### 4.2 Moyenne Priorité - Réduire le God Module `db.transactions`

**Solution: Séparer les responsabilités**

Créer des modules spécialisés:
- `db/transactions_read.py` - Requêtes SELECT (cache-friendly)
- `db/transactions_write.py` - INSERT/UPDATE/DELETE (avec events)
- `db/transactions_batch.py` - Opérations bulk (déjà existe, étendre)

### 4.3 Moyenne Priorité - Réduire les imports locaux

**Solution: Dependency Injection ou Pattern Strategy**

Pour `categorization.py`:
```python
# Créer une classe avec injection
class CategorizationService:
    def __init__(self, rules_provider, feature_flags_provider):
        self.rules = rules_provider
        self.flags = feature_flags_provider
    
    def categorize(self, label, amount, date):
        # Plus besoin d'imports locaux
        rules = self.rules.get_compiled_rules()
        if self.flags.is_enabled("FORCE_OFFLINE_MODE"):
            return "Inconnu", "offline_forced", 0.0
```

### 4.4 Basse Priorité - Simplifier les UI complexes

**Modules à refactorer:**
- `ui.dashboard.sections` (13 imports) → Split en widgets
- `ui.validation.main` (11 imports) → Pattern MVP/Presenter
- `ui.config.config_dashboard` (8 imports) → Séparer logique UI

---

## 📊 5. MÉTRIQUES DE QUALITÉ

### 5.1 Distribution des imports

```
0 imports:   ████████ 15% (modules simples/utilitaires)
1-2 imports: ████████████████ 30% (bon équilibre)
3-4 imports: ████████████ 22% (acceptable)
5-6 imports: ████████ 15% (attention)
7+ imports:  ██████ 18% (à refactorer)
```

### 5.2 Scores de couplage

| Module | Score | Gravité |
|--------|-------|---------|
| `ui.dashboard.sections` | 13 | 🔴 Critique |
| `ui.validation.main` | 11 | 🔴 Critique |
| `categorization` | 8 | 🟠 Élevé |
| `db.transactions` | 30 imports entrants | 🟠 Élevé |
| `logger` | 51 imports entrants | 🟢 Normal (utilitaire) |
| `utils` | 0/12 | 🟢 Excellent |

---

## ✅ 6. PLAN D'ACTION RECOMMANDÉ

### Phase 1: Sécurité (Semaine 1)
- [ ] Créer `modules/db/events.py` pour le pattern Observer
- [ ] Remplacer les imports circulaires `cache_manager` ↔ `db.*`
- [ ] Ajouter des tests d'import pour détecter les régressions

### Phase 2: Architecture (Semaine 2-3)
- [ ] Extraire `transactions_read.py` et `transactions_write.py`
- [ ] Créer `CategorizationService` avec DI
- [ ] Documenter les nouveaux patterns

### Phase 3: UI (Semaine 4)
- [ ] Refactor `ui.dashboard.sections` en composants
- [ ] Refactor `ui.validation.main` avec pattern Presenter
- [ ] Nettoyer les imports locaux restants

### Phase 4: Outils (Continue)
- [ ] Ajouter un linter d'imports circulaires au CI
- [ ] Surveiller les métriques de couplage
- [ ] Mettre à jour AGENTS.md avec les nouvelles conventions

---

## 📚 7. CONVENTIONS RECOMMANDÉS

### 7.1 Règles d'import

```python
# ✅ CORRECT - Imports au niveau module
from modules.logger import logger
from modules.utils import clean_label

# ⚠️ ÉVITER - Imports dans les fonctions
def ma_fonction():
    from modules.db.rules import get_rules  # Code smell
    ...

# ✅ CORRECT - Utiliser l'injection si nécessaire
class MonService:
    def __init__(self, rules_provider):
        self.rules = rules_provider
```

### 7.2 Architecture en couches

```
┌─────────────────────────────────────┐
│  UI Layer (pages/, modules/ui/)     │
│  - Streamlit components             │
│  - Pas d'accès direct DB            │
├─────────────────────────────────────┤
│  Service Layer (modules/*)          │
│  - categorization, analytics        │
│  - Orchestration métier             │
├─────────────────────────────────────┤
│  Data Layer (modules/db/)           │
│  - CRUD operations                  │
│  - Events pour cache invalidation   │
├─────────────────────────────────────┤
│  Utils (modules/utils.py, logger)   │
│  - Stateless, pas de dépendances    │
└─────────────────────────────────────┘
```

---

## 🔍 8. OUTILS RECOMMANDÉS

### 8.1 Vérification des imports circulaires

```bash
# Installer pylint
pip install pylint

# Vérifier les cycles
pylint --disable=all --enable=R0401 modules/

# Ou utiliser pydeps
pip install pydeps
pydeps modules/ --max-bacon=2 -o imports_graph.svg
```

### 8.2 Tests de non-régression

```python
# tests/test_imports.py
def test_no_circular_imports():
    """Ensure no circular imports exist."""
    import modules.cache_manager
    import modules.db.transactions
    import modules.db.categories
    import modules.db.members
    # Si ça passe, pas d'import circulaire
```

---

**Fin du rapport**  
*Généré automatiquement le 2026-02-18*
