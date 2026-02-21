"""
Unit of Work Pattern
====================

Manages transactions across multiple repositories atomically.
"""

from contextlib import contextmanager
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from modules.db_v2.repositories.transaction_repository import TransactionRepository
    from modules.db_v2.repositories.category_repository import CategoryRepository
    from modules.db_v2.repositories.member_repository import MemberRepository


class UnitOfWork:
    """
    Unit of Work pattern for transaction management.

    Ensures atomic operations across multiple repositories.
    Automatically commits on success, rolls back on exception.

    Example:
        >>> with UnitOfWork() as uow:
        ...     tx = uow.transactions.get_by_id(1)
        ...     uow.transactions.update_category(tx.id, "Food")
        ...     # Auto-commit if no exception
    """

    def __init__(self, connection=None):
        """
        Initialize Unit of Work.

        Args:
            connection: Optional existing connection (for nested UoW)
        """
        self._conn = connection
        self._owns_connection = connection is None
        self._repositories: dict = {}

    def __enter__(self) -> "UnitOfWork":
        """Enter context - acquire connection if needed."""
        if self._owns_connection:
            from modules.db.connection import get_db_connection

            self._conn = get_db_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - commit/rollback and cleanup."""
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()

        if self._owns_connection:
            self._conn.close()

        # Clear repositories to release references
        self._repositories.clear()

    @property
    def connection(self):
        """Get underlying database connection."""
        return self._conn

    @property
    def transactions(self) -> "TransactionRepository":
        """Get transaction repository."""
        if "transactions" not in self._repositories:
            from modules.db_v2.repositories.transaction_repository import (
                TransactionRepository,
            )

            self._repositories["transactions"] = TransactionRepository(self._conn)
        return self._repositories["transactions"]

    @property
    def categories(self) -> "CategoryRepository":
        """Get category repository."""
        if "categories" not in self._repositories:
            from modules.db_v2.repositories.category_repository import (
                CategoryRepository,
            )

            self._repositories["categories"] = CategoryRepository(self._conn)
        return self._repositories["categories"]

    @property
    def members(self) -> "MemberRepository":
        """Get member repository."""
        if "members" not in self._repositories:
            from modules.db_v2.repositories.member_repository import MemberRepository

            self._repositories["members"] = MemberRepository(self._conn)
        return self._repositories["members"]


@contextmanager
def unit_of_work():
    """
    Convenience context manager for Unit of Work.

    Example:
        >>> with unit_of_work() as uow:
        ...     tx = uow.transactions.get_by_id(1)
        ...     uow.transactions.update_category(tx.id, "Food")
    """
    with UnitOfWork() as uow:
        yield uow
