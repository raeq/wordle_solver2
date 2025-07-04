"""
Observer interfaces for the event system.

This module provides the core interfaces for the observer pattern implementation,
allowing components to subscribe to and receive events.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .event import GameEvent
from .exceptions import (
    EventPublishingError,
    EventSubscriptionError,
    ObserverNotificationError,
)


class GameStateObserver(ABC):
    """Interface for all observers that want to be notified of game events."""

    @abstractmethod
    def notify(self, event: GameEvent) -> None:
        """Called when a relevant event occurs.

        Args:
            event: The event that occurred
        """
        pass


class GameEventBus:
    """Central event dispatcher for the game."""

    def __init__(self):
        """Initialize a new event bus with empty observer lists."""
        self._observers: Dict[str, List[GameStateObserver]] = {}
        self._global_observers: List[GameStateObserver] = []

    def subscribe(
        self, observer: GameStateObserver, event_type: Optional[str] = None
    ) -> None:
        """Add an observer to be notified of events.

        Args:
            observer: The observer to add
            event_type: The specific event type to subscribe to, or None to receive all events

        Raises:
            EventSubscriptionError: If the observer is not valid or already subscribed
        """
        if not isinstance(observer, GameStateObserver):
            observer_type = type(observer).__name__
            raise EventSubscriptionError(
                "Observer must implement GameStateObserver interface",
                observer_type=observer_type,
            )

        if event_type:
            if event_type not in self._observers:
                self._observers[event_type] = []
            if observer in self._observers[event_type]:
                observer_type = type(observer).__name__
                raise EventSubscriptionError(
                    f"Observer already subscribed to event type: {event_type}",
                    observer_type=observer_type,
                )
            self._observers[event_type].append(observer)
        else:
            if observer in self._global_observers:
                observer_type = type(observer).__name__
                raise EventSubscriptionError(
                    "Observer already subscribed as global observer",
                    observer_type=observer_type,
                )
            self._global_observers.append(observer)

    def unsubscribe(
        self, observer: GameStateObserver, event_type: Optional[str] = None
    ) -> None:
        """Remove an observer from receiving notifications.

        Args:
            observer: The observer to remove
            event_type: The specific event type to unsubscribe from, or None to unsubscribe from all
        """
        if event_type:
            if event_type in self._observers:
                if observer in self._observers[event_type]:
                    self._observers[event_type].remove(observer)
        else:
            if observer in self._global_observers:
                self._global_observers.remove(observer)
            # Also remove from all specific event types
            for event_list in self._observers.values():
                if observer in event_list:
                    event_list.remove(observer)

    def publish(self, event: GameEvent) -> None:
        """Notify all relevant observers of an event.

        Args:
            event: The event to publish

        Raises:
            EventPublishingError: If there's an error during event publishing
            ObserverNotificationError: If an observer fails to process the event
        """
        # Basic validation
        if event is None:
            raise EventPublishingError("Cannot publish None event")

        # Type validation
        if not isinstance(event, GameEvent):
            event_type_name = type(event).__name__
            raise EventPublishingError(
                f"Invalid event type: {event_type_name}, must be a GameEvent subclass",
                event_type=event_type_name,
            )

        # Event attribute validation
        try:
            event_type = event.event_type
        except AttributeError:
            raise EventPublishingError(
                "Invalid event object: missing event_type attribute",
                event_type="unknown",
            )
        # Additional event_type validation
        if event_type is None or (
            hasattr(event_type, "__class__")
            and event_type.__class__.__name__ == "NoneType"
        ):
            raise EventPublishingError(
                "Invalid event_type: event_type cannot be None",
                event_type=event_type,
            )
        # Optionally, check for correct type (uncomment if you want strict type checking)
        # from events.enums import EventType
        # if not isinstance(event_type, EventType):
        #     raise EventPublishingError(
        #         f"Invalid event_type: {event_type} is not an EventType",
        #         event_type=event_type,
        #     )

        # Validate event_id is present and has the correct format
        try:
            event_id = event.event_id
            if not isinstance(event_id, str) or not event_id:
                raise EventPublishingError(
                    f"Invalid event_id: must be a non-empty string, got: {type(event_id).__name__}",
                    event_type=str(event_type),
                )
        except AttributeError:
            raise EventPublishingError(
                "Invalid event object: missing event_id attribute",
                event_type=str(event_type),
            )

        # Validate timestamp is present and has the correct type
        try:
            timestamp = event.timestamp
            if not timestamp:
                raise EventPublishingError(
                    "Event has an empty timestamp",
                    event_type=str(event_type),
                )
        except AttributeError:
            raise EventPublishingError(
                "Invalid event object: missing timestamp attribute",
                event_type=str(event_type),
            )

        # Convert enum to string to match the keys in _observers
        event_type_str = str(event_type)

        # Make copies of observer lists to avoid issues if lists are modified during notification
        specific_observers = list(self._observers.get(event_type_str, []))
        global_observers = list(self._global_observers)

        # Validate the event has expected data structure through get_event_data
        try:
            event_data = event.get_event_data()
            if not isinstance(event_data, dict):
                raise EventPublishingError(
                    f"Event.get_event_data() must return a dictionary, got: {type(event_data).__name__}",
                    event_type=event_type_str,
                )
        except Exception as e:
            raise EventPublishingError(
                f"Failed to get event data: {str(e)}",
                event_type=event_type_str,
            ) from e

        # Notify observers registered for this specific event type
        for observer in specific_observers:
            try:
                observer.notify(event)
            except Exception as e:
                observer_name = type(observer).__name__
                raise ObserverNotificationError(
                    f"Observer notification failed: {str(e)}",
                    observer_id=observer_name,
                    event_id=event.event_id,
                ) from e

        # Notify global observers that listen to all events
        for observer in global_observers:
            try:
                observer.notify(event)
            except Exception as e:
                observer_name = type(observer).__name__
                raise ObserverNotificationError(
                    f"Observer notification failed: {str(e)}",
                    observer_id=observer_name,
                    event_id=event.event_id,
                ) from e
