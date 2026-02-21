"""
Repository pattern implementation for FinancePerso database layer.

This module provides a clean Repository pattern over the existing database layer,
offering typed entities, consistent CRUD operations, and improved testability.

Example:
    from modules.db.repositories import RepositoryFactory
    
    # Get repository instance
    tx_repo = RepositoryFactory.transactions()
    
    # Use typed CRUD operations
    pending = tx_repo.get_pending()
    tx_repo.validate([1, 2, 3], category="Alimentation")
"""

from modules.db.repositories.entities import (
    Transaction,
    TransactionStatus,
    Category,
    Member,
    MemberMapping,
    AccountMemberMapping,
    Budget,
    LearningRule,
)

from modules.db.repositories.base import (
    FilterSpec,
    FilterBuilder,
    BaseRepository,
)

from modules.db.repositories.transaction_repo import TransactionRepository
from modules.db.repositories.category_repo import CategoryRepository
from modules.db.repositories.member_repo import MemberRepository
from modules.db.repositories.budget_repo import BudgetRepository


class RepositoryFactory:
    """Factory for creating repository instances."""
    
    @staticmethod
    def transactions() -> TransactionRepository:
        """Get TransactionRepository instance."""
        return TransactionRepository()
    
    @staticmethod
    def categories() -> CategoryRepository:
        """Get CategoryRepository instance."""
        return CategoryRepository()
    
    @staticmethod
    def members() -> MemberRepository:
        """Get MemberRepository instance."""
        return MemberRepository()
    
    @staticmethod
    def budgets() -> BudgetRepository:
        """Get BudgetRepository instance."""
        return BudgetRepository()


__all__ = [
    # Entities
    "Transaction",
    "TransactionStatus",
    "Category",
    "Member",
    "MemberMapping",
    "AccountMemberMapping",
    "Budget",
    "LearningRule",
    # Base classes
    "FilterSpec",
    "FilterBuilder",
    "BaseRepository",
    # Repositories
    "TransactionRepository",
    "CategoryRepository",
    "MemberRepository",
    "BudgetRepository",
    # Factory
    "RepositoryFactory",
]
