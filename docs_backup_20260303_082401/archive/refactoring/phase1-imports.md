# Phase 1 : Résolution des Imports Circulaires

## Problème identifié

Les modules `cache_manager.py` et `db/*.py` ont des dépendances circulaires:

```
cache_manager.py ──import──▶ db/transactions.py
       ▲                           │
       └──────────import───────────┘
```

Cela force des imports locaux (dans les fonctions) qui:
- Masquent les dépendances
- Compliquent les tests
- Risquent des erreurs runtime

## Analyse détaillée

### Fichiers concernés

```python
# cache_manager.py (lignes 17, 43, 61, 79, 95)
from modules.db.transactions import get_all_hashes, get_all_transactions, ...
from modules.db.rules import get_compiled_learning_rules, ...
from modules.db.categories import get_categories, ...
from modules.db.members import get_members

# db/transactions.py (plusieurs imports locaux)
def some_function():
    from modules.cache_manager import invalidate_transaction_caches  # Local!
```

## Solution proposée : Pattern Observer/Event Bus

### Architecture cible

```
┌─────────────────────────────────────────────────────────┐
│                    Event Bus (Nouveau)                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  cache_manager.py    ──s'abonne──▶  "db.changed"        │
│  db/transactions.py  ──émet──────▶  "db.changed"        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Implémentation

#### 1. Créer `modules/core/events.py`

```python
"""Event bus for decoupled communication between modules."""
from typing import Callable, Dict, List
from functools import wraps

class EventBus:
    """Simple event bus for in-process communication."""
    
    _listeners: Dict[str, List[Callable]] = {}
    
    @classmethod
    def subscribe(cls, event: str, callback: Callable):
        """Subscribe to an event."""
        if event not in cls._listeners:
            cls._listeners[event] = []
        cls._listeners[event].append(callback)
    
    @classmethod
    def emit(cls, event: str, **kwargs):
        """Emit an event to all subscribers."""
        for callback in cls._listeners.get(event, []):
            try:
                callback(**kwargs)
            except Exception as e:
                from modules.logger import logger
                logger.error(f"Event handler error for {event}: {e}")
    
    @classmethod
    def clear(cls):
        """Clear all listeners (for testing)."""
        cls._listeners.clear()


def on_event(event: str):
    """Decorator to subscribe to an event."""
    def decorator(func: Callable):
        EventBus.subscribe(event, func)
        return func
    return decorator
```

#### 2. Modifier `cache_manager.py`

```python
"""Cache management - Version refactorée."""
from functools import wraps
import streamlit as st

from modules.core.events import EventBus, on_event
from modules.logger import logger


# === INVALIDATION PAR ÉVÉNEMENTS ===

@on_event("transactions.changed")
def _invalidate_transactions(**kwargs):
    """Handler pour changement transactions."""
    try:
        # Import local accepté ici car c'est un handler
        from modules.db.transactions import get_all_transactions, get_all_hashes
        get_all_transactions.clear()
        get_all_hashes.clear()
    except Exception as e:
        logger.warning(f"Cache clear error: {e}")


@on_event("rules.changed")
def _invalidate_rules(**kwargs):
    """Handler pour changement règles."""
    try:
        from modules.db.rules import get_compiled_learning_rules
        get_compiled_learning_rules.clear()
    except Exception as e:
        logger.warning(f"Cache clear error: {e}")


# === API PUBLIQUE (pour compatibilité) ===

def invalidate_transaction_caches():
    """Invalidate transaction caches."""
    EventBus.emit("transactions.changed")


def invalidate_rule_caches():
    """Invalidate rule caches."""
    EventBus.emit("rules.changed")


def invalidate_all_caches():
    """Nuclear option."""
    st.cache_data.clear()
```

#### 3. Modifier `db/transactions.py`

```python
"""Transactions DB - Version refactorée."""
from modules.core.events import EventBus
from modules.db.connection import get_db_connection
# SUPPRIMER: from modules.cache_manager import invalidate_transaction_caches


