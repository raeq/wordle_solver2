"""
Enumerations for the event system.

This module contains all enumerations used by the event system for the Wordle Solver application.

Enum Value Ranges:
- GameState: 100-199 (base game functioning)
- LetterState: 200-299 (letter outcomes)
- EventType: 300-399 (event system)
"""

from enum import Enum


class WordleEnum(Enum):
    """Base class for all enumerations in the event system.

    Provides common functionality like string representation.
    """

    def __str__(self) -> str:
        """String representation for better readability in logs."""
        return self.name.lower()


class EventType(WordleEnum):
    """Enumeration of all possible event types."""

    BASE_EVENT = 300
    LETTER_GUESSED = 310
    WORD_GUESSED = 320
    GAME_STATE_CHANGED = 330


class GameState(WordleEnum):
    """Enumeration of all possible game states."""

    INITIALIZED = 100
    STARTED = 110
    IN_PROGRESS = 120
    GAME_OVER = 130
    PAUSED = 140


class LetterState(WordleEnum):
    """Enumeration of all possible letter states."""

    UNDEFINED = 200  # Default state before a letter has been guessed
    CORRECT = 210  # Letter is in the right position
    PRESENT = 220  # Letter is in the word but in the wrong position
    ABSENT = 230  # Letter is not in the word
