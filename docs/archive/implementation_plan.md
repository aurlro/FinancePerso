# Plan d'Implementation - Refactoring FinancePerso

> **Version:** 1.0  
> **Date:** 2026-02-20  
> **Projet:** FinancePerso v5.2.0

## Vue d'ensemble

Ce document décrit le plan de refactoring complet de l'application FinancePerso pour améliorer la maintenabilité, la testabilité et la qualité du code.

---

## Phase 1: Fondations ✅ COMPLETE

### Objectifs
- Résoudre les imports circulaires
- Mettre en place l'architecture EventBus
- Créer les modules core

### Livrables

#### 1.1 EventBus Pattern (`modules/core/events.py`)
```python
class EventBus:
    """Système de communication pub/sub découplée."""
    
    def subscribe(self, event_name: str, handler: Callable) -> None
    def emit(self, event_name: str, **kwargs) -> None
    def unsubscribe(self, event_name: str, handler: Callable) -> bool

def on_event(event_name: str) -> Callable
```

#### 1.2 Cache Manager Refactorisé
- Remplacement des imports directs par des souscriptions EventBus
- Events: `transactions.changed`, `categories.changed`, `members.changed`, etc.

#### 1.3 Module Update Refactorisé
- `update_manager.py` (858 lignes) → 7 modules dans `modules/update/`
- Structure: version, changelog, git, manager

### Résultats
- ✅ 3 imports circulaires résolus
- ✅ 20 nouveaux modules créés
- ✅ Compatibilité arrière maintenue

---

## Phase 2: Restructuration UI - Atomic Design ✅ COMPLETE

### Objectifs
- Migrer de `modules/ui/` vers `modules/ui_v2/` avec pattern Atomic Design
- Créer des composants réutilisables et cohérents
- Maintenir la backward compatibility

### Structure Atomic Design

```
modules/ui_v2/
├── atoms/              # Éléments indivisibles
├── molecules/          # Combinaisons d'atoms
├── organisms/          # Sections fonctionnelles
├── widgets/            # Widgets métier (dashboard)
└── templates/          # Layouts de page
```

### Livrables

#### 2.1 Atoms (3 fichiers, 267 lignes)
| Fichier | Description |
|---------|-------------|
| `icons.py` | `IconSet` enum (80+ icônes standardisées) |
| `colors.py` | `FeedbackColor`, `PriorityColor`, `ColorScheme` |
| `__init__.py` | Exports |

**Usage:**
```python
from modules.ui_v2.atoms.icons import IconSet
from modules.ui_v2.atoms.colors import FeedbackColor, ColorScheme
```

#### 2.2 Molecules (8+ fichiers, ~1,800 lignes)
| Fichier | Description |
|---------|-------------|
| `toasts.py` | 6 variantes de toasts (success, error, warning, info, loading, custom) |
| `banners.py` | 5 niveaux de banners persistants |
| `badges.py` | Status badges, priority badges, type badges |
| `components/` | 20+ composants réutilisables |

**Components migrés:**
- `confirm_dialog.py` (176 lignes)
- `empty_states.py` (211 lignes)
- `loading_states.py` (272 lignes)
- `quick_actions.py` (458 lignes)
- `smart_actions.py` (324 lignes)
- `tags/tag_manager.py` (480 lignes)
- `tags/tag_selector_smart.py` (343 lignes)
- `transactions/drill_down.py` (535 lignes)
- `widgets/savings_goals.py` (346 lignes)

#### 2.3 Organisms (15+ fichiers, ~3,500 lignes)
| Fichier | Description |
|---------|-------------|
| `dialogs.py` | 5 types de modals (confirm_delete, confirm_dialog, etc.) |
| `flash_messages.py` | Système de messages flash avec timeout |
| `notifications/` | 7 fichiers pour le système de notifications |
| `config/` | 10 fichiers pour la configuration |

**Config migrée:**
- `member_management.py` (606 lignes) - avec impact analysis
- `category_management.py` (295 lignes) - avec emoji selector
- `audit_tools.py` (506 lignes)
- `api_settings.py` (274 lignes)
- `backup_restore.py` (242 lignes)
- `data_operations.py` (277 lignes)
- `notifications.py` (276 lignes)
- `tags_rules.py` (208 lignes)

