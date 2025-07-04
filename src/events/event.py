"""
Core event system implementation.

This module provides the core event classes for the Wordle Solver application,
enabling loose coupling between components through an event-based architecture.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .enums import EventType, GameState, LetterState
from .exceptions import EventValidationError


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

        Raises:
            TypeError: If letter is not a string
        """
        super().__init__(source)
        if not isinstance(letter, str):
            raise EventValidationError(
                f"Letter must be a string, got {type(letter).__name__}"
            )
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

        Raises:
            TypeError: If word is not a string
        """
        super().__init__(source)
        if not isinstance(word, str):
            raise EventValidationError(
                f"Word must be a string, got {type(word).__name__}"
            )
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

        Raises:
            EventValidationError: If either state is not a GameState enum value
        """
        super().__init__(source)
        if not isinstance(old_state, GameState):
            raise EventValidationError(
                f"Old state must be a GameState enum value, got {type(old_state).__name__}",
                "old_state",
            )
        if not isinstance(new_state, GameState):
            raise EventValidationError(
                f"New state must be a GameState enum value, got {type(new_state).__name__}",
                "new_state",
            )

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


class GameStartedEvent(GameEvent):
    """Event fired when a new game is started."""

    event_type = EventType.GAME_STARTED

    def __init__(self, game_id: str, mode: str = None, source: str = None):
        """Initialize a game started event.

        Args:
            game_id: The unique identifier for the game
            mode: The mode in which the game is played (optional)
            source: Identifier of the component that generated the event
        """
        super().__init__(source)
        self.game_id = game_id
        self.mode = mode

    def get_event_data(self) -> Dict[str, Any]:
        """Get game started event data.

        Returns:
            Dictionary containing event data including game ID and mode
        """
        data = super().get_event_data()
        data.update({"game_id": self.game_id, "mode": self.mode})
        return data


class GameEndedEvent(GameEvent):
    """Event fired when a game ends (won or lost)."""

    event_type = EventType.GAME_ENDED

    def __init__(
        self,
        game_id: str,
        state: GameState,
        guesses: int,
        is_won: bool,
        target_word: str = None,
        mode: str = None,
        source: str = None,
    ):
        """Initialize a game ended event.

        Args:
            game_id: The unique identifier for the game
            state: The final state of the game (GameState enum value)
            guesses: The number of guesses taken
            is_won: Whether the game was won or lost
            target_word: The target word (optional, for lost games)
            mode: The mode in which the game was played (optional)
            source: Identifier of the component that generated the event

        Raises:
            EventValidationError: If state is not a GameState enum value
        """
        super().__init__(source)
        self.game_id = game_id
        self.state = state
        self.guesses = guesses
        self.is_won = is_won
        self.target_word = target_word
        self.mode = mode

    def get_event_data(self) -> Dict[str, Any]:
        """Get game ended event data.

        Returns:
            Dictionary containing event data including game ID, final state, and guesses
        """
        data = super().get_event_data()
        data.update(
            {
                "game_id": self.game_id,
                "state": str(self.state),
                "guesses": self.guesses,
                "is_won": self.is_won,
                "target_word": self.target_word,
                "mode": self.mode,
            }
        )
        return data


class GameSaveSuccessEvent(GameEvent):
    """Event fired when a game is successfully saved by StatsManager."""

    event_type = EventType.GAME_SAVE_SUCCESS

    def __init__(self, game_record: Dict[str, Any], source: str = None):
        """Initialize a game save success event.

        Args:
            game_record: The record of the game that was saved
            source: Identifier of the component that generated the event
        """
        super().__init__(source)
        self.game_record = game_record

    def get_event_data(self) -> Dict[str, Any]:
        """Get game save success event data.

        Returns:
            Dictionary containing event data including the saved game record
        """
        data = super().get_event_data()
        data.update({"game_record": self.game_record})
        return data
