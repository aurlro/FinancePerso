"""
Extended tests for events.py module (EventBus).
"""

from modules.core.events import EventBus, on_event


class TestEventBusExtended:
    """Extended tests for EventBus functionality."""

    def test_singleton_pattern(self):
        """Test that EventBus is a singleton."""
        bus1 = EventBus()
        bus2 = EventBus()
        assert bus1 is bus2

    def test_emit_with_no_subscribers(self):
        """Test emitting event with no subscribers doesn't error."""
        bus = EventBus()
        bus.emit("nonexistent_event")  # Should not raise
        bus.emit("nonexistent_event", data="test")  # Should not raise

    def test_multiple_handlers_same_event(self):
        """Test multiple handlers for same event."""
        bus = EventBus()
        results = []

        def handler1(data):
            results.append(f"h1:{data}")

        def handler2(data):
            results.append(f"h2:{data}")

        bus.subscribe("multi_event", handler1)
        bus.subscribe("multi_event", handler2)
        bus.emit("multi_event", data="test")

        assert len(results) == 2
        assert "h1:test" in results
        assert "h2:test" in results

    def test_unsubscribe_specific_handler(self):
        """Test unsubscribing specific handler."""
        bus = EventBus()
        results = []

        def handler1():
            results.append("h1")

        def handler2():
            results.append("h2")

        bus.subscribe("test_event", handler1)
        bus.subscribe("test_event", handler2)
        bus.unsubscribe("test_event", handler1)
        bus.emit("test_event")

        assert "h1" not in results
        assert "h2" in results

    def test_handler_exception_isolation(self):
        """Test that exception in one handler doesn't affect others."""
        bus = EventBus()
        results = []

        def failing_handler():
            raise ValueError("Test error")

        def success_handler():
            results.append("success")

        bus.subscribe("test_event", failing_handler)
        bus.subscribe("test_event", success_handler)

        # Should not raise exception
        bus.emit("test_event")

        assert "success" in results


class TestOnEventDecorator:
    """Tests for @on_event decorator."""

    def test_decorator_registration(self):
        """Test that decorator registers handler."""
        bus = EventBus()
        results = []

        @on_event("decorated_event")
        def my_handler(data):
            results.append(data)

        bus.emit("decorated_event", data="test")
        assert "test" in results

    def test_decorator_preserves_function(self):
        """Test that decorator preserves function metadata."""

        @on_event("test_event")
        def my_handler():
            """My docstring."""
            pass

        assert my_handler.__name__ == "my_handler"
        assert my_handler.__doc__ == "My docstring."


class TestEventBusClear:
    """Tests for clearing subscribers."""

    def test_clear_all_subscribers(self):
        """Test clearing all subscribers."""
        bus = EventBus()
        results = []

        def handler():
            results.append("called")

        bus.subscribe("event1", handler)
        bus.subscribe("event2", handler)
        bus.clear()

        bus.emit("event1")
        bus.emit("event2")

        assert len(results) == 0

    def test_clear_specific_event(self):
        """Test clearing subscribers for specific event."""
        bus = EventBus()
        results = []

        def handler():
            results.append("called")

        bus.subscribe("event1", handler)
        bus.subscribe("event2", handler)
        bus.clear("event1")

        bus.emit("event1")
        assert len(results) == 0

        bus.emit("event2")
        assert len(results) == 1