#### 2.4 Widgets Dashboard (10 fichiers, ~2,500 lignes)
| Fichier | Description |
|---------|-------------|
| `kpi_cards.py` | KPI cards avec trends |
| `category_charts.py` | Bar charts, pie charts, stacked charts |
| `evolution_chart.py` | Line charts d'évolution |
| `budget_tracker.py` | Suivi des budgets |
| `top_expenses.py` | Top dépenses |
| `smart_recommendations.py` | Recommandations intelligentes |
| `ai_insights.py` | Insights IA |
| `filters.py` | Filtres du dashboard |

#### 2.5 Templates (5 fichiers, ~2,200 lignes)
| Fichier | Description |
|---------|-------------|
| `layouts.py` | `WidgetType` enum, `LAYOUT_TEMPLATES` (4 templates) |
| `manager.py` | `DashboardLayoutManager` avec mode Preview |
| `renderer.py` | `render_dashboard_configurator()`, `render_customizable_overview()` |
| `legacy.py` | Backward compatibility |

### Modules God migrés

| Module | Avant | Après |
|--------|-------|-------|
| `feedback.py` | 671 lignes | Wrapper legacy (89 lignes) |
| `customizable_dashboard.py` | 718 lignes | Wrapper legacy (115 lignes) |
| `notifications/components.py` | 646 lignes | Wrapper legacy (89 lignes) |

### API Modernisée

```python
# NOUVEAU (recommandé)
from modules.ui_v2.atoms.icons import IconSet
from modules.ui_v2.molecules.toasts import toast_success
from modules.ui_v2.organisms.dialogs import confirm_delete
from modules.ui_v2.templates import DashboardLayoutManager

# ANCIEN (deprecated mais fonctionnel)
from modules.ui.feedback import toast_success  # ⚠️ DeprecationWarning
```

### Résultats
- ✅ 69 fichiers créés
- ✅ 13,721 lignes migrées
- ✅ Backward compatibility complète
- ✅ Design tokens centralisés (IconSet, ColorScheme)

---

## Phase 3: DB Repository Pattern 🚧 PLANNED

### Objectifs
- Unifier l'accès aux données avec le pattern Repository
- Réduire la duplication de code SQL
- Faciliter les tests unitaires (mocking)
- Préparer pour une future migration de base de données

### Architecture cible

```
modules/db/
├── base/                    # NEW
│   ├── __init__.py
│   ├── repository.py        # BaseRepository abstract class
│   ├── unit_of_work.py      # Transaction management
│   └── pagination.py        # Pagination utilities
├── repositories/            # NEW
│   ├── __init__.py
│   ├── transaction_repository.py
│   ├── category_repository.py
│   ├── member_repository.py
│   └── budget_repository.py
├── connection.py            # EXISTING
├── migrations.py            # EXISTING
└── legacy/                  # EXISTING (current modules)
```

