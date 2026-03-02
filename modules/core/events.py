"""Event bus for decoupled communication between modules.

This module provides a simple event bus pattern to eliminate circular dependencies
between cache_manager and database modules.

Example:
    # Publisher (db module)
    from modules.core.events import EventBus
    EventBus.emit("transactions.changed", tx_id=123)

    # Subscriber (cache module)
    from modules.core.events import on_event

    @on_event("transactions.changed")
    def clear_transaction_cache(**kwargs):
        # Clear cache logic here
        pass
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, Optional


class EventBus:
    """Simple in-process event bus for decoupled communication.

    This class implements the Observer pattern to allow modules to communicate
    without direct imports, eliminating circular dependencies.
    This is a singleton class.

    Attributes:
        _listeners: Dictionary mapping event names to lists of callback functions.
        _instance: Singleton instance.
    """

    _instance: Optional["EventBus"] = None
    _listeners: dict[str, list[Callable]] = {}

    def __new__(cls) -> "EventBus":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def subscribe(cls, event: str, callback: Callable) -> None:
        """Subscribe a callback to an event.

        Args:
            event: The event name to subscribe to.
            callback: Function to call when the event is emitted.

        Example:
            def on_transaction_changed(**kwargs):
                print(f"Transaction {kwargs.get('tx_id')} changed")

            EventBus.subscribe("transactions.changed", on_transaction_changed)
        """
        if event not in cls._listeners:
            cls._listeners[event] = []
        cls._listeners[event].append(callback)

    @classmethod
    def unsubscribe(cls, event: str, callback: Callable) -> bool:
        """Unsubscribe a callback from an event.

        Args:
            event: The event name to unsubscribe from.
            callback: The callback function to remove.

        Returns:
            True if the callback was found and removed, False otherwise.
        """
        if event in cls._listeners and callback in cls._listeners[event]:
            cls._listeners[event].remove(callback)
            return True
        return False

    @classmethod
    def emit(cls, event: str, **kwargs: Any) -> None:
        """Emit an event to all subscribers.

        Args:
            event: The event name to emit.
            **kwargs: Data to pass to subscribers.

        Note:
            Exceptions in handlers are caught and logged to prevent
            one handler's failure from affecting others.
        """
        from modules.logger import logger

        handlers = cls._listeners.get(event, [])
        for callback in handlers:
            try:
                callback(**kwargs)
            except Exception as e:
                logger.error(f"Event handler error for '{event}': {e}")

    @classmethod
    def clear(cls, event: str | None = None) -> None:
        """Clear all listeners or listeners for a specific event.

        Args:
            event: Optional event name to clear subscribers for.
                   If None, clears all subscribers.
        """
        if event is None:
            cls._listeners.clear()
        elif event in cls._listeners:
            del cls._listeners[event]

    @classmethod
    def get_subscribers(cls, event: str | None = None) -> list[str]:
        """Get list of subscribed events or handlers for a specific event.

        Args:
            event: Optional event name to get handlers for.

        Returns:
            List of event names if no event specified,
            or list of handler names for the specified event.
        """
        if event is None:
            return list(cls._listeners.keys())
        return [h.__name__ for h in cls._listeners.get(event, [])]


def on_event(event: str):
    """Decorator to subscribe a function to an event.

    Args:
        event: The event name to subscribe to.

    Returns:
        Decorator function that registers the handler.

    Example:
        @on_event("transactions.changed")
        def invalidate_cache(**kwargs):
            # This will be called when transactions.changed is emitted
            pass
    """

    def decorator(func: Callable) -> Callable:
        EventBus.subscribe(event, func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Keep reference for testing
        wrapper._event_handler = True
        wrapper._event_name = event
        return wrapper

    return decorator
