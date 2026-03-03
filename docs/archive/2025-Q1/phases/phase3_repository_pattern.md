# Phase 3: DB Repository Pattern - Specification

> **Status:** Ready for Implementation  
> **Estimated Time:** 2 days  
> **Files to Create:** 15  
> **Lines of Code:** ~3,000

---

## 1. Analysis Summary

### Current DB Layer Statistics

| Module | Functions | Reads | Creates | Updates | Deletes |
|--------|-----------|-------|---------|---------|---------|
| members.py | 24 | 9 | 3 | 2 | 4 |
| transactions.py | 18 | 7 | 2 | 2 | 3 |
| categories.py | 12 | 5 | 2 | 3 | 1 |
| settings.py | 14 | 9 | 1 | 0 | 0 |
| dashboard_layouts.py | 8 | 2 | 1 | 0 | 1 |
| rules.py | 5 | 3 | 1 | 0 | 1 |

### Common Patterns Identified

1. **CRUD Operations**: All modules follow similar patterns
2. **Caching**: Heavy use of `@st.cache_data` decorators
3. **Event Emission**: `EventBus.emit()` after write operations
4. **Filter Building**: `build_filter_clause()` utility used
5. **DataFrame Returns**: Most read operations return pandas DataFrames
6. **Batch Operations**: Separate `transactions_batch.py` module

---

## 2. Target Architecture

```
modules/db_v2/
├── __init__.py
├── base/
│   ├── __init__.py
│   ├── repository.py       # BaseRepository abstract class
│   ├── unit_of_work.py     # UnitOfWork pattern
│   └── pagination.py       # Pagination utilities
├── models/
│   ├── __init__.py
│   ├── transaction.py      # Transaction dataclass
│   ├── category.py         # Category dataclass
│   ├── member.py           # Member dataclass
│   └── budget.py           # Budget dataclass
└── repositories/
    ├── __init__.py
    ├── transaction_repository.py
    ├── category_repository.py
    ├── member_repository.py
    └── budget_repository.py
```

---

## 3. BaseRepository Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any
import pandas as pd

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository implementing CRUD operations.
    
    Type Parameters:
        T: The entity dataclass type
    """
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by primary key."""
        pass
    
    @abstractmethod
    def get_all(
        self, 
        filters: dict[str, Any] = None,
        order_by: str = None,
        limit: int = None,
        offset: int = 0
    ) -> pd.DataFrame:
        """Get all entities with optional filtering."""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> int:
        """Create entity, return new ID."""
        pass
    
    @abstractmethod
    def update(self, entity_id: int, data: dict[str, Any]) -> bool:
        """Update entity fields."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if entity exists."""
        pass
    
    def count(self, filters: dict[str, Any] = None) -> int:
        """Count entities matching filters."""
        pass
    
    def bulk_create(self, entities: list[T]) -> int:
        """Create multiple entities."""
        pass
    
    def bulk_update(self, entity_ids: list[int], data: dict[str, Any]) -> int:
        """Update multiple entities."""
        pass
    
    def bulk_delete(self, entity_ids: list[int]) -> int:
        """Delete multiple entities."""
        pass
```

---

## 4. Entity Models

### Transaction Model

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    """Transaction entity."""
    id: Optional[int] = None
    date: str = ""  # YYYY-MM-DD
    label: str = ""
    amount: float = 0.0
    category: Optional[str] = None
    category_validated: Optional[str] = None
    status: str = "pending"  # pending, validated
    member: Optional[str] = None
    tags: Optional[str] = None  # comma-separated
    tx_hash: Optional[str] = None
    account_label: str = "Unknown"
    beneficiary: Optional[str] = None
    notes: Optional[str] = None
    is_grouped: bool = False
    group_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for DataFrame operations."""
        return {
            'id': self.id,
            'date': self.date,
            'label': self.label,
            'amount': self.amount,
            'category': self.category,
            'category_validated': self.category_validated,
            'status': self.status,
            'member': self.member,
            'tags': self.tags,
            'tx_hash': self.tx_hash,
            'account_label': self.account_label,
        }
    
    @classmethod
    def from_series(cls, series: pd.Series) -> 'Transaction':
        """Create from DataFrame row."""
        return cls(
            id=series.get('id'),
            date=series.get('date', ''),
            label=series.get('label', ''),
            amount=series.get('amount', 0.0),
            # ...
        )
```

### Category Model

```python
@dataclass
class Category:
    """Category entity."""
    id: Optional[int] = None
    name: str = ""
    emoji: str = "📦"
    is_fixed: bool = False
    suggested_tags: Optional[str] = None
    created_at: Optional[datetime] = None
```