### BaseRepository Interface

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional
import pandas as pd

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository with CRUD operations."""
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self, filters: dict = None, limit: int = None, offset: int = 0) -> pd.DataFrame:
        """Get all entities with optional filtering and pagination."""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> int:
        """Create entity, return new ID."""
        pass
    
    @abstractmethod
    def update(self, id: int, entity: T) -> bool:
        """Update entity by ID."""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def exists(self, id: int) -> bool:
        """Check if entity exists."""
        pass
    
    def count(self, filters: dict = None) -> int:
        """Count entities with optional filters."""
        pass
```

### TransactionRepository

```python
from modules.db.base.repository import BaseRepository
from modules.db.models import Transaction  # NEW dataclass

class TransactionRepository(BaseRepository[Transaction]):
    """Repository for transaction operations."""
    
    def get_by_id(self, tx_id: int) -> Optional[Transaction]:
        # Implementation
        
    def get_by_hash(self, tx_hash: str) -> Optional[Transaction]:
        # Specific to transactions
        
    def get_pending(self, limit: int = None) -> pd.DataFrame:
        # Specific to transactions
        
    def bulk_insert(self, transactions: list[Transaction]) -> int:
        # Batch insert
        
    def update_category(self, tx_id: int, category: str) -> bool:
        # Domain-specific operation
        
    def update_tags(self, tx_id: int, tags: list[str]) -> bool:
        # Domain-specific operation
```

### Unit of Work Pattern

```python
from contextlib import contextmanager
from modules.db.base.unit_of_work import UnitOfWork

@contextmanager
def unit_of_work():
    """Manage transactions atomically."""
    conn = get_db_connection()
    try:
        yield UnitOfWork(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Usage
with unit_of_work() as uow:
    tx_repo = uow.transactions
    cat_repo = uow.categories
    
    tx = tx_repo.get_by_id(1)
    tx.category = "New Category"
    tx_repo.update(tx.id, tx)
    
    # Automatic commit if no exception
```

### Migration progressive

```python
# Phase 3.1: Create repositories alongside existing code
# modules/db/repositories/transaction_repository.py

# Phase 3.2: Migrate one module at a time
# OLD: from modules.db.transactions import get_transaction_by_id
# NEW: from modules.db.repositories import TransactionRepository

# Phase 3.3: Deprecate old modules
# Add deprecation warnings to old functions

# Phase 3.4: Remove old modules (v6.0)
```

### Livrables

1. **Base Repository** (`modules/db/base/repository.py`)
   - Interface abstraite CRUD
   - Support pagination
   - Support filtrage générique

2. **Unit of Work** (`modules/db/base/unit_of_work.py`)
   - Gestion des transactions
   - Coordination des repositories
   - Rollback automatique

3. **Entity Models** (`modules/db/models/`)
   - `Transaction` dataclass
   - `Category` dataclass
   - `Member` dataclass
   - Converters to/from DataFrame

4. **Concrete Repositories**
   - `TransactionRepository`
   - `CategoryRepository`
   - `MemberRepository`
   - `BudgetRepository`

5. **Legacy Wrappers**
   - Fonctions existantes délèguent aux repositories
   - Deprecation warnings

### Résultats attendus
- 📦 Code métier découplé de SQLite
- 🧪 Tests unitaires plus faciles (mock repositories)
- 🔄 Migration base de données facilitée
- 📚 API cohérente et documentée

---

## Phase 4: Modernisation API Google 🚧 PLANNED

### Objectifs
- Migrer de `google.generativeai` vers `google.genai`
- Améliorer les type hints
- Standardiser les appels API

### Changements

```python
# OLD (deprecated)
import google.generativeai as genai
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content(prompt)

# NEW (modern)
from google import genai
client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=prompt
)
```

### Fichiers concernés
- `modules/ai_manager.py`
- `modules/ai/*.py` (tous les modules IA)

---

## Phase 5: Optimisation & Documentation 🚧 PLANNED

### Objectifs
- Améliorer les performances
- Compléter la documentation
- Ajouter des tests

### Livrables
- [ ] Documentation technique complète
- [ ] Tests unitaires (couverture > 80%)
- [ ] Tests d'intégration
- [ ] Guide de contribution
- [ ] Benchmarks de performance

---

## Timeline

| Phase | Statut | Fichiers | Lignes | Estimation |
|-------|--------|----------|--------|------------|
| Phase 1: Fondations | ✅ Done | 20 | ~2,000 | 1 jour |
| Phase 2: UI Atomic Design | ✅ Done | 69 | ~13,700 | 2 jours |
| Phase 3: DB Repository | 🚧 Planned | 15 | ~3,000 | 2 jours |
| Phase 4: API Google | 🚧 Planned | 5 | ~500 | 1 jour |
| Phase 5: Optimisation | 🚧 Planned | - | - | 2 jours |

---

## Notes

### Backward Compatibility
Toutes les phases maintiennent la backward compatibility:
- Wrappers legacy avec `DeprecationWarning`
- Migration progressive des imports
- Documentation des changements

### Tests
À chaque phase:
```bash
pytest tests/ -v --cov=modules --cov-report=html
```

### Qualité
```bash
black modules/ pages/ tests/
ruff check modules/ pages/ tests/
```

---

## Références

- [Atomic Design](https://atomicdesign.bradfrost.com/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Unit of Work Pattern](https://martinfowler.com/eaaCatalog/unitOfWork.html)
- [Google GenAI Migration](https://github.com/google-gemini/deprecated-generative-ai-python)
