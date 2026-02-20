"""Tests for the EventBus module."""

import pytest
from modules.core.events import EventBus, on_event


class TestEventBus:
    """Test suite for EventBus functionality."""

    def setup_method(self):
        """Clear all listeners before each test."""
        EventBus.clear()

    def teardown_method(self):
        """Clean up after each test."""
        EventBus.clear()

    def test_subscribe_and_emit(self):
        """Test basic subscribe and emit functionality."""
        calls = []

        def handler(**kwargs):
            calls.append(kwargs)

        EventBus.subscribe("test.event", handler)
        EventBus.emit("test.event", data="value", id=123)

        assert len(calls) == 1
        assert calls[0]["data"] == "value"
        assert calls[0]["id"] == 123

    def test_decorator_subscription(self):
        """Test @on_event decorator."""
        calls = []

        @on_event("decorated.event")
        def handler(**kwargs):
            calls.append(kwargs)

        EventBus.emit("decorated.event", message="hello")

        assert len(calls) == 1
        assert calls[0]["message"] == "hello"

    def test_multiple_handlers(self):
        """Test multiple handlers for the same event."""
        calls = []

        def handler1(**kwargs):
            calls.append("handler1")

        def handler2(**kwargs):
            calls.append("handler2")

        EventBus.subscribe("multi", handler1)
        EventBus.subscribe("multi", handler2)

        EventBus.emit("multi")

        assert calls == ["handler1", "handler2"]

    def test_no_handlers(self):
        """Test emitting an event with no handlers - should not crash."""
        # Should not raise any exception
        EventBus.emit("unknown.event")
        assert True  # If we get here, test passed

    def test_unsubscribe(self):
        """Test unsubscribing a handler."""
        calls = []

        def handler(**kwargs):
            calls.append(kwargs)

        EventBus.subscribe("test", handler)
        assert EventBus.unsubscribe("test", handler) is True

        EventBus.emit("test")
        assert len(calls) == 0

    def test_unsubscribe_not_found(self):
        """Test unsubscribing a handler that wasn't subscribed."""

        def handler(**kwargs):
            pass

        assert EventBus.unsubscribe("test", handler) is False

    def test_handler_exception_isolation(self):
        """Test that one handler's exception doesn't affect others."""
        calls = []

        def failing_handler(**kwargs):
            raise ValueError("Intentional error")

        def working_handler(**kwargs):
            calls.append("working")

        EventBus.subscribe("test", failing_handler)
        EventBus.subscribe("test", working_handler)

        # Should not raise despite failing_handler
        EventBus.emit("test")

        assert calls == ["working"]

    def test_get_subscribers_all(self):
        """Test getting all subscribed events."""
        EventBus.subscribe("event1", lambda **_: None)
        EventBus.subscribe("event2", lambda **_: None)

        events = EventBus.get_subscribers()
        assert "event1" in events
        assert "event2" in events

    def test_get_subscribers_specific(self):
        """Test getting handlers for a specific event."""
        def handler1(**kwargs):
            pass

        def handler2(**kwargs):
            pass

        EventBus.subscribe("test", handler1)
        EventBus.subscribe("test", handler2)

        handlers = EventBus.get_subscribers("test")
        assert "handler1" in handlers
        assert "handler2" in handlers

    def test_clear(self):
        """Test clearing all listeners."""
        calls = []

        def handler(**kwargs):
            calls.append(kwargs)

        EventBus.subscribe("test", handler)
        EventBus.clear()

        EventBus.emit("test", data="should not be received")
        assert len(calls) == 0

    def test_decorator_preserves_function(self):
        """Test that @on_event decorator preserves function metadata."""

        @on_event("test")
        def my_handler(**kwargs):
            """My docstring."""
            pass

        assert my_handler.__name__ == "my_handler"
        assert hasattr(my_handler, "_event_handler")
        assert my_handler._event_name == "test"

    def test_emit_with_no_kwargs(self):
        """Test emitting without keyword arguments."""
        calls = []

        def handler(**kwargs):
            calls.append(kwargs)

        EventBus.subscribe("test", handler)
        EventBus.emit("test")

        assert calls == [{}]
