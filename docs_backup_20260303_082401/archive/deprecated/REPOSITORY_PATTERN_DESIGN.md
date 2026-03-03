# Repository Pattern Implementation Design

## Executive Summary

This document provides a comprehensive analysis of the FinancePerso database layer (`modules/db/`) and designs a Repository pattern implementation to improve code organization, testability, and maintainability.

**Current State**: 17 database modules with ~2,500 lines of code using procedural function-based approach.  
**Target State**: Clean Repository pattern with entity models, base repository class, and specific repositories per entity.

---

## 1. Analysis of Current Database Layer

### 1.1 Files Analyzed

| File | Lines | Purpose |
|------|-------|---------|
| `connection.py` | 91 | Connection management, filter builder, cache clearing |
| `transactions.py` | 595 | Core transaction CRUD + business operations |
| `transactions_batch.py` | 360 | Batch operations, atomic transactions |
| `categories.py` | 355 | Category management, merge operations |
| `members.py` | 650 | Member management, mappings, detection |
| `budgets.py` | 69 | Simple budget CRUD |
| `rules.py` | 150 | Learning rules management |
| `tags.py` | 179 | Tag extraction and management |
| `settings.py` | 252 | Key-value settings storage |
| `migrations.py` | 364 | Schema initialization and migrations |

### 1.2 Common CRUD Patterns Found

#### SELECT Patterns

```python
# Pattern 1: Simple list with caching
@st.cache_data(ttl=300)
def get_entities() -> list[str] | pd.DataFrame:
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM table ORDER BY name", conn)

# Pattern 2: Get by ID (common in all modules)
def get_by_id(entity_id: int) -> dict | None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM table WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

# Pattern 3: Get with dynamic filters
def get_all_transactions(
    limit: int = None, 
    offset: int = 0, 
    filters: dict = None, 
    order_by: str = "date DESC"
) -> pd.DataFrame:
    query = "SELECT * FROM transactions WHERE 1=1"
    where_clause, params = build_filter_clause(filters)
    query += where_clause
    # ... pagination

# Pattern 4: Get dictionary mapping (name -> value)
@st.cache_data(ttl=300)
def get_member_mappings() -> dict[str, str]:
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT card_suffix, member_name FROM member_mappings", conn)
        return dict(zip(df["card_suffix"], df["member_name"]))
```

#### INSERT Patterns

```python
# Pattern 1: Simple insert with integrity check
def add_entity(name: str, ...) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO table (col1, col2) VALUES (?, ?)",
                (name, ...)
            )
            conn.commit()
            EventBus.emit("entities.changed", action="added")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Entity '{name}' already exists")
            return False

# Pattern 2: Insert or Replace (upsert)
cursor.execute(
    "INSERT OR REPLACE INTO table (col1, col2) VALUES (?, ?)",
    (val1, val2)
)

# Pattern 3: Batch insert with executemany()
def save_transactions(df: pd.DataFrame) -> tuple[int, int]:
    # ... prepare rows_to_insert
    cursor.executemany(
        "INSERT INTO transactions (cols) VALUES (placeholders)",
        rows_to_insert
    )
```

#### UPDATE Patterns

```python
# Pattern 1: Single field update
def update_field(entity_id: int, new_value: str) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE table SET field = ? WHERE id = ?", (new_value, entity_id))
        conn.commit()
    EventBus.emit("entities.changed")

# Pattern 2: Dynamic field update
def bulk_update_transaction_status(
    tx_ids: list[int],
    new_category: str,
    tags: str = None,
    beneficiary: str = None,
    notes: str = None,
) -> None:
    set_clauses = ["category_validated = ?", "status = 'validated'"]
    params = [new_category]
    
    if tags is not None:
        set_clauses.append("tags = ?")
        params.append(tags)
    # ... more fields
    
    query = f"UPDATE transactions SET {', '.join(set_clauses)} WHERE id IN ({placeholders})"
```

#### DELETE Patterns

```python
# Pattern 1: Single delete
def delete_entity(entity_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM table WHERE id = ?", (entity_id,))
        conn.commit()
        return cursor.rowcount > 0

# Pattern 2: Delete with IN clause
def delete_transactions_by_period(month_str: str) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE strftime('%Y-%m', date) = ?", (month_str,))
        deleted_count = cursor.rowcount
        conn.commit()
    EventBus.emit("transactions.batch_changed", ...)
    return deleted_count
```

### 1.3 Specific Business Operations by Entity

#### Transactions (transactions.py)

| Operation | Purpose |
|-----------|---------|
| `save_transactions()` | Import with duplicate detection using Count-Based Verification |
| `transaction_exists()` | Check existence by tx_hash |
| `get_pending_transactions()` | Get unvalidated transactions for UI |
| `get_duplicates_report()` | Find duplicate transactions |
| `bulk_update_transaction_status()` | Validate transactions with undo logging |
| `undo_last_action()` | Revert last validation |
| `apply_member_mappings_to_pending()` | Auto-assign members |
| `mark_transaction_as_ungrouped()` | Exclude from smart grouping |
| `add_tag_to_transactions()` | Add tags without overwriting |

#### Categories (categories.py)

| Operation | Purpose |
|-----------|---------|
| `get_categories_with_emojis()` | Get emoji mapping |
| `get_categories_suggested_tags()` | Get tag suggestions per category |
| `get_all_categories_including_ghosts()` | Find orphaned categories |
| `add_tag_to_category()` | Append tag to suggestions |
| `merge_categories()` | Complex merge: transactions, rules, budgets |

#### Members (members.py)

| Operation | Purpose |
|-----------|---------|
| `rename_member()` | Propagate rename across transactions, mappings |
| `get_orphan_labels()` | Find unknown member values |
| `delete_and_replace_label()` | Replace label across tables |
| `detect_member_from_content()` | Smart detection with cascading strategy |
| `get_member_mappings()` / `get_account_member_mappings()` | Card/account mappings |
| `get_unknown_member_stats()` | Analytics on unidentified |
| `repair_unknown_members()` | Bulk repair with default |
| `analyze_unknown_patterns()` | Suggest improvements |

#### Rules (rules.py)

| Operation | Purpose |
|-----------|---------|
| `get_compiled_learning_rules()` | Pre-compiled regex for performance |
| `get_rules_for_category()` | Filter by category |
| Pattern validation | ReDoS protection via `validate_regex_pattern()` |

