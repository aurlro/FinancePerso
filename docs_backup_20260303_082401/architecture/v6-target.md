# Architecture Cible v6.0

## Vision

> Une architecture **Clean Architecture** / **Hexagonale** où chaque couche est indépendante et testable.

## Principes

1. **Domain-Driven Design** : Le métier au centre, infrastructure en périphérie
2. **Dependency Inversion** : Dépendre d'abstractions, pas d'implémentations
3. **Single Responsibility** : Un module = une raison de changer
4. **Testability** : Chaque couche testable sans les autres

## Architecture en couches

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLEAN ARCHITECTURE v6.0                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  PRESENTATION LAYER                                      │   │
│  │  (Streamlit pages)                                      │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐                   │   │
│  │  │ Page 1  │ │ Page 2  │ │ Page 3  │  ...              │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘                   │   │
│  │       └─────────────┬─────────────┘                     │   │
│  │                     ▼                                   │   │
│  │  ┌─────────────────────────────────────┐               │   │
│  │  │  UI Components (Atoms/Molecules)    │               │   │
│  │  └─────────────────────────────────────┘               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  APPLICATION LAYER                                       │   │
│  │  (Use Cases / Services)                                 │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │   │
│  │  │ ImportTx    │ │ Categorize  │ │ BudgetAlert │       │   │
│  │  │ Service     │ │ Service     │ │ Service     │       │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  DOMAIN LAYER (Cœur métier)                             │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  Models (Pydantic)                              │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐          │   │   │
│  │  │  │Transaction│ │ Category│ │  Budget │          │   │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘          │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  Repository Interfaces (Abstract)               │   │   │
│  │  │  - ITransactionRepository                       │   │   │
│  │  │  - ICategoryRepository                          │   │   │
│  │  │  - IBudgetRepository                            │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  INFRASTRUCTURE LAYER                                    │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  Persistence                                    │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐          │   │   │
│  │  │  │SQLite   │ │  Cache  │ │  File   │          │   │   │
│  │  │  │Repo     │ │  Layer  │ │  Store  │          │   │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘          │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  AI Providers                                   │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐          │   │   │
│  │  │  │ Gemini  │ │ Ollama  │ │ DeepSeek│          │   │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘          │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Structure des dossiers

