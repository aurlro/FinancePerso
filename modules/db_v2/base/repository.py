"""
Base Repository Abstract Class
==============================

Defines the interface for all repositories.
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, Any
import pandas as pd

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository implementing standard CRUD operations.

    Type Parameters:
        T: The entity dataclass type

    Example:
        >>> class TransactionRepository(BaseRepository[Transaction]):
        ...     def get_by_id(self, entity_id: int) -> Optional[Transaction]:
        ...         # Implementation
    """

    _table: str = ""  # Override in subclass
    _entity_class: type = object  # Override in subclass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Get entity by primary key.

        Args:
            entity_id: Primary key value

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(
        self,
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> pd.DataFrame:
        """
        Get all entities with optional filtering.

        Args:
            filters: Column-value pairs for filtering
            order_by: SQL ORDER BY clause
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            DataFrame with matching entities
        """
        pass

    @abstractmethod
    def create(self, entity: T) -> int:
        """
        Create a new entity.

        Args:
            entity: Entity to create

        Returns:
            ID of created entity
        """
        pass

    @abstractmethod
    def update(self, entity_id: int, data: dict[str, Any]) -> bool:
        """
        Update entity fields.

        Args:
            entity_id: ID of entity to update
            data: Field-value pairs to update

        Returns:
            True if updated, False if not found
        """
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """
        Delete entity by ID.

        Args:
            entity_id: ID of entity to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """
        Check if entity exists.

        Args:
            entity_id: ID to check

        Returns:
            True if exists, False otherwise
        """
        pass

    def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        """
        Count entities matching filters.

        Args:
            filters: Column-value pairs for filtering

        Returns:
            Count of matching entities
        """
        # Default implementation - override for efficiency
        df = self.get_all(filters=filters, limit=None)
        return len(df)

    def bulk_create(self, entities: list[T]) -> int:
        """
        Create multiple entities.

        Args:
            entities: List of entities to create

        Returns:
            Number of entities created
        """
        count = 0
        for entity in entities:
            self.create(entity)
            count += 1
        return count

    def bulk_update(self, entity_ids: list[int], data: dict[str, Any]) -> int:
        """
        Update multiple entities.

        Args:
            entity_ids: IDs of entities to update
            data: Field-value pairs to update

        Returns:
            Number of entities updated
        """
        count = 0
        for entity_id in entity_ids:
            if self.update(entity_id, data):
                count += 1
        return count

    def bulk_delete(self, entity_ids: list[int]) -> int:
        """
        Delete multiple entities.

        Args:
            entity_ids: IDs of entities to delete

        Returns:
            Number of entities deleted
        """
        count = 0
        for entity_id in entity_ids:
            if self.delete(entity_id):
                count += 1
        return count