### 1.4 Filter Patterns

The `build_filter_clause()` function in `connection.py` provides a flexible filtering system:

```python
# Supported filter formats:
filters = {
    "status": "validated",           # Exact match: "status = ?"
    "amount": (">", 100),            # Operator: "amount > ?"
    "label": ("LIKE", "%CARREFOUR%") # Pattern matching
}

# Usage:
where_clause, params = build_filter_clause(filters)
# Returns: (" AND status = ? AND amount > ?", ["validated", 100])
```

**Extensions needed for Repository pattern:**
- Support for OR conditions
- Support for NULL checks
- Support for date ranges
- Support for IN clauses

### 1.5 Batch Operations

| Module | Function | Description |
|--------|----------|-------------|
| `transactions.py` | `save_transactions()` | Bulk insert with deduplication |
| `transactions.py` | `bulk_update_transaction_status()` | Update + history logging |
| `transactions_batch.py` | `batch_update_transactions_with_rule()` | Update + rule creation |
| `transactions_batch.py` | `merge_categories_atomic()` | Multi-table atomic merge |
| `transactions_batch.py` | `bulk_tag_transactions()` | Tag manipulation |
| `transactions_batch.py` | `batch_delete_transactions()` | Delete with backup |
| `categories.py` | `merge_categories()` | Complex cross-table merge |
| `members.py` | `repair_unknown_members()` | Bulk repair |

### 1.6 Caching Usage

All cached functions use `@st.cache_data()` decorator:

| Function | TTL | Purpose |
|----------|-----|---------|
| `get_categories()` | 300s | Category list dropdown |
| `get_categories_with_emojis()` | 300s | Emoji display |
| `get_categories_suggested_tags()` | 300s | Tag suggestions |
| `get_categories_df()` | 1h | Full category data |
| `get_members()` | 300s | Member list |
| `get_member_mappings()` | 300s | Card suffix mapping |
| `get_account_member_mappings()` | 300s | Account mapping |
| `get_learning_rules()` | 1h | Rules management |
| `get_compiled_learning_rules()` | ∞ | Pre-compiled patterns |
| `get_all_transactions()` | ∞ | Main transaction grid |
| `get_pending_transactions()` | 1h | Validation page |
| `get_duplicates_report()` | 1h | Deduplication UI |
| `get_all_tags()` | 300s | Tag cloud |

**Cache invalidation**: `clear_db_cache()` calls `st.cache_data.clear()`

### 1.7 Event Emission Points

All database modifications emit events via `EventBus`:

| Event | Modules | Trigger |
|-------|---------|---------|
| `transactions.changed` | transactions.py | Single update, delete, undo |
| `transactions.batch_changed` | transactions.py | Bulk import, delete by period |
| `categories.changed` | categories.py | CRUD, merge |
| `members.changed` | members.py | CRUD, rename, mappings |
| `tags.changed` | tags.py | Tag removal |

---

## 2. Entity Models Design

### 2.1 Base Entity

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any