```
FinancePerso/
├── src/                                    # Code source principal
│   ├── __init__.py
│   ├── config.py                          # Configuration centralisée
│   │
│   ├── domain/                            # COEUR MÉTIER (stable)
│   │   ├── __init__.py
│   │   ├── models/                        # Entités Pydantic
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   ├── budget.py
│   │   │   ├── member.py
│   │   │   └── common.py                  # Types partagés
│   │   │
│   │   ├── repositories/                  # Interfaces (contrats)
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py             # ITransactionRepository
│   │   │   ├── category.py                # ICategoryRepository
│   │   │   └── base.py                    # Repository base class
│   │   │
│   │   ├── services/                      # Logique métier pure
│   │   │   ├── __init__.py
│   │   │   ├── categorization.py          # Algo de catégorisation
│   │   │   ├── statistics.py              # Calculs statistiques
│   │   │   └── validation.py              # Règles de validation
│   │   │
│   │   └── exceptions.py                  # Exceptions métier
│   │
│   ├── application/                       # CAS D'USAGE
│   │   ├── __init__.py
│   │   ├── use_cases/                     # Un fichier = un use case
│   │   │   ├── __init__.py
│   │   │   ├── import_transactions.py
│   │   │   ├── categorize_pending.py
│   │   │   ├── generate_report.py
│   │   │   └── check_budget_alerts.py
│   │   │
│   │   └── dto/                           # Data Transfer Objects
│   │       ├── __init__.py
│   │       ├── transaction.py
│   │       └── report.py
│   │
│   ├── infrastructure/                    # TECHNIQUE (remplaçable)
│   │   ├── __init__.py
│   │   ├── persistence/                   # Stockage
│   │   │   ├── __init__.py
│   │   │   ├── sqlite/                    # Implémentation SQLite
│   │   │   │   ├── __init__.py
│   │   │   │   ├── connection.py
│   │   │   │   ├── migrations.py
│   │   │   │   ├── repositories/          # Implémentations concrètes
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── transaction.py     # TransactionRepository
│   │   │   │   │   ├── category.py        # CategoryRepository
│   │   │   │   │   └── base.py
│   │   │   │   └── models/                # Modèles SQLAlchemy (optionnel)
│   │   │   │
│   │   │   └── cache/                     # Couche cache
│   │   │       ├── __init__.py
│   │   │       ├── manager.py
│   │   │       └── decorators.py
│   │   │
│   │   ├── ai/                            # Providers IA
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    # AIProvider abstract
│   │   │   ├── providers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── gemini.py
│   │   │   │   ├── ollama.py
│   │   │   │   ├── openai.py
│   │   │   │   └── deepseek.py
│   │   │   │
│   │   │   └── analyzers/                 # Analyses IA
│   │   │       ├── __init__.py
│   │   │       ├── base.py
│   │   │       ├── budget/
│   │   │       ├── trends/
│   │   │       └── savings/
│   │   │
│   │   ├── security/                      # Chiffrement, auth
│   │   │   ├── __init__.py
│   │   │   └── encryption.py
│   │   │
│   │   └── logging/                       # Logging configuré
│   │       ├── __init__.py
│   │       └── setup.py
│   │
│   └── presentation/                      # UI / STREAMLIT
│       ├── __init__.py
│       ├── pages/                         # Pages Streamlit
│       │   ├── __init__.py
│       │   ├── operations.py              # Ancien 1_Opérations.py
│       │   ├── synthese.py                # Ancien 3_Synthèse.py
│       │   └── ...
│       │
│       ├── components/                    # Composants réutilisables
│       │   ├── __init__.py
│       │   ├── atoms/                     # Éléments de base
│       │   │   ├── __init__.py
│       │   │   ├── buttons.py
│       │   │   ├── icons.py
│       │   │   └── typography.py
│       │   │
│       │   ├── molecules/                 # Composants composés
│       │   │   ├── __init__.py
│       │   │   ├── cards.py
│       │   │   ├── forms.py
│       │   │   └── lists.py
│       │   │
│       │   └── organisms/                 # Sections complètes
│       │       ├── __init__.py
│       │       ├── transaction_list.py
│       │       ├── budget_widget.py
│       │       └── dashboard_section.py
│       │
│       ├── layouts/                       # Templates de page
│       │   ├── __init__.py
│       │   ├── default.py
│       │   ├── centered.py
│       │   └── sidebar.py
│       │
│       └── hooks/                         # Logique UI réutilisable
│           ├── __init__.py
│           ├── use_transactions.py
│           └── use_categories.py
│
├── tests/                                 # Tests
│   ├── unit/                              # Tests unitaires
│   │   ├── domain/                        # Tests métier
│   │   ├── application/                   # Tests use cases
│   │   └── infrastructure/                # Tests infra (mocké)
│   │
│   ├── integration/                       # Tests intégration
│   │   ├── persistence/                   # Tests DB réelle
│   │   └── ai/                            # Tests providers IA
│   │
│   ├── e2e/                               # Tests end-to-end
│   │   └── test_streamlit.py              # Tests Streamlit
│   │
│   └── fixtures/                          # Données de test
│       ├── transactions.json
│       └── categories.json
│
├── docs/                                  # Documentation
│   ├── architecture/
│   ├── api/
│   └── deployment/
│
├── scripts/                               # Scripts utilitaires
│   ├── setup.py
│   ├── migrate.py
│   └── analyze.py
│
├── pyproject.toml                         # Configuration moderne
├── README.md
└── CHANGELOG.md
```

## Exemple: Flux complet

### Use Case: Importer des transactions