def insert_transaction(data: dict) -> int:
    """Insert transaction and notify cache."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, ...)
            VALUES (?, ?, ?, ...)
        """, (...))
        conn.commit()
        tx_id = cursor.lastrowid
    
    # Émettre événement au lieu d'appeler directement
    EventBus.emit("transactions.changed", tx_id=tx_id)
    return tx_id


def update_transaction(tx_id: int, **fields) -> bool:
    """Update transaction and notify cache."""
    with get_db_connection() as conn:
        # ... update logic ...
        conn.commit()
    
    EventBus.emit("transactions.changed", tx_id=tx_id)
    return True
```

## Plan de migration

### Étape 1 : Créer le Event Bus (30 min)
```bash
# Créer le fichier
touch modules/core/events.py

# Écrire l'implémentation (voir ci-dessus)
```

### Étape 2 : Refactoriser cache_manager (1h)
```bash
# Sauvegarder l'ancien
mv modules/cache_manager.py modules/cache_manager.py.backup

# Créer nouveau avec events
# Copier code de la section 2 ci-dessus
```

### Étape 3 : Refactoriser db/transactions.py (1h30)
```bash
# Remplacer imports locaux par EventBus.emit
# Vérifier tous les points de modification:
grep -n "invalidate_transaction_caches" modules/db/*.py
```

### Étape 4 : Tests (1h)
```bash
# Vérifier que les tests passent toujours
pytest tests/db/test_transactions.py -v

# Test spécifique du event bus
pytest tests/core/test_events.py -v  # À créer
```

## Vérification du succès

```bash
# Vérifier qu'il n'y a plus d'imports locaux
grep -n "from modules.cache_manager import" modules/db/*.py
# Devrait retourner vide

# Vérifier que EventBus est utilisé
grep -n "EventBus.emit" modules/db/*.py
grep -n "EventBus.subscribe" modules/cache_manager.py
```

## Risques et mitigation

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Oublier un import local | Moyen | Élevé | Checklist, grep audit |
| EventBus trop complexe | Faible | Moyen | Garder simple |
| Performance (overhead events) | Faible | Faible | Mesurer avant/après |

## Checklist de validation

- [ ] `modules/core/events.py` créé et testé
- [ ] `cache_manager.py` refactorisé
- [ ] `db/transactions.py` sans imports locaux
- [ ] `db/rules.py` sans imports locaux
- [ ] `db/categories.py` sans imports locaux
- [ ] `db/members.py` sans imports locaux
- [ ] Tous les tests passent
- [ ] Aucun import circulaire détecté par `pylint`

## Code de test pour EventBus

```python
# tests/core/test_events.py
import pytest
from modules.core.events import EventBus, on_event


class TestEventBus:
    def setup_method(self):
        EventBus.clear()
    
    def test_subscribe_and_emit(self):
        """Test basic subscribe/emit."""
        calls = []
        
        def handler(**kwargs):
            calls.append(kwargs)
        
        EventBus.subscribe("test.event", handler)
        EventBus.emit("test.event", data="value")
        
        assert len(calls) == 1
        assert calls[0]["data"] == "value"
    
    def test_decorator(self):
        """Test @on_event decorator."""
        calls = []
        
        @on_event("decorated.event")
        def handler(**kwargs):
            calls.append(kwargs)
        
        EventBus.emit("decorated.event", id=123)
        
        assert len(calls) == 1
        assert calls[0]["id"] == 123
    
    def test_multiple_handlers(self):
        """Test multiple handlers for same event."""
        calls = []
        
        EventBus.subscribe("multi", lambda **_: calls.append(1))
        EventBus.subscribe("multi", lambda **_: calls.append(2))
        
        EventBus.emit("multi")
        
        assert calls == [1, 2]
    
    def test_no_handlers(self):
        """Test emit with no handlers (should not crash)."""
        EventBus.emit("unknown.event")  # Should not raise
```

---

**Estimation totale** : 4 heures  
**Priorité** : P0 (bloquant)  
**Dépendances** : Aucune