@dataclass
class BaseEntity:
    """Base class for all entities."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary for database operations."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                result[key] = value
        return result
    
    @classmethod
    def from_row(cls, row: tuple | sqlite3.Row) -> "BaseEntity":
        """Create entity from database row."""
        raise NotImplementedError
```

### 2.2 Transaction Entity

```python
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"

@dataclass
class Transaction:
    """Transaction entity representing a bank transaction."""
    # Required fields
    date: date
    label: str
    amount: Decimal
    
    # Optional fields with defaults
    id: Optional[int] = None
    original_category: Optional[str] = None
    category_validated: Optional[str] = None
    account_id: Optional[str] = None
    account_label: str = "Compte Principal"
    status: TransactionStatus = TransactionStatus.PENDING
    ai_confidence: Optional[float] = None
    
    # Member-related
    member: str = "Inconnu"
    beneficiary: Optional[str] = None
    card_suffix: Optional[str] = None
    
    # Content
    tags: Optional[str] = None  # Comma-separated
    notes: Optional[str] = None
    comment: Optional[str] = None
    
    # Technical
    tx_hash: Optional[str] = None
    is_manually_ungrouped: bool = False
    import_date: Optional[datetime] = None
    
    # Computed properties
    @property
    def is_validated(self) -> bool:
        return self.status == TransactionStatus.VALIDATED
    
    @property
    def is_expense(self) -> bool:
        return self.amount < 0
    
    @property
    def is_income(self) -> bool:
        return self.amount > 0
    
    @property
    def tag_list(self) -> list[str]:
        """Parse tags string into list."""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the transaction."""
        tags = self.tag_list
        if tag not in tags:
            tags.append(tag)
            self.tags = ", ".join(tags)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the transaction."""
        tags = self.tag_list
        if tag in tags:
            tags.remove(tag)
            self.tags = ", ".join(tags) if tags else None
```

### 2.3 Category Entity

```python
@dataclass
class Category:
    """Category entity for transaction classification."""
    id: Optional[int] = None
    name: str = ""
    emoji: str = "🏷️"
    is_fixed: bool = False  # Monthly vs variable expenses
    suggested_tags: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @property
    def tag_list(self) -> list[str]:
        if not self.suggested_tags:
            return []
        return [t.strip() for t in self.suggested_tags.split(",") if t.strip()]
    
    def add_suggested_tag(self, tag: str) -> None:
        tags = self.tag_list
        if tag not in tags:
            tags.append(tag)
            self.suggested_tags = ", ".join(sorted(tags))
```

### 2.4 Member Entity

```python
from modules.constants import MemberType

@dataclass
class Member:
    """Member entity representing a household member or external entity."""
    id: Optional[int] = None
    name: str = ""
    member_type: str = MemberType.HOUSEHOLD
    created_at: Optional[datetime] = None
    
    @property
    def is_household(self) -> bool:
        return self.member_type == MemberType.HOUSEHOLD
    
    @property
    def is_external(self) -> bool:
        return self.member_type == MemberType.EXTERNAL

@dataclass
class MemberMapping:
    """Mapping between card suffix and member."""
    id: Optional[int] = None
    card_suffix: str = ""
    member_name: str = ""
    created_at: Optional[datetime] = None

@dataclass
class AccountMemberMapping:
    """Default member for an account."""
    id: Optional[int] = None
    account_label: str = ""
    member_name: str = ""
    created_at: Optional[datetime] = None
```

### 2.5 Budget Entity

```python
@dataclass
class Budget:
    """Budget entity for category budget tracking."""
    category: str  # Primary key
    amount: Decimal
    updated_at: Optional[datetime] = None
    
    @property
    def is_set(self) -> bool:
        return self.amount > 0
```

### 2.6 Rule Entity

```python
import re
from dataclasses import field

@dataclass
class LearningRule:
    """Learning rule entity for automatic categorization."""
    id: Optional[int] = None
    pattern: str = ""
    category: str = ""
    priority: int = 1
    created_at: Optional[datetime] = None
    
    # Compiled pattern (not persisted)
    _compiled: Optional[re.Pattern] = field(default=None, repr=False, compare=False)
    
    def compile(self) -> Optional[re.Pattern]:
        """Compile regex pattern for matching."""
        if self._compiled is None:
            try:
                self._compiled = re.compile(self.pattern, re.IGNORECASE)
            except re.error:
                return None
        return self._compiled
    
    def matches(self, text: str) -> bool:
        """Check if text matches the pattern."""
        pattern = self.compile()
        if pattern:
            return bool(pattern.search(text))
        # Fallback to simple string matching
        return self.pattern.upper() in text.upper()
```

---

## 3. Repository Interface Design

### 3.1 Generic Type Variables

```python
from typing import TypeVar, Generic, Optional, Union
import pandas as pd

T = TypeVar('T')  # Entity type
ID = TypeVar('ID', int, str)  # ID type (int for most, str for budgets)
```

### 3.2 Filter Specification

```python
from dataclasses import dataclass
from typing import Any, Literal
from datetime import date, datetime

@dataclass
class FilterSpec:
    """Specification for a single filter condition."""
    column: str
    operator: Literal["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "IS NULL", "IS NOT NULL"]
    value: Any = None
    
    def to_sql(self) -> tuple[str, list]:
        """Convert to SQL clause and parameters."""
        if self.operator in ("IS NULL", "IS NOT NULL"):
            return f" AND {self.column} {self.operator}", []
        if self.operator == "IN":
            placeholders = ", ".join(["?"] * len(self.value))
            return f" AND {self.column} IN ({placeholders})", list(self.value)
        return f" AND {self.column} {self.operator} ?", [self.value]


class FilterBuilder:
    """Builder for complex filter conditions."""
    
    def __init__(self):
        self.filters: list[FilterSpec] = []
    
    def eq(self, column: str, value: Any) -> "FilterBuilder":
        self.filters.append(FilterSpec(column, "=", value))
        return self
    
    def gt(self, column: str, value: Any) -> "FilterBuilder":
        self.filters.append(FilterSpec(column, ">", value))
        return self
    
    def lt(self, column: str, value: Any) -> "FilterBuilder":
        self.filters.append(FilterSpec(column, "<", value))
        return self
    
    def like(self, column: str, pattern: str) -> "FilterBuilder":
        self.filters.append(FilterSpec(column, "LIKE", pattern))
        return self
    
    def in_(self, column: str, values: list) -> "FilterBuilder":
        self.filters.append(FilterSpec(column, "IN", values))
        return self
    
    def is_null(self, column: str) -> "FilterBuilder":
        self.filters.append(FilterSpec(column, "IS NULL"))
        return self
    
    def date_between(self, column: str, start: date, end: date) -> "FilterBuilder":
        self.filters.append(FilterSpec(column, ">=", start.isoformat()))
        self.filters.append(FilterSpec(column, "<=", end.isoformat()))
        return self
    
    def build(self) -> tuple[str, list]:
        """Build WHERE clause and parameters."""
        clauses = []
        params = []
        for f in self.filters:
            clause, p = f.to_sql()
            clauses.append(clause)
            params.extend(p)
        return "".join(clauses), params
```

### 3.3 Base Repository Abstract Class

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Union, List, Dict, Any
import pandas as pd

T = TypeVar('T')
ID = TypeVar('ID', int, str)

class BaseRepository(ABC, Generic[T, ID]):
    """
    Abstract base class for all repositories.
    
    Provides common CRUD operations with consistent patterns:
    - Type-safe entity handling
    - Automatic cache invalidation
    - Event emission on mutations
    - Batch operation support
    """
    
    def __init__(self):
        self._table_name = self._get_table_name()
        self._cache_ttl = self._get_cache_ttl()
    
    @abstractmethod
    def _get_table_name(self) -> str:
        """Return the database table name."""
        pass
    
    @abstractmethod
    def _get_cache_ttl(self) -> str | int:
        """Return cache TTL (e.g., '1h', 300, or None)."""
        pass
    
    @abstractmethod
    def _row_to_entity(self, row: sqlite3.Row) -> T:
        """Convert database row to entity instance."""
        pass
    
    @abstractmethod
    def _entity_to_dict(self, entity: T) -> dict[str, Any]:
        """Convert entity to dictionary for INSERT/UPDATE."""
        pass
    
    @abstractmethod
    def _get_id_column(self) -> str:
        """Return the primary key column name."""
        return "id"
    
    @abstractmethod
    def _get_event_name(self) -> str:
        """Return the event name for change notifications."""
        pass
    
    # ==================== CRUD Operations ====================
    
    def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Get a single entity by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {self._table_name} WHERE {self._get_id_column()} = ?",
                (entity_id,)
            )
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None
    
    def get_all(
        self,
        filters: FilterBuilder | dict | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int = None
    ) -> pd.DataFrame:
        """
        Get all entities with optional filtering and pagination.
        
        Args:
            filters: FilterBuilder instance or dict (legacy support)
            order_by: SQL ORDER BY clause (e.g., "date DESC")
            limit: Maximum number of rows
            offset: Number of rows to skip
        """
        query = f"SELECT * FROM {self._table_name} WHERE 1=1"
        params = []
        
        if filters:
            if isinstance(filters, FilterBuilder):
                where_clause, params = filters.build()
            else:
                where_clause, params = build_filter_clause(filters)
            query += where_clause
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit is not None:
            query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
        
        with get_db_connection() as conn:
            return pd.read_sql(query, conn, params=params if params else None)
    
    def create(self, entity: T) -> ID:
        """
        Create a new entity.
        
        Returns:
            The ID of the created entity
        """
        data = self._entity_to_dict(entity)
        
        # Remove ID if None (auto-increment)
        if self._get_id_column() in data and data[self._get_id_column()] is None:
            del data[self._get_id_column()]
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})",
                tuple(data.values())
            )
            conn.commit()
            entity_id = cursor.lastrowid
        
        self._emit_change("created", entity_id=entity_id)
        return entity_id
    
    def update(self, entity_id: ID, data: dict[str, Any]) -> bool:
        """
        Update an entity by ID.
        
        Args:
            entity_id: Entity ID to update
            data: Dictionary of fields to update
        
        Returns:
            True if updated, False if not found
        """
        if not data:
            return False
        
        set_clauses = [f"{k} = ?" for k in data.keys()]
        params = list(data.values())
        params.append(entity_id)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table_name} SET {', '.join(set_clauses)} WHERE {self._get_id_column()} = ?",
                params
            )
            conn.commit()
            updated = cursor.rowcount > 0
        
        if updated:
            self._emit_change("updated", entity_id=entity_id)
        return updated
    
    def delete(self, entity_id: ID) -> bool:
        """Delete an entity by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self._table_name} WHERE {self._get_id_column()} = ?",
                (entity_id,)
            )
            conn.commit()
            deleted = cursor.rowcount > 0
        
        if deleted:
            self._emit_change("deleted", entity_id=entity_id)
        return deleted
    
    def exists(self, entity_id: ID) -> bool:
        """Check if entity exists."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM {self._table_name} WHERE {self._get_id_column()} = ? LIMIT 1",
                (entity_id,)
            )
            return cursor.fetchone() is not None
    
    def count(self, filters: FilterBuilder | dict | None = None) -> int:
        """Count entities matching filters."""
        query = f"SELECT COUNT(*) as count FROM {self._table_name} WHERE 1=1"
        params = []
        
        if filters:
            if isinstance(filters, FilterBuilder):
                where_clause, params = filters.build()
            else:
                where_clause, params = build_filter_clause(filters)
            query += where_clause
        
        with get_db_connection() as conn:
            result = pd.read_sql(query, conn, params=params if params else None)
            return int(result["count"].iloc[0])
    
    # ==================== Batch Operations ====================
    
    def bulk_create(self, entities: list[T]) -> int:
        """Create multiple entities in a single transaction."""
        if not entities:
            return 0
        
        rows = []
        columns = None
        
        for entity in entities:
            data = self._entity_to_dict(entity)
            if self._get_id_column() in data and data[self._get_id_column()] is None:
                del data[self._get_id_column()]
            
            if columns is None:
                columns = list(data.keys())
            rows.append(tuple(data.values()))
        
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                f"INSERT INTO {self._table_name} ({cols_str}) VALUES ({placeholders})",
                rows
            )
            conn.commit()
            count = cursor.rowcount
        
        self._emit_change("bulk_created", count=count)
        return count
    
    def bulk_update(self, entity_ids: list[ID], data: dict[str, Any]) -> int:
        """Update multiple entities with the same values."""
        if not entity_ids or not data:
            return 0
        
        set_clauses = [f"{k} = ?" for k in data.keys()]
        params = list(data.values())
        
        placeholders = ", ".join(["?"] * len(entity_ids))
        params.extend(entity_ids)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table_name} SET {', '.join(set_clauses)} WHERE {self._get_id_column()} IN ({placeholders})",
                params
            )
            conn.commit()
            count = cursor.rowcount
        
        self._emit_change("bulk_updated", count=count, entity_ids=entity_ids)
        return count
    
    def bulk_delete(self, entity_ids: list[ID]) -> int:
        """Delete multiple entities."""
        if not entity_ids:
            return 0
        
        placeholders = ", ".join(["?"] * len(entity_ids))
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self._table_name} WHERE {self._get_id_column()} IN ({placeholders})",
                entity_ids
            )
            conn.commit()
            count = cursor.rowcount
        
        self._emit_change("bulk_deleted", count=count, entity_ids=entity_ids)
        return count
    
    # ==================== Helper Methods ====================
    
    def _emit_change(self, action: str, **kwargs) -> None:
        """Emit change event and clear cache."""
        EventBus.emit(f"{self._get_event_name()}.changed", action=action, **kwargs)
        self._clear_cache()
    
    def _clear_cache(self) -> None:
        """Clear Streamlit cache for this repository."""
        clear_db_cache()
```

---

## 4. Specific Repository Implementations

### 4.1 TransactionRepository

```python
from datetime import date, datetime
from decimal import Decimal
import uuid
import pandas as pd
from typing import Optional

class TransactionRepository(BaseRepository[Transaction, int]):
    """
    Repository for Transaction entities.
    
    Extends base repository with transaction-specific operations like:
    - Duplicate detection
    - Status management
    - Undo/redo functionality
    - Member detection
    """
    
    def _get_table_name(self) -> str:
        return "transactions"
    
    def _get_cache_ttl(self) -> str:
        return "1h"
    
    def _get_id_column(self) -> str:
        return "id"
    
    def _get_event_name(self) -> str:
        return "transactions"
    
    def _row_to_entity(self, row: sqlite3.Row) -> Transaction:
        return Transaction(
            id=row["id"],
            date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
            label=row["label"],
            amount=Decimal(str(row["amount"])),
            original_category=row.get("original_category"),
            category_validated=row.get("category_validated"),
            account_id=row.get("account_id"),
            account_label=row.get("account_label", "Compte Principal"),
            status=TransactionStatus(row.get("status", "pending")),
            ai_confidence=row.get("ai_confidence"),
            member=row.get("member", "Inconnu"),
            beneficiary=row.get("beneficiary"),
            card_suffix=row.get("card_suffix"),
            tags=row.get("tags"),
            notes=row.get("notes"),
            comment=row.get("comment"),
            tx_hash=row.get("tx_hash"),
            is_manually_ungrouped=bool(row.get("is_manually_ungrouped", 0)),
            import_date=row.get("import_date"),
        )
    
    def _entity_to_dict(self, entity: Transaction) -> dict:
        result = {
            "date": entity.date.isoformat() if entity.date else None,
            "label": entity.label,
            "amount": float(entity.amount),
            "original_category": entity.original_category,
            "category_validated": entity.category_validated,
            "account_id": entity.account_id,
            "account_label": entity.account_label,
            "status": entity.status.value,
            "ai_confidence": entity.ai_confidence,
            "member": entity.member,
            "beneficiary": entity.beneficiary,
            "card_suffix": entity.card_suffix,
            "tags": entity.tags,
            "notes": entity.notes,
            "comment": entity.comment,
            "tx_hash": entity.tx_hash,
            "is_manually_ungrouped": 1 if entity.is_manually_ungrouped else 0,
        }
        if entity.id is not None:
            result["id"] = entity.id
        return result
    
    # ==================== Transaction-Specific Queries ====================
    
    def get_pending(self) -> pd.DataFrame:
        """Get all pending (unvalidated) transactions."""
        return self.get_all(
            filters=FilterBuilder().eq("status", "pending"),
            order_by="date DESC"
        )
    
    def get_validated(self, limit: int = None) -> pd.DataFrame:
        """Get validated transactions."""
        return self.get_all(
            filters=FilterBuilder().eq("status", "validated"),
            order_by="date DESC",
            limit=limit
        )
    
    def get_by_period(self, month: str) -> pd.DataFrame:
        """Get transactions for a specific month (YYYY-MM)."""
        with get_db_connection() as conn:
            return pd.read_sql(
                "SELECT * FROM transactions WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC",
                conn,
                params=(month,)
            )
    
    def get_by_category(self, category: str) -> pd.DataFrame:
        """Get transactions by validated category."""
        return self.get_all(
            filters=FilterBuilder().eq("category_validated", category),
            order_by="date DESC"
        )
    
    def get_by_member(self, member: str) -> pd.DataFrame:
        """Get transactions by member."""
        return self.get_all(
            filters=FilterBuilder().eq("member", member),
            order_by="date DESC"
        )
    
    def search_by_label(self, pattern: str) -> pd.DataFrame:
        """Search transactions by label pattern."""
        return self.get_all(
            filters=FilterBuilder().like("label", f"%{pattern}%"),
            order_by="date DESC"
        )
    
    def get_duplicates(self) -> pd.DataFrame:
        """Find transactions with identical date, label, amount."""
        with get_db_connection() as conn:
            return pd.read_sql(
                """
                SELECT date, label, amount, COUNT(*) as count 
                FROM transactions 
                GROUP BY date, label, amount 
                HAVING count > 1
                """,
                conn
            )
    
    def exists_by_hash(self, tx_hash: str) -> bool:
        """Check if transaction exists by hash."""
        if not tx_hash:
            return False
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM transactions WHERE tx_hash = ? LIMIT 1", (tx_hash,))
            return cursor.fetchone() is not None
    
    def count_by_criteria(self, date: date = None, label: str = None, amount: Decimal = None) -> int:
        """Count transactions matching criteria."""
        with get_db_connection() as conn:
            query = "SELECT COUNT(*) FROM transactions WHERE 1=1"
            params = []
            
            if date:
                query += " AND date = ?"
                params.append(date.isoformat())
            if label:
                query += " AND label = ?"
                params.append(label)
            if amount is not None:
                query += " AND amount = ?"
                params.append(float(amount))
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    
    # ==================== Import Operations ====================
    
    def save_from_dataframe(
        self,
        df: pd.DataFrame,
        detect_duplicates: bool = True
    ) -> tuple[int, int]:
        """
        Save transactions from DataFrame with duplicate detection.
        
        Returns:
            Tuple of (new_count, skipped_count)
        """
        if df.empty:
            return 0, 0
        
        # Ensure tx_hash exists
        if "tx_hash" not in df.columns or df["tx_hash"].isna().any():
            from modules.ingestion import generate_tx_hash
            df = generate_tx_hash(df)
        
        # Pre-load member mappings
        from modules.db.members import get_member_mappings, detect_member_from_content
        get_member_mappings()
        
        df["date_str"] = df["date"].astype(str)
        
        if "account_label" not in df.columns:
            df["account_label"] = "Unknown"
        
        # Group by signature
        grouped = df.groupby(["date_str", "label", "amount"])
        unique_sigs = [(d, l, a) for (d, l, a), _ in grouped]
        
        # Batch query existing counts
        db_counts = self._get_existing_counts(unique_sigs)
        
        # Collect rows to insert
        rows_to_insert = []
        insert_columns = None
        skipped_count = 0
        
        for (date, label, amount), group in grouped:
            db_count = db_counts.get((date, label, amount), 0)
            input_count = len(group)
            to_insert_count = max(0, input_count - db_count)
            skipped_count += input_count - to_insert_count
            
            if to_insert_count > 0:
                group_to_insert = group.tail(to_insert_count)
                for _, row in group_to_insert.iterrows():
                    row_dict = row.to_dict()
                    if "date_str" in row_dict:
                        del row_dict["date_str"]
                    
                    # Apply member detection
                    if row_dict.get("member") in [None, "", "Inconnu"]:
                        suffix = row_dict.get("card_suffix")
                        account = row_dict.get("account_label")
                        row_dict["member"] = detect_member_from_content(
                            label=row_dict["label"],
                            card_suffix=suffix,
                            account_label=account
                        )
                    
                    if insert_columns is None:
                        insert_columns = list(row_dict.keys())
                    rows_to_insert.append(tuple(row_dict.values()))
        
        # Batch insert
        if rows_to_insert:
            cols = ", ".join(insert_columns)
            placeholders = ", ".join(["?"] * len(insert_columns))
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    f"INSERT INTO transactions ({cols}) VALUES ({placeholders})",
                    rows_to_insert
                )
                conn.commit()
        
        new_count = len(rows_to_insert)
        self._emit_change("batch_imported", new_count=new_count, skipped_count=skipped_count)
        return new_count, skipped_count
    
    def _get_existing_counts(self, signatures: list[tuple]) -> dict[tuple, int]:
        """Get count of existing transactions for signatures."""
        if not signatures:
            return {}
        
        placeholders = ",".join(["(?,?,?)"] * len(signatures))
        flat_params = [item for sig in signatures for item in sig]
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT date, label, amount, COUNT(*) as cnt
                FROM transactions
                WHERE (date, label, amount) IN ({placeholders})
                GROUP BY date, label, amount
                """,
                flat_params
            )
            return {(row[0], row[1], row[2]): row[3] for row in cursor.fetchall()}
    
    # ==================== Validation Operations ====================
    
    def validate(
        self,
        tx_ids: list[int],
        category: str,
        tags: str = None,
        beneficiary: str = None,
        notes: str = None
    ) -> None:
        """
        Validate transactions and log for undo.
        """
        if not tx_ids:
            return
        
        action_id = str(uuid.uuid4())[:8]
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Capture previous state for undo
            placeholders = ", ".join(["?"] * len(tx_ids))
            cursor.execute(
                f"""
                SELECT id, status, category_validated, member, tags, beneficiary, notes
                FROM transactions WHERE id IN ({placeholders})
                """,
                list(tx_ids)
            )
            rows = cursor.fetchall()
            
            # Insert history records
            history_records = [
                (action_id, str(r[0]), r[1], r[2], r[3], r[4], r[5], r[6])
                for r in rows
            ]
            
            if history_records:
                cursor.executemany(
                    """
                    INSERT INTO transaction_history
                    (action_group_id, tx_ids, prev_status, prev_category, prev_member, prev_tags, prev_beneficiary, prev_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    history_records
                )
            
            # Apply updates
            set_clauses = ["category_validated = ?", "status = 'validated'"]
            params = [category]
            
            if tags is not None:
                set_clauses.append("tags = ?")
                params.append(tags)
            if beneficiary is not None:
                set_clauses.append("beneficiary = ?")
                params.append(beneficiary)
            if notes is not None:
                set_clauses.append("notes = ?")
                params.append(notes)
            
            query = f"""
                UPDATE transactions
                SET {', '.join(set_clauses)}
                WHERE id IN ({placeholders})
            """
            params.extend(list(tx_ids))
            cursor.execute(query, params)
            conn.commit()
        
        self._emit_change("validated", tx_ids=tx_ids, category=category)
    
    def undo_last_validation(self) -> tuple[bool, str]:
        """Undo the last validation action."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get last action
            cursor.execute(
                "SELECT action_group_id FROM transaction_history ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if not row:
                return False, "Aucune action à annuler."
            
            action_id = row[0]
            
            # Get history entries
            cursor.execute(
                "SELECT * FROM transaction_history WHERE action_group_id = ?",
                (action_id,)
            )
            entries = cursor.fetchall()
            
            # Restore previous state
            undo_updates = [
                (e[3], e[4], e[5], e[6], e[7], int(e[2]))
                for e in entries
            ]
            
            if undo_updates:
                cursor.executemany(
                    """
                    UPDATE transactions
                    SET status = ?, category_validated = ?, member = ?, tags = ?, beneficiary = ?
                    WHERE id = ?
                    """,
                    undo_updates
                )
            
            # Delete history
            cursor.execute(
                "DELETE FROM transaction_history WHERE action_group_id = ?",
                (action_id,)
            )
            conn.commit()
        
        self._emit_change("undo", action_id=action_id, count=len(entries))
        return True, f"Action {action_id} annulée ({len(entries)} transactions rétablies)."
    
    def mark_ungrouped(self, tx_id: int) -> None:
        """Mark transaction to be excluded from smart grouping."""
        self.update(tx_id, {"is_manually_ungrouped": 1})
    
    # ==================== Tag Operations ====================
    
    def add_tags(self, tx_ids: list[int], tags: list[str]) -> int:
        """Add tags to transactions without overwriting existing."""
        if not tx_ids or not tags:
            return 0
        
        tag_str = ", ".join(tags)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get current tags
            placeholders = ", ".join(["?"] * len(tx_ids))
            cursor.execute(
                f"SELECT id, tags FROM transactions WHERE id IN ({placeholders})",
                list(tx_ids)
            )
            rows = cursor.fetchall()
            
            # Prepare updates
            updates = []
            for tx_id, current_tags in rows:
                new_tags = tag_str
                if current_tags:
                    if any(t in current_tags for t in tags):
                        continue
                    new_tags = f"{current_tags},{tag_str}"
                updates.append((new_tags, tx_id))
            
            if updates:
                cursor.executemany(
                    "UPDATE transactions SET tags = ? WHERE id = ?",
                    updates
                )
            
            conn.commit()
            return len(updates)
    
    def delete_by_period(self, month_str: str) -> int:
        """Delete all transactions for a month (YYYY-MM)."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM transactions WHERE strftime('%Y-%m', date) = ?",
                (month_str,)
            )
            count = cursor.rowcount
            conn.commit()
        
        self._emit_change("deleted_by_period", period=month_str, count=count)
        return count
```

### 4.2 CategoryRepository

```python
class CategoryRepository(BaseRepository[Category, int]):
    """Repository for Category entities."""
    
    def _get_table_name(self) -> str:
        return "categories"
    
    def _get_cache_ttl(self) -> int:
        return 300
    
    def _get_event_name(self) -> str:
        return "categories"
    
    def _row_to_entity(self, row: sqlite3.Row) -> Category:
        return Category(
            id=row["id"],
            name=row["name"],
            emoji=row.get("emoji", "🏷️"),
            is_fixed=bool(row.get("is_fixed", 0)),
            suggested_tags=row.get("suggested_tags"),
            created_at=row.get("created_at"),
        )
    
    def _entity_to_dict(self, entity: Category) -> dict:
        return {
            "id": entity.id,
            "name": entity.name,
            "emoji": entity.emoji,
            "is_fixed": 1 if entity.is_fixed else 0,
            "suggested_tags": entity.suggested_tags,
        }
    
    # Specific operations
    
    def get_names(self) -> list[str]:
        """Get list of category names."""
        with get_db_connection() as conn:
            df = pd.read_sql("SELECT name FROM categories ORDER BY name", conn)
            return df["name"].tolist()
    
    def get_with_emojis(self) -> dict[str, str]:
        """Get mapping of name -> emoji."""
        with get_db_connection() as conn:
            df = pd.read_sql("SELECT name, emoji FROM categories", conn)
            return dict(zip(df["name"], df["emoji"]))
    
    def get_suggested_tags(self) -> dict[str, list[str]]:
        """Get mapping of name -> suggested tags list."""
        with get_db_connection() as conn:
            df = pd.read_sql("SELECT name, suggested_tags FROM categories", conn)
            result = {}
            for _, row in df.iterrows():
                if row["suggested_tags"]:
                    result[row["name"]] = [
                        t.strip() for t in str(row["suggested_tags"]).split(",") if t.strip()
                    ]
                else:
                    result[row["name"]] = []
            return result
    
    def add_suggested_tag(self, cat_name: str, tag: str) -> bool:
        """Add a tag to category's suggested tags."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, suggested_tags FROM categories WHERE name = ?",
                (cat_name,)
            )
            row = cursor.fetchone()
            if not row:
                return False
            
            cat_id, current_str = row
            current = [t.strip() for t in str(current_str).split(",") if t.strip() and t != "None"]
            
            if tag not in current:
                current.append(tag)
                new_str = ", ".join(sorted(current))
                cursor.execute(
                    "UPDATE categories SET suggested_tags = ? WHERE id = ?",
                    (new_str, cat_id)
                )
                conn.commit()
            
            return True
    
    def merge(self, source: str, target: str) -> dict:
        """Merge source category into target."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Update transactions
            cursor.execute(
                """
                UPDATE transactions SET category_validated = ?
                WHERE category_validated = ? COLLATE NOCASE
                """,
                (target, source)
            )
            tx_count = cursor.rowcount
            
            # Update rules
            cursor.execute(
                """
                UPDATE learning_rules SET category = ?
                WHERE category = ? COLLATE NOCASE
                """,
                (target, source)
            )
            rule_count = cursor.rowcount
            
            # Transfer budget
            budget_transferred = False
            cursor.execute(
                "SELECT amount FROM budgets WHERE category = ? COLLATE NOCASE",
                (source,)
            )
            source_budget = cursor.fetchone()
            
            if source_budget:
                source_amount = source_budget[0]
                cursor.execute(
                    "SELECT amount FROM budgets WHERE category = ? COLLATE NOCASE",
                    (target,)
                )
                target_budget = cursor.fetchone()
                
                if target_budget:
                    new_amount = target_budget[0] + source_amount
                    cursor.execute(
                        "UPDATE budgets SET amount = ? WHERE category = ? COLLATE NOCASE",
                        (new_amount, target)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO budgets (category, amount) VALUES (?, ?)",
                        (target, source_amount)
                    )
                
                cursor.execute(
                    "DELETE FROM budgets WHERE category = ? COLLATE NOCASE",
                    (source,)
                )
                budget_transferred = True
            
            # Delete source
            cursor.execute(
                "DELETE FROM categories WHERE name = ? COLLATE NOCASE",
                (source,)
            )
            category_deleted = cursor.rowcount > 0
            
            conn.commit()
        
        self._emit_change("merged", source=source, target=target)
        
        return {
            "transactions": tx_count,
            "rules": rule_count,
            "budgets_transferred": budget_transferred,
            "category_deleted": category_deleted,
        }
    
    def get_ghosts(self) -> list[dict]:
        """Get categories used in transactions but not defined."""
        with get_db_connection() as conn:
            official_df = pd.read_sql("SELECT name FROM categories", conn)
            official_set = set(official_df["name"].tolist())
            
            used_df = pd.read_sql(
                """
                SELECT DISTINCT category_validated FROM transactions
                WHERE category_validated IS NOT NULL AND category_validated != 'Inconnu'
                """,
                conn
            )
            used_set = set(used_df["category_validated"].tolist())
            
            all_names = sorted(list(official_set.union(used_set)))
            return [
                {"name": name, "type": "OFFICIAL" if name in official_set else "GHOST"}
                for name in all_names
            ]
```

### 4.3 MemberRepository

```python
class MemberRepository(BaseRepository[Member, int]):
    """Repository for Member entities."""
    
    def _get_table_name(self) -> str:
        return "members"
    
    def _get_cache_ttl(self) -> int:
        return 300
    
    def _get_event_name(self) -> str:
        return "members"
    
    def _row_to_entity(self, row: sqlite3.Row) -> Member:
        return Member(
            id=row["id"],
            name=row["name"],
            member_type=row.get("member_type", MemberType.HOUSEHOLD),
            created_at=row.get("created_at"),
        )
    
    def _entity_to_dict(self, entity: Member) -> dict:
        return {
            "id": entity.id,
            "name": entity.name,
            "member_type": entity.member_type,
        }
    
    # Specific operations
    
    def rename(self, old_name: str, new_name: str) -> int:
        """Rename member and propagate to all references."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Update members table
            cursor.execute(
                "UPDATE members SET name = ? WHERE name = ?",
                (new_name, old_name)
            )
            
            # Update transactions
            cursor.execute(
                "UPDATE transactions SET member = ? WHERE member = ?",
                (new_name, old_name)
            )
            tx_count = cursor.rowcount
            
            cursor.execute(
                "UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?",
                (new_name, old_name)
            )
            tx_count += cursor.rowcount
            
            # Update mappings
            cursor.execute(
                "UPDATE member_mappings SET member_name = ? WHERE member_name = ?",
                (new_name, old_name)
            )
            
            conn.commit()
        
        self._emit_change("renamed", old_name=old_name, new_name=new_name)
        EventBus.emit("transactions.changed")  # Cross-entity event
        return tx_count
    
    def get_orphans(self) -> list[str]:
        """Find member values in transactions not in members table."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM members")
            official = {r[0] for r in cursor.fetchall()}
            official.update({"Maison", "Famille", "Inconnu", "Anonyme", "", None})
            
            cursor.execute("SELECT DISTINCT member FROM transactions")
            txn_members = {r[0] for r in cursor.fetchall() if r[0]}
            
            cursor.execute("SELECT DISTINCT beneficiary FROM transactions")
            txn_benefs = {r[0] for r in cursor.fetchall() if r[0]}
            
            return sorted(list((txn_members.union(txn_benefs)) - official))
    
    def replace_label(self, old_label: str, replacement: str = "Inconnu") -> int:
        """Replace a member label across all tables."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE transactions SET member = ? WHERE member = ?",
                (replacement, old_label)
            )
            count = cursor.rowcount
            
            cursor.execute(
                "UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?",
                (replacement, old_label)
            )
            count += cursor.rowcount
            
            cursor.execute(
                "DELETE FROM member_mappings WHERE member_name = ?",
                (old_label,)
            )
            
            cursor.execute(
                "DELETE FROM members WHERE name = ?",
                (old_label,)
            )
            
            conn.commit()
        
        self._emit_change("label_replaced", old=old_label, new=replacement)
        EventBus.emit("transactions.changed")
        return count