### Member Model

```python
@dataclass
class Member:
    """Member entity."""
    id: Optional[int] = None
    name: str = ""
    member_type: str = "HOUSEHOLD"  # HOUSEHOLD, EXTERNAL
    created_at: Optional[datetime] = None
```

---

## 5. Repository Implementations

### TransactionRepository

```python
from modules.db_v2.base.repository import BaseRepository
from modules.db_v2.models.transaction import Transaction
from modules.db.connection import get_db_connection
from modules.core.events import EventBus
import streamlit as st
import pandas as pd

class TransactionRepository(BaseRepository[Transaction]):
    """Repository for transaction operations."""
    
    _table = "transactions"
    _entity_class = Transaction
    
    def get_by_id(self, entity_id: int) -> Optional[Transaction]:
        """Get transaction by ID."""
        with get_db_connection() as conn:
            df = pd.read_sql(
                f"SELECT * FROM {self._table} WHERE id = ?",
                conn, params=(entity_id,)
            )
            if df.empty:
                return None
            return Transaction.from_series(df.iloc[0])
    
    def get_by_hash(self, tx_hash: str) -> Optional[Transaction]:
        """Get transaction by hash."""
        with get_db_connection() as conn:
            df = pd.read_sql(
                f"SELECT * FROM {self._table} WHERE tx_hash = ?",
                conn, params=(tx_hash,)
            )
            if df.empty:
                return None
            return Transaction.from_series(df.iloc[0])
    
    @st.cache_data(ttl=60)
    def get_all(
        self,
        filters: dict = None,
        order_by: str = "date DESC",
        limit: int = None,
        offset: int = 0
    ) -> pd.DataFrame:
        """Get all transactions with filtering."""
        query = f"SELECT * FROM {self._table} WHERE 1=1"
        params = []
        
        if filters:
            # Build filter clause
            pass
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        with get_db_connection() as conn:
            return pd.read_sql(query, conn, params=params)
    
    def get_pending(self, limit: int = None) -> pd.DataFrame:
        """Get pending transactions."""
        return self.get_all(
            filters={"status": "pending"},
            order_by="date DESC",
            limit=limit
        )
    
    def create(self, entity: Transaction) -> int:
        """Create transaction."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions 
                (date, label, amount, category, status, member, tags, tx_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.date, entity.label, entity.amount,
                entity.category, entity.status, entity.member,
                entity.tags, entity.tx_hash
            ))
            conn.commit()
            new_id = cursor.lastrowid
            
        EventBus.emit("transactions.changed", id=new_id, action="created")
        return new_id
    
    def update(self, entity_id: int, data: dict) -> bool:
        """Update transaction fields."""
        if not data:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [entity_id]
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table} SET {set_clause} WHERE id = ?",
                values
            )
            conn.commit()
            updated = cursor.rowcount > 0
            
        if updated:
            EventBus.emit("transactions.changed", id=entity_id, action="updated")
        return updated
    
    def update_category(self, entity_id: int, category: str) -> bool:
        """Update transaction category."""
        return self.update(entity_id, {
            "category": category,
            "category_validated": category
        })
    
    def update_tags(self, entity_id: int, tags: list[str]) -> bool:
        """Update transaction tags."""
        tags_str = ", ".join(tags) if tags else None
        return self.update(entity_id, {"tags": tags_str})
    
    def delete(self, entity_id: int) -> bool:
        """Delete transaction."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self._table} WHERE id = ?",
                (entity_id,)
            )
            conn.commit()
            deleted = cursor.rowcount > 0
            
        if deleted:
            EventBus.emit("transactions.changed", id=entity_id, action="deleted")
        return deleted
    
    def exists(self, entity_id: int) -> bool:
        """Check if transaction exists."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM {self._table} WHERE id = ?",
                (entity_id,)
            )
            return cursor.fetchone() is not None
    
    def bulk_create(self, entities: list[Transaction]) -> int:
        """Create multiple transactions."""
        # Implementation with executemany
        pass
```

---

## 6. Unit of Work Pattern

