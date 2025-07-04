"""
Specific exceptions for the event system.

This module provides specialized exceptions for different error scenarios
in the Wordle Solver's event system.
"""

from .base import WordleEventSystemException


class EventSubscriptionError(WordleEventSystemException):
    """Raised when there's an error during event subscription."""

    def __init__(self, message: str, observer_type: str = None):
        """Initialize the exception.

        Args:
            message: A human-readable error description
            observer_type: Optional type name of the observer causing the issue
        """
        self.observer_type = observer_type
        full_message = message
        if observer_type:
            full_message = f"{message} (Observer type: {observer_type})"
        super().__init__(full_message)


class EventPublishingError(WordleEventSystemException):
    """Raised when there's an error during event publishing."""

    def __init__(self, message: str, event_type: str = None):
        """Initialize the exception.

        Args:
            message: A human-readable error description
            event_type: Optional type name of the event being published
        """
        self.event_type = event_type
        full_message = message
        if event_type:
            full_message = f"{message} (Event type: {event_type})"
        super().__init__(full_message)


class InvalidEventTypeError(WordleEventSystemException):
    """Raised when an invalid event type is specified."""

    def __init__(self, event_type):
        """Initialize the exception.

        Args:
            event_type: The invalid event type that was specified
        """
        self.event_type = event_type
        message = f"Invalid event type: {event_type}"
        super().__init__(message)


class ObserverNotificationError(WordleEventSystemException):
    """Raised when notification of an observer fails."""

    def __init__(self, message: str, observer_id: str = None, event_id: str = None):
        """Initialize the exception.

        Args:
            message: A human-readable error description
            observer_id: Optional identifier for the observer that failed
            event_id: Optional identifier for the event that was being processed
        """
        self.observer_id = observer_id
        self.event_id = event_id

        details = []
        if observer_id:
            details.append(f"Observer ID: {observer_id}")
        if event_id:
            details.append(f"Event ID: {event_id}")

        full_message = message
        if details:
            full_message = f"{message} ({', '.join(details)})"

        super().__init__(full_message)


class EventValidationError(WordleEventSystemException):
    """Raised when an event fails validation."""

    def __init__(self, message: str, field_name: str = None):
        """Initialize the exception.

        Args:
            message: A human-readable error description
            field_name: Optional name of the field that failed validation
        """
        self.field_name = field_name
        full_message = message
        if field_name:
            full_message = f"Validation error in field '{field_name}': {message}"
        super().__init__(full_message)


class EventBusConfigurationError(WordleEventSystemException):
    """Raised when there is a configuration issue with the event bus."""

    def __init__(self, message: str):
        """Initialize the exception.

        Args:
            message: A human-readable error description
        """
        super().__init__(f"Event bus configuration error: {message}")


class EventCyclicReferenceError(WordleEventSystemException):
    """Raised when a cyclic reference is detected in event processing."""

    def __init__(self, cycle_depth: int, max_depth: int):
        """Initialize the exception.

        Args:
            cycle_depth: The current depth of the event processing cycle
            max_depth: The maximum allowed depth before triggering this error
        """
        self.cycle_depth = cycle_depth
        self.max_depth = max_depth
        message = f"Event processing cycle detected (depth: {cycle_depth}, max allowed: {max_depth})"
        super().__init__(message)
