"""
Core event system implementation.

This module provides the core event classes for the Wordle Solver application,
enabling loose coupling between components through an event-based architecture.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .enums import EventType, GameState, LetterState


class GameEvent:
    """Base class for all game events.

    This is the foundation of the observer pattern implementation,
    representing events that can be published to observers.
    """

    event_type: EventType = EventType.BASE_EVENT

    def __init__(self, source: Optional[str] = None):
        """Initialize a new game event.

        Args:
            source: Identifier of the component that generated the event
        """
        self.source = source
        # Add immutable timestamp when the event is created
        self._timestamp = datetime.now(timezone.utc)
        # Add a globally unique identifier for this event
        self._event_id = str(uuid.uuid4())

    @property
    def timestamp(self) -> datetime:
        """Get the immutable timestamp of when this event was created.

        Returns:
            UTC timestamp as a datetime object
        """
        return self._timestamp

    @property
    def event_id(self) -> str:
        """Get the globally unique identifier for this event.

        Returns:
            A string containing the event's GUID
        """
        return self._event_id

    def get_event_data(self) -> Dict[str, Any]:
        """Get event data as a dictionary for processing by observers.

        Returns:
            Dictionary containing event data
        """
        return {
            "event_id": self._event_id,
            "event_type": str(self.event_type),
            "source": self.source,
            "timestamp": self._timestamp.isoformat(),
        }


class LetterGuessedEvent(GameEvent):
    """Event fired when a letter is guessed."""

    event_type = EventType.LETTER_GUESSED

    def __init__(self, letter: str, result: LetterState, source: Optional[str] = None):
        """Initialize a letter guessed event.

        Args:
            letter: The guessed letter
            result: The result (LetterState.CORRECT, LetterState.PRESENT, or LetterState.ABSENT)
            source: Identifier of the component that generated the event
        """
        super().__init__(source)
        self.letter = letter
        self.result = result

    def get_event_data(self) -> Dict[str, Any]:
        """Get letter guessed event data.

        Returns:
            Dictionary containing event data including letter and result
        """
        data = super().get_event_data()
        data.update({"letter": self.letter, "result": str(self.result)})
        return data


class WordGuessedEvent(GameEvent):
    """Event fired when a complete word is guessed."""

    event_type = EventType.WORD_GUESSED

    def __init__(
        self, word: str, results: List[LetterState], source: Optional[str] = None
    ):
        """Initialize a word guessed event.

        Args:
            word: The guessed word
            results: List of results for each letter (LetterState values)
            source: Identifier of the component that generated the event
        """
        super().__init__(source)
        self.word = word
        self.results = results

    def get_event_data(self) -> Dict[str, Any]:
        """Get word guessed event data.

        Returns:
            Dictionary containing event data including word and results
        """
        data = super().get_event_data()
        data.update(
            {"word": self.word, "results": [str(result) for result in self.results]}
        )
        return data


class GameStateChangedEvent(GameEvent):
    """Event fired when the game state changes (e.g., game over, new game)."""

    event_type = EventType.GAME_STATE_CHANGED

    def __init__(
        self,
        old_state: GameState,
        new_state: GameState,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
    ):
        """Initialize a game state changed event.

        Args:
            old_state: Previous game state
            new_state: New game state
            metadata: Additional data about the state change
            source: Identifier of the component that generated the event
        """
        super().__init__(source)
        self.old_state = old_state
        self.new_state = new_state
        self.metadata = metadata or {}

    def get_event_data(self) -> Dict[str, Any]:
        """Get game state changed event data.

        Returns:
            Dictionary containing event data including old and new states
        """
        data = super().get_event_data()
        data.update(
            {
                "old_state": str(self.old_state),
                "new_state": str(self.new_state),
                "metadata": self.metadata,
            }
        )
        return data