```python
from contextlib import contextmanager
from typing import Optional
from modules.db.connection import get_db_connection

class UnitOfWork:
    """
    Unit of Work pattern for transaction management.
    
    Ensures atomic operations across multiple repositories.
    """
    
    def __init__(self, connection=None):
        self._conn = connection
        self._owns_connection = connection is None
        self._repositories = {}
    
    def __enter__(self):
        if self._owns_connection:
            self._conn = get_db_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
        
        if self._owns_connection:
            self._conn.close()
    
    @property
    def transactions(self) -> 'TransactionRepository':
        """Get transaction repository."""
        if 'transactions' not in self._repositories:
            from modules.db_v2.repositories.transaction_repository import TransactionRepository
            self._repositories['transactions'] = TransactionRepository(self._conn)
        return self._repositories['transactions']
    
    @property
    def categories(self) -> 'CategoryRepository':
        """Get category repository."""
        if 'categories' not in self._repositories:
            from modules.db_v2.repositories.category_repository import CategoryRepository
            self._repositories['categories'] = CategoryRepository(self._conn)
        return self._repositories['categories']
    
    @property
    def members(self) -> 'MemberRepository':
        """Get member repository."""
        if 'members' not in self._repositories:
            from modules.db_v2.repositories.member_repository import MemberRepository
            self._repositories['members'] = MemberRepository(self._conn)
        return self._repositories['members']


# Convenience function
@contextmanager
def unit_of_work():
    """Create a Unit of Work context."""
    with UnitOfWork() as uow:
        yield uow
```

---

## 7. Migration Plan

### Step 1: Create Base Infrastructure
1. Create `modules/db_v2/base/repository.py`
2. Create `modules/db_v2/base/unit_of_work.py`
3. Create `modules/db_v2/models/` dataclasses

### Step 2: Implement Repositories
1. `TransactionRepository` - Most complex, ~20 methods
2. `CategoryRepository` - Medium complexity
3. `MemberRepository` - High complexity (mappings, types)
4. `BudgetRepository` - Simple

### Step 3: Legacy Wrappers
Update existing functions to use repositories:

```python
# In modules/db/transactions.py
from modules.db_v2.repositories.transaction_repository import TransactionRepository

def get_transaction_by_id(tx_id: int):
    """Legacy wrapper - delegates to repository."""
    warnings.warn("Use TransactionRepository", DeprecationWarning)
    repo = TransactionRepository()
    return repo.get_by_id(tx_id)
```

### Step 4: Update Callers (Progressive)
Migrate one module at a time:
- Week 1: Pages using transactions
- Week 2: Pages using categories
- Week 3: Pages using members
- Week 4: Cleanup

---

## 8. Testing Strategy

```python
# tests/db_v2/test_transaction_repository.py
import pytest
from modules.db_v2.repositories.transaction_repository import TransactionRepository
from modules.db_v2.models.transaction import Transaction

class TestTransactionRepository:
    @pytest.fixture
    def repo(self, temp_db):
        return TransactionRepository()
    
    def test_create_and_get(self, repo):
        tx = Transaction(date="2024-01-01", label="Test", amount=100.0)
        tx_id = repo.create(tx)
        
        retrieved = repo.get_by_id(tx_id)
        assert retrieved is not None
        assert retrieved.label == "Test"
    
    def test_update_category(self, repo):
        tx = Transaction(date="2024-01-01", label="Test", amount=100.0)
        tx_id = repo.create(tx)
        
        repo.update_category(tx_id, "Food")
        
        retrieved = repo.get_by_id(tx_id)
        assert retrieved.category == "Food"
        assert retrieved.category_validated == "Food"
```

---

## 9. Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Testability** | Hard to mock DB | Easy repository mocking |
| **Consistency** | Ad-hoc SQL | Standardized CRUD |
| **Type Safety** | DataFrame returns | Typed entities |
| **Transactions** | Manual commit | Unit of Work |
| **DB Migration** | SQLite-specific | Abstracted layer |

---

## 10. Files to Create

| File | Lines | Priority |
|------|-------|----------|
| `base/repository.py` | 80 | 🔴 High |
| `base/unit_of_work.py` | 60 | 🔴 High |
| `models/transaction.py` | 50 | 🔴 High |
| `models/category.py` | 30 | 🔴 High |
| `models/member.py` | 30 | 🔴 High |
| `repositories/transaction_repository.py` | 200 | 🔴 High |
| `repositories/category_repository.py` | 120 | 🟡 Medium |
| `repositories/member_repository.py` | 150 | 🟡 Medium |
| `repositories/budget_repository.py` | 80 | 🟢 Low |
| `__init__.py` exports | 50 | 🟡 Medium |
| Legacy wrappers | 200 | 🟡 Medium |
| **Total** | **~1,250** | |

---

## Next Steps

1. ✅ Review this specification
2. ✅ Approve approach
3. 🚧 Implement base infrastructure
4. 🚧 Implement TransactionRepository
5. 🚧 Implement other repositories
6. 🚧 Create legacy wrappers
7. 🚧 Update implementation_plan.md status
