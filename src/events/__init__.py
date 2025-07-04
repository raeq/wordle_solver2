"""
Event system for game state management.

This package provides an implementation of the observer pattern for the Wordle Solver,
enabling loose coupling between components through an event-based architecture.
"""

# Import and export concrete observer implementations
from .concrete_observers import (
    GameStatisticsObserver,
    KeyboardStateObserver,
    LoggingObserver,
)

# Import and export enumerations
from .enums import EventType, GameState, LetterState

# Import and export event classes
from .event import (
    GameEvent,
    GameStateChangedEvent,
    LetterGuessedEvent,
    WordGuessedEvent,
)

# Import and export observer interfaces
from .observer import GameEventBus, GameStateObserver

__all__ = [
    # Enumerations
    "EventType",
    "GameState",
    "LetterState",
    # Event classes
    "GameEvent",
    "LetterGuessedEvent",
    "WordGuessedEvent",
    "GameStateChangedEvent",
    # Observer interfaces
    "GameStateObserver",
    "GameEventBus",
    # Concrete observers
    "KeyboardStateObserver",
    "GameStatisticsObserver",
    "LoggingObserver",
]
