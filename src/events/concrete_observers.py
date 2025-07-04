"""
Concrete observer implementations for the game events.

This module provides implementations of the GameStateObserver interface
for common use cases in the game.
"""

import logging
from typing import Any, Dict, Optional, Set

from .enums import GameState, LetterState
from .event import (
    GameEvent,
    GameStateChangedEvent,
    LetterGuessedEvent,
    WordGuessedEvent,
)
from .observer import GameStateObserver

logger = logging.getLogger(__name__)


class KeyboardStateObserver(GameStateObserver):
    """Tracks the state of the keyboard based on game events."""

    def __init__(self):
        """Initialize with empty keyboard state tracking."""
        self.correct_letters: Set[str] = set()
        self.present_letters: Set[str] = set()
        self.absent_letters: Set[str] = set()
        self.all_guessed_letters: Set[str] = set()

    def notify(self, event: GameEvent) -> None:
        """Update keyboard state based on letter guessed events.

        Args:
            event: The game event
        """
        if isinstance(event, LetterGuessedEvent):
            letter = event.letter
            result = event.result

            self.all_guessed_letters.add(letter)

            # Update the appropriate set based on the result
            if result == LetterState.CORRECT:
                self.correct_letters.add(letter)
                # Remove from other sets if present
                self.present_letters.discard(letter)
                self.absent_letters.discard(letter)
            elif result == LetterState.PRESENT:
                # Only add as present if not already correct
                if letter not in self.correct_letters:
                    self.present_letters.add(letter)
                self.absent_letters.discard(letter)
            elif result == LetterState.ABSENT:
                # Only add as absent if not already correct or present
                if (
                    letter not in self.correct_letters
                    and letter not in self.present_letters
                ):
                    self.absent_letters.add(letter)

    def reset(self) -> None:
        """Reset the keyboard state."""
        self.correct_letters.clear()
        self.present_letters.clear()
        self.absent_letters.clear()
        self.all_guessed_letters.clear()

    def get_letter_state(self, letter: str) -> Optional[LetterState]:
        """Get the current state of a letter.

        Args:
            letter: The letter to check

        Returns:
            LetterState.CORRECT, LetterState.PRESENT, LetterState.ABSENT, or
            LetterState.UNDEFINED if the letter hasn't been guessed
        """
        if letter in self.correct_letters:
            return LetterState.CORRECT
        elif letter in self.present_letters:
            return LetterState.PRESENT
        elif letter in self.absent_letters:
            return LetterState.ABSENT
        else:
            return LetterState.UNDEFINED

    def get_keyboard_state(self) -> Dict[str, LetterState]:
        """Get the state of all guessed letters.

        Returns:
            A dictionary mapping letters to their states
        """
        state = {}
        for letter in self.all_guessed_letters:
            state[letter] = self.get_letter_state(letter)
        return state


class GameStatisticsObserver(GameStateObserver):
    """Tracks game statistics based on game events."""

    def __init__(self):
        """Initialize with empty statistics."""
        self.games_played = 0
        self.games_won = 0
        self.current_streak = 0
        self.max_streak = 0
        self.guess_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        self.letters_guessed = 0
        self.most_frequent_guess = None
        self.current_game_guesses = 0
        self.letter_frequency: Dict[str, int] = {}

    def notify(self, event: GameEvent) -> None:
        """Update statistics based on game events.

        Args:
            event: The game event
        """
        if isinstance(event, LetterGuessedEvent):
            self._handle_letter_guessed(event)
        elif isinstance(event, WordGuessedEvent):
            self._handle_word_guessed(event)
        elif isinstance(event, GameStateChangedEvent):
            self._handle_game_state_changed(event)

    def _handle_letter_guessed(self, event: LetterGuessedEvent) -> None:
        """Process letter guessed events.

        Args:
            event: The letter guessed event
        """
        self.letters_guessed += 1
        letter = event.letter
        self.letter_frequency[letter] = self.letter_frequency.get(letter, 0) + 1

        # Update most frequent guess
        if self.most_frequent_guess is None or self.letter_frequency[
            letter
        ] > self.letter_frequency.get(self.most_frequent_guess, 0):
            self.most_frequent_guess = letter

    def _handle_word_guessed(self, event: WordGuessedEvent) -> None:
        """Process word guessed events.

        Args:
            event: The word guessed event
        """
        self.current_game_guesses += 1

    def _handle_game_state_changed(self, event: GameStateChangedEvent) -> None:
        """Process game state changed events.

        Args:
            event: The game state changed event
        """
        new_state = event.new_state

        if new_state == GameState.GAME_OVER:
            self._process_game_over(event.metadata)
        elif new_state == GameState.STARTED:
            self._reset_current_game()

    def _process_game_over(self, metadata: Dict[str, Any]) -> None:
        """Handle game over state.

        Args:
            metadata: Game metadata including win status
        """
        self.games_played += 1
        game_won = metadata.get("won", False)

        if game_won:
            self._process_game_win()
        else:
            # Reset streak on loss
            self.current_streak = 0

        # Reset current game counter regardless of win/loss
        self._reset_current_game()

    def _process_game_win(self) -> None:
        """Handle game win logic."""
        self.games_won += 1
        self.current_streak += 1

        # Update max streak if current streak is higher
        if self.current_streak > self.max_streak:
            self.max_streak = self.current_streak

        # Update guess distribution
        guesses = self.current_game_guesses
        if 1 <= guesses <= 6:
            self.guess_distribution[guesses] += 1

    def _reset_current_game(self) -> None:
        """Reset current game counters."""
        self.current_game_guesses = 0


class LoggingObserver(GameStateObserver):
    """Observer that logs all game events."""

    def __init__(self, log_level=logging.INFO):
        """Initialize with specified log level.

        Args:
            log_level: The logging level to use
        """
        self.log_level = log_level

    def notify(self, event: GameEvent) -> None:
        """Log the event that occurred.

        Args:
            event: The game event
        """
        if isinstance(event, LetterGuessedEvent):
            self._log_letter_guessed(event)
        elif isinstance(event, WordGuessedEvent):
            self._log_word_guessed(event)
        else:
            self._log_generic_event(event)

    def _log_letter_guessed(self, event: LetterGuessedEvent) -> None:
        """Log letter guessed event.

        Args:
            event: The letter guessed event
        """
        logger.log(
            self.log_level,
            f"Letter guessed: '{event.letter}', result: '{event.result}'",
        )

    def _log_word_guessed(self, event: WordGuessedEvent) -> None:
        """Log word guessed event.

        Args:
            event: The word guessed event
        """
        results_str = ", ".join(
            [
                f"'{letter}': {result}"
                for letter, result in zip(event.word, event.results)
            ]
        )
        logger.log(
            self.log_level, f"Word guessed: '{event.word}', results: [{results_str}]"
        )

    def _log_generic_event(self, event: GameEvent) -> None:
        """Log any other game event.

        Args:
            event: The game event
        """
        event_data = event.get_event_data()
        event_type = event_data.get("event_type", "unknown")
        logger.log(self.log_level, f"Game event: {event_type}, data: {event_data}")