```python
# ============================================
# 1. PRESENTATION (Streamlit)
# ============================================

# src/presentation/pages/operations.py
import streamlit as st
from src.application.use_cases.import_transactions import ImportTransactionsUseCase
from src.application.dto.transaction import ImportResult
from src.infrastructure.persistence.sqlite.repositories import TransactionRepository
from src.infrastructure.ai.providers import GeminiProvider

def render_import_page():
    uploaded_file = st.file_uploader("Fichier CSV")
    
    if uploaded_file:
        # Créer le use case avec ses dépendances
        use_case = ImportTransactionsUseCase(
            transaction_repo=TransactionRepository(),
            ai_provider=GeminiProvider(),
            categorization_service=CategorizationService()
        )
        
        # Exécuter
        result: ImportResult = use_case.execute(
            file_content=uploaded_file.read(),
            account_label="Compte Principal"
        )
        
        st.success(f"{result.imported_count} transactions importées!")


# ============================================
# 2. APPLICATION (Use Case)
# ============================================

# src/application/use_cases/import_transactions.py
from dataclasses import dataclass
from typing import List

from src.domain.models.transaction import Transaction
from src.domain.repositories.transaction import ITransactionRepository
from src.domain.services.categorization import CategorizationService
from src.infrastructure.ai.base import AIProvider


@dataclass
class ImportResult:
    imported_count: int
    duplicated_count: int
    categorized_count: int
    errors: List[str]


class ImportTransactionsUseCase:
    """Use case: Import transactions from CSV."""
    
    def __init__(
        self,
        transaction_repo: ITransactionRepository,
        ai_provider: AIProvider,
        categorization_service: CategorizationService
    ):
        self._repo = transaction_repo
        self._ai = ai_provider
        self._cat_service = categorization_service
    
    def execute(
        self,
        file_content: bytes,
        account_label: str
    ) -> ImportResult:
        """Execute the use case."""
        # 1. Parser le CSV
        raw_transactions = self._parse_csv(file_content)
        
        # 2. Créer les entités du domaine
        transactions = [
            Transaction.from_csv_row(row, account_label)
            for row in raw_transactions
        ]
        
        # 3. Dédupliquer
        new_transactions = self._deduplicate(transactions)
        
        # 4. Catégoriser
        for tx in new_transactions:
            category = self._cat_service.categorize(tx)
            tx.assign_category(category)
        
        # 5. Sauvegarder
        saved_count = self._repo.save_batch(new_transactions)
        
        return ImportResult(
            imported_count=saved_count,
            duplicated_count=len(transactions) - len(new_transactions),
            categorized_count=len(new_transactions),
            errors=[]
        )


# ============================================
# 3. DOMAIN (Modèle & Service)
# ============================================

# src/domain/models/transaction.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """Domain entity for a financial transaction."""
    
    id: int | None = None
    date: datetime
    label: str = Field(..., min_length=1)
    amount: Decimal
    category: str = "Inconnu"
    account_label: str
    
    @property
    def is_expense(self) -> bool:
        return self.amount < 0
    
    @property
    def is_income(self) -> bool:
        return self.amount > 0
    
    def assign_category(self, category: str) -> None:
        """Assign a category to this transaction."""
        self.category = category
    
    @classmethod
    def from_csv_row(cls, row: dict, account: str) -> "Transaction":
        """Factory method from CSV data."""
        return cls(
            date=datetime.strptime(row["date"], "%Y-%m-%d"),
            label=row["label"],
            amount=Decimal(row["amount"]),
            account_label=account
        )


# src/domain/services/categorization.py
from src.domain.models.transaction import Transaction


class CategorizationService:
    """Service for categorizing transactions."""
    
    def __init__(self, ai_provider=None):
        self._ai = ai_provider
        self._rules = self._load_rules()
    
    def categorize(self, transaction: Transaction) -> str:
        """Categorize a transaction using rules or AI."""
        # 1. Try rules first
        category = self._apply_rules(transaction)
        if category:
            return category
        
        # 2. Try AI if available
        if self._ai:
            return self._ask_ai(transaction)
        
        return "Inconnu"
    
    def _apply_rules(self, transaction: Transaction) -> str | None:
        """Apply categorization rules."""
        for rule in self._rules:
            if rule.matches(transaction):
                return rule.category
        return None


# ============================================
# 4. INFRASTRUCTURE (Repository & AI)
# ============================================

# src/infrastructure/persistence/sqlite/repositories/transaction.py
from typing import List
import sqlite3

from src.domain.models.transaction import Transaction
from src.domain.repositories.transaction import ITransactionRepository
from src.infrastructure.persistence.sqlite.connection import get_connection


class TransactionRepository(ITransactionRepository):
    """SQLite implementation of transaction repository."""
    
    def __init__(self):
        self._connection = get_connection()
    
    def save_batch(self, transactions: List[Transaction]) -> int:
        """Save multiple transactions."""
        cursor = self._connection.cursor()
        
        data = [
            (tx.date, tx.label, float(tx.amount), tx.category, tx.account_label)
            for tx in transactions
        ]
        
        cursor.executemany(
            """
            INSERT INTO transactions (date, label, amount, category, account_label)
            VALUES (?, ?, ?, ?, ?)
            """,
            data
        )
        
        self._connection.commit()
        return cursor.rowcount
    
    def get_by_id(self, tx_id: int) -> Transaction | None:
        """Get transaction by ID."""
        # Implementation...
        pass


# src/domain/repositories/transaction.py (Interface)
from abc import ABC, abstractmethod
from typing import List

from src.domain.models.transaction import Transaction


class ITransactionRepository(ABC):
    """Interface for transaction repositories."""
    
    @abstractmethod
    def save_batch(self, transactions: List[Transaction]) -> int:
        """Save multiple transactions. Returns count saved."""
        pass
    
    @abstractmethod
    def get_by_id(self, tx_id: int) -> Transaction | None:
        """Get transaction by ID."""
        pass
```

## Comparaison v5.x vs v6.0

| Aspect | v5.x | v6.0 | Bénéfice |
|--------|------|------|----------|
| **Structure** | modules/ plat | src/ avec couches | Séparation claire |
| **Dépendances** | Imports circulaires | Dependency injection | Testabilité |
| **DB** | SQL direct | Repository pattern | Changement facile |
| **IA** | Provider monolithique | Providers modulaires | Ajout facile |
| **UI** | 78 fichiers sans structure | Atomic design | Maintenabilité |
| **Tests** | 75% coverage | 85%+ target | Confiance |
| **Documentation** | README + AGENTS | Architecture Decision Records | Transparence |

## Migration graduelle

Pas besoin de tout réécrire! Approche incrémentale:

```
Étape 1: Renommer modules/ → src/ (1h)
Étape 2: Créer domain/models/ (2h)
Étape 3: Extraire use cases un par un (1j par use case)
Étape 4: Migrer repositories vers pattern (2j)
Étape 5: Refactoriser UI (3j)
```

---

**Vision** : Une codebase où ajouter une feature prend 2h, pas 2j.  
**Métrique de succès** : Nombre de fichiers touchés pour une feature < 5.