```

### 4.4 BudgetRepository

```python
class BudgetRepository(BaseRepository[Budget, str]):
    """Repository for Budget entities (uses category as PK)."""
    
    def _get_table_name(self) -> str:
        return "budgets"
    
    def _get_cache_ttl(self) -> str:
        return "1h"
    
    def _get_id_column(self) -> str:
        return "category"
    
    def _get_event_name(self) -> str:
        return "budgets"
    
    def _row_to_entity(self, row: sqlite3.Row) -> Budget:
        return Budget(
            category=row["category"],
            amount=Decimal(str(row["amount"])),
            updated_at=row.get("updated_at"),
        )
    
    def _entity_to_dict(self, entity: Budget) -> dict:
        return {
            "category": entity.category,
            "amount": float(entity.amount),
        }
    
    # Override for string PK
    def create(self, entity: Budget) -> str:
        """Create or replace budget (upsert)."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)",
                (entity.category, float(entity.amount))
            )
            conn.commit()
        
        self._emit_change("saved", category=entity.category)
        return entity.category
    
    def get_by_category(self, category: str) -> Optional[Budget]:
        """Get budget for specific category."""
        return self.get_by_id(category)
```

---

## 5. Migration Plan

### Phase 1: Infrastructure (Week 1)

1. **Create base infrastructure**:
   ```
   modules/db/repositories/
   ├── __init__.py
   ├── base.py          # BaseRepository, FilterBuilder
   ├── entities.py      # Entity dataclasses
   └── unit_of_work.py  # Transaction management
   ```

2. **Keep existing code functional** - no breaking changes

3. **Add repository factory**:
   ```python
   class RepositoryFactory:
       @staticmethod
       def transactions() -> TransactionRepository:
           return TransactionRepository()
       # ... other repos
   ```

### Phase 2: Parallel Implementation (Week 2-3)

1. **Implement repositories alongside existing code**
2. **Add deprecation warnings to old functions**:
   ```python
   import warnings
   
   def get_pending_transactions() -> pd.DataFrame:
       warnings.warn(
           "Use TransactionRepository().get_pending() instead",
           DeprecationWarning,
           stacklevel=2
       )
       # ... existing code
   ```

3. **Create compatibility layer** for common operations

### Phase 3: Gradual Migration (Week 4-6)

1. **Migrate one page/module at a time**
2. **Update tests** to use repositories
3. **Remove deprecated functions** once all callers migrated

### Phase 4: Cleanup (Week 7)

1. **Remove legacy functions**
2. **Update documentation**
3. **Archive old code**

---

## 6. Usage Examples

### Basic CRUD

```python
from modules.db.repositories import RepositoryFactory

# Get repository
tx_repo = RepositoryFactory.transactions()
cat_repo = RepositoryFactory.categories()

# Create
new_tx = Transaction(
    date=date.today(),
    label="CARREFOUR",
    amount=Decimal("-45.67")
)
tx_id = tx_repo.create(new_tx)

# Read
pending = tx_repo.get_pending()
by_category = tx_repo.get_by_category("Alimentation")

# Update
tx_repo.update(tx_id, {"category_validated": "Courses"})

# Delete
tx_repo.delete(tx_id)
```

### Complex Queries

```python
# Using FilterBuilder
from modules.db.repositories import FilterBuilder

filters = (
    FilterBuilder()
    .eq("status", "validated")
    .gt("amount", 100)
    .date_between("date", date(2024, 1, 1), date(2024, 12, 31))
    .like("label", "%CARREFOUR%")
)

results = tx_repo.get_all(
    filters=filters,
    order_by="date DESC",
    limit=100
)
```

### Batch Operations

```python
# Import from DataFrame
new_count, skipped = tx_repo.save_from_dataframe(df)

# Bulk validate
tx_repo.validate(
    tx_ids=[1, 2, 3],
    category="Alimentation",
    tags="Courses, Supermarché"
)

# Bulk update
tx_repo.bulk_update(
    entity_ids=[1, 2, 3],
    data={"member": "Moi"}
)
```

---

## 7. Benefits of Repository Pattern

| Aspect | Before | After |
|--------|--------|-------|
| **Testability** | Hard to mock global functions | Easy dependency injection |
| **Type Safety** | Dict/row manipulation | Typed entities |
| **Code Reuse** | Copy-paste SQL | Inherited base methods |
| **Maintainability** | 600-line files | Small focused classes |
| **Documentation** | Function docstrings | Self-documenting entities |
| **Refactoring** | Error-prone | Centralized in repository |
| **Caching** | Decorators scattered | Centralized in base class |
| **Events** | Manual emission | Automatic on mutations |

---

## Appendix: Full File Structure

```
modules/db/
├── __init__.py              # Re-export for compatibility
├── connection.py            # Keep (with build_filter_clause)
├── migrations.py            # Keep
├── transactions.py          # Deprecate → use TransactionRepository
├── transactions_batch.py    # Deprecate → use TransactionRepository
├── categories.py            # Deprecate → use CategoryRepository
├── members.py               # Deprecate → use MemberRepository
├── budgets.py               # Deprecate → use BudgetRepository
├── rules.py                 # Deprecate → use RuleRepository
├── tags.py                  # Deprecate → move to TransactionRepository
├── settings.py              # Keep (key-value special case)
├── stats.py                 # Keep (analytics special case)
├── audit.py                 # Keep
├── dashboard_layouts.py     # Keep
├── dashboard_cleanup.py     # Keep
├── maintenance.py           # Keep
├── recurrence_feedback.py   # Keep
└── repositories/            # NEW
    ├── __init__.py
    ├── base.py              # BaseRepository, FilterBuilder
    ├── entities.py          # All entity dataclasses
    ├── unit_of_work.py      # Atomic transaction helper
    ├── transaction_repo.py
    ├── category_repo.py
    ├── member_repo.py
    ├── budget_repo.py
    └── rule_repo.py
```

---

*Document generated: 2026-02-20*  
*Based on analysis of modules/db/ directory - ~2,500 lines of code*
