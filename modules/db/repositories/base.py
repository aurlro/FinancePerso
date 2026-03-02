"""Base repository pattern for FinancePerso."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base class for all repositories."""

    @abstractmethod
    def get_by_id(self, id: int) -> T | None:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self, filters: dict[str, Any] | None = None) -> list[T]:
        """Get all entities, optionally filtered."""
        pass

    @abstractmethod
    def create(self, data: dict[str, Any]) -> T:
        """Create new entity."""
        pass

    @abstractmethod
    def update(self, id: int, data: dict[str, Any]) -> T | None:
        """Update entity by ID."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass
