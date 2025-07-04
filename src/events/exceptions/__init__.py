"""
Event system exceptions package.

This package provides specialized exceptions for the event system,
allowing for more specific error handling.
"""

from .base import WordleEventSystemException
from .event_exceptions import (
    EventBusConfigurationError,
    EventCyclicReferenceError,
    EventPublishingError,
    EventSubscriptionError,
    EventValidationError,
    InvalidEventTypeError,
    ObserverNotificationError,
)

__all__ = [
    "WordleEventSystemException",
    "EventSubscriptionError",
    "EventPublishingError",
    "InvalidEventTypeError",
    "ObserverNotificationError",
    "EventValidationError",
    "EventBusConfigurationError",
    "EventCyclicReferenceError",
]
