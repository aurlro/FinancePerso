"""Core module for cross-cutting concerns."""

from modules.core.events import EventBus, on_event

__all__ = ["EventBus", "on_event"]
