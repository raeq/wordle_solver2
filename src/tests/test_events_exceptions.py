"""Tests for the event system exceptions.

This module contains tests for the custom exception classes used in the event system,
ensuring they're properly raised and contain the expected information.
"""

import pytest

from events.enums import GameState, LetterState
from events.event import (
    GameEvent,
    GameStateChangedEvent,
    LetterGuessedEvent,
    WordGuessedEvent,
)
from events.exceptions import (
    EventBusConfigurationError,
    EventCyclicReferenceError,
    EventPublishingError,
    EventSubscriptionError,
    EventValidationError,
    InvalidEventTypeError,
    ObserverNotificationError,
    WordleEventSystemException,
)
from events.observer import GameEventBus, GameStateObserver


class TestWordleEventSystemExceptions:
    """Tests for the base WordleEventSystemException class."""

    def test_base_exception_creation(self):
        """Test creating the base exception with a message."""
        error_message = "Test error message"
        exception = WordleEventSystemException(error_message)

        assert exception.message == error_message
        assert str(exception) == error_message

    def test_base_exception_inheritance(self):
        """Test that the base exception inherits from Exception."""
        exception = WordleEventSystemException("Test")

        assert isinstance(exception, Exception)


class TestEventSubscriptionError:
    """Tests for the EventSubscriptionError exception."""

    def test_basic_error(self):
        """Test creating a basic subscription error."""
        message = "Failed to subscribe"
        error = EventSubscriptionError(message)

        assert error.observer_type is None
        assert error.message == message
        assert str(error) == message

    def test_with_observer_type(self):
        """Test creating a subscription error with observer type."""
        message = "Failed to subscribe"
        observer_type = "TestObserver"
        error = EventSubscriptionError(message, observer_type)

        assert error.observer_type == observer_type
        assert error.message == f"{message} (Observer type: {observer_type})"
        assert str(error) == f"{message} (Observer type: {observer_type})"

    def test_raised_by_event_bus(self):
        """Test that EventSubscriptionError is raised by GameEventBus."""
        bus = GameEventBus()

        # Create an object that doesn't implement GameStateObserver
        invalid_observer = object()

        with pytest.raises(EventSubscriptionError) as exc_info:
            bus.subscribe(invalid_observer)

        assert "Observer must implement GameStateObserver interface" in str(
            exc_info.value
        )
        assert exc_info.value.observer_type == "object"

        # Test duplicate subscription
        class TestObserver(GameStateObserver):
            def notify(self, event):
                pass

        observer = TestObserver()
        bus.subscribe(observer)

        with pytest.raises(EventSubscriptionError) as exc_info:
            bus.subscribe(observer)

        assert "Observer already subscribed as global observer" in str(exc_info.value)
        assert exc_info.value.observer_type == "TestObserver"


class TestEventPublishingError:
    """Tests for the EventPublishingError exception."""

    def test_basic_error(self):
        """Test creating a basic publishing error."""
        message = "Failed to publish event"
        error = EventPublishingError(message)

        assert error.event_type is None
        assert error.message == message
        assert str(error) == message

    def test_with_event_type(self):
        """Test creating a publishing error with event type."""
        message = "Failed to publish event"
        event_type = "test_event"
        error = EventPublishingError(message, event_type)

        assert error.event_type == event_type
        assert error.message == f"{message} (Event type: {event_type})"
        assert str(error) == f"{message} (Event type: {event_type})"

    def test_raised_by_event_bus(self):
        """Test that EventPublishingError is raised by GameEventBus."""
        bus = GameEventBus()

        with pytest.raises(EventPublishingError) as exc_info:
            bus.publish(None)

        assert "Cannot publish None event" in str(exc_info.value)

        # Test with invalid event object (no event_type attribute)
        class InvalidEvent:
            pass

        invalid_event = InvalidEvent()

        with pytest.raises(EventPublishingError) as exc_info:
            bus.publish(invalid_event)

        assert "Invalid event type: InvalidEvent, must be a GameEvent subclass" in str(
            exc_info.value
        )


class TestInvalidEventTypeError:
    """Tests for the InvalidEventTypeError exception."""

    def test_error_creation(self):
        """Test creating an invalid event type error."""
        event_type = "unknown_event"
        error = InvalidEventTypeError(event_type)

        assert error.event_type == event_type
        assert error.message == f"Invalid event type: {event_type}"
        assert str(error) == f"Invalid event type: {event_type}"


