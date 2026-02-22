"""
DB Repository Pattern v2
========================

Modern database access layer using Repository pattern.

Migration guide:
    OLD: from modules.db.transactions import get_transaction_by_id
    NEW: from modules.db_v2.repositories import TransactionRepository

Example:
    >>> from modules.db_v2.repositories import TransactionRepository
    >>> repo = TransactionRepository()
    >>> tx = repo.get_by_id(1)
    >>> 
    >>> # With Unit of Work
    >>> from modules.db_v2.base import unit_of_work
    >>> with unit_of_work() as uow:
    ...     tx = uow.transactions.get_by_id(1)
    ...     uow.transactions.update_category(tx.id, "Food")
"""

__version__ = "2.0.0"

# Base classes
from modules.db_v2.base.repository import BaseRepository
from modules.db_v2.base.unit_of_work import UnitOfWork, unit_of_work

# Models
from modules.db_v2.models.budget import Budget
from modules.db_v2.models.category import Category
from modules.db_v2.models.member import Member
from modules.db_v2.models.transaction import Transaction

# Repositories
from modules.db_v2.repositories import (
    BudgetRepository,
    CategoryRepository,
    MemberRepository,
    TransactionRepository,
)

__all__ = [
    # Base
    "BaseRepository",
    "UnitOfWork",
    "unit_of_work",
    # Models
    "Transaction",
    "Category",
    "Member",
    "Budget",
    # Repositories
    "TransactionRepository",
    "CategoryRepository",
    "MemberRepository",
    "BudgetRepository",
]
