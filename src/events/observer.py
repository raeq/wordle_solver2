"""
Observer interfaces for the event system.

This module provides the core interfaces for the observer pattern implementation,
allowing components to subscribe to and receive events.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .event import GameEvent


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
        """
        if event_type:
            if event_type not in self._observers:
                self._observers[event_type] = []
            self._observers[event_type].append(observer)
        else:
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
        """
        # Notify observers registered for this specific event type
        if event.event_type in self._observers:
            for observer in self._observers[event.event_type]:
                observer.notify(event)

        # Notify global observers that listen to all events
        for observer in self._global_observers:
            observer.notify(event)