class TestObserverNotificationError:
    """Tests for the ObserverNotificationError exception."""

    def test_basic_error(self):
        """Test creating a basic notification error."""
        message = "Failed to notify observer"
        error = ObserverNotificationError(message)

        assert error.observer_id is None
        assert error.event_id is None
        assert error.message == message
        assert str(error) == message

    def test_with_ids(self):
        """Test creating a notification error with observer and event IDs."""
        message = "Failed to notify observer"
        observer_id = "TestObserver"
        event_id = "event-123"
        error = ObserverNotificationError(message, observer_id, event_id)

        assert error.observer_id == observer_id
        assert error.event_id == event_id
        assert (
            error.message
            == f"{message} (Observer ID: {observer_id}, Event ID: {event_id})"
        )
        assert (
            str(error)
            == f"{message} (Observer ID: {observer_id}, Event ID: {event_id})"
        )

    def test_with_only_observer_id(self):
        """Test creating a notification error with only observer ID."""
        message = "Failed to notify observer"
        observer_id = "TestObserver"
        error = ObserverNotificationError(message, observer_id)

        assert error.observer_id == observer_id
        assert error.event_id is None
        assert error.message == f"{message} (Observer ID: {observer_id})"
        assert str(error) == f"{message} (Observer ID: {observer_id})"

    def test_raised_by_event_bus(self):
        """Test that ObserverNotificationError is raised by GameEventBus."""
        bus = GameEventBus()
        event = GameEvent()

        # Create an observer that raises an exception when notified
        class FailingObserver(GameStateObserver):
            def notify(self, event):
                raise ValueError("Test error")

        observer = FailingObserver()
        bus.subscribe(observer)

        with pytest.raises(ObserverNotificationError) as exc_info:
            bus.publish(event)

        assert "Observer notification failed: Test error" in str(exc_info.value)
        assert exc_info.value.observer_id == "FailingObserver"
        assert exc_info.value.event_id == event.event_id


class TestEventValidationError:
    """Tests for the EventValidationError exception."""

    def test_basic_error(self):
        """Test creating a basic validation error."""
        message = "Validation failed"
        error = EventValidationError(message)

        assert error.field_name is None
        assert error.message == message
        assert str(error) == message

    def test_with_field_name(self):
        """Test creating a validation error with a field name."""
        message = "Field cannot be empty"
        field_name = "letter"
        error = EventValidationError(message, field_name)

        assert error.field_name == field_name
        assert error.message == f"Validation error in field '{field_name}': {message}"
        assert str(error) == f"Validation error in field '{field_name}': {message}"

    def test_raised_by_letter_guessed_event(self):
        """Test that EventValidationError is raised by LetterGuessedEvent."""
        with pytest.raises(EventValidationError) as exc_info:
            LetterGuessedEvent(123, LetterState.CORRECT)

        assert "Letter must be a string" in str(exc_info.value)

    def test_raised_by_word_guessed_event(self):
        """Test that EventValidationError is raised by WordGuessedEvent."""
        with pytest.raises(EventValidationError) as exc_info:
            WordGuessedEvent(123, [LetterState.CORRECT])

        assert "Word must be a string" in str(exc_info.value)

    def test_raised_by_game_state_changed_event(self):
        """Test that EventValidationError is raised by GameStateChangedEvent."""
        with pytest.raises(EventValidationError) as exc_info:
            GameStateChangedEvent("INVALID", GameState.STARTED)

        assert "Old state must be a GameState enum value" in str(exc_info.value)
        assert exc_info.value.field_name == "old_state"

        with pytest.raises(EventValidationError) as exc_info:
            GameStateChangedEvent(GameState.STARTED, "INVALID")

        assert "New state must be a GameState enum value" in str(exc_info.value)
        assert exc_info.value.field_name == "new_state"


class TestEventBusConfigurationError:
    """Tests for the EventBusConfigurationError exception."""

    def test_error_creation(self):
        """Test creating an event bus configuration error."""
        message = "Invalid configuration"
        error = EventBusConfigurationError(message)

        assert error.message == f"Event bus configuration error: {message}"
        assert str(error) == f"Event bus configuration error: {message}"


class TestEventCyclicReferenceError:
    """Tests for the EventCyclicReferenceError exception."""

    def test_error_creation(self):
        """Test creating a cyclic reference error."""
        cycle_depth = 10
        max_depth = 5
        error = EventCyclicReferenceError(cycle_depth, max_depth)

        assert error.cycle_depth == cycle_depth
        assert error.max_depth == max_depth
        assert (
            error.message
            == f"Event processing cycle detected (depth: {cycle_depth}, max allowed: {max_depth})"
        )
        assert (
            str(error)
            == f"Event processing cycle detected (depth: {cycle_depth}, max allowed: {max_depth})"
        )
