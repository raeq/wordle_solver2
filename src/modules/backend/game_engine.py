# src/modules/backend/game_engine.py
"""
Game engine module for handling the game logic when the computer selects a target word.
"""
import secrets  # More secure random number generation
import string
from typing import Dict, List, Tuple

from ..logging_utils import log_method, logger, set_game_id
from .exceptions import (
    GameStateError,
    InputLengthError,
    InvalidGuessError,
    InvalidWordError,
)
from .result_color import ResultColor
from .solver.constants import DEFAULT_GAME_ID_LENGTH, DEFAULT_MAX_ATTEMPTS


class GameEngine:
    """Handles the computer vs player game mode."""

    @log_method("DEBUG")
    def __init__(self):
        """
        Initialize a new GameEngine instance.

        The GameEngine maintains strict encapsulation by creating and controlling
        its own WordManager and StatsManager instances.
        """
        from .stateless_word_manager import (
            StatelessWordManager,  # Import for internal use
        )
        from .stats_manager import StatsManager  # Import here to avoid circular imports

        self.word_manager = (
            StatelessWordManager()
        )  # GameEngine creates and controls its own WordManager
        self.stats_manager = (
            StatsManager()
        )  # GameEngine creates and controls its own StatsManager
        self.target_word = ""
        self.guesses: List[Tuple[str, str]] = []
        self.max_guesses = DEFAULT_MAX_ATTEMPTS
        self.game_active = False
        self._game_id = ""
        self.game_mode = "auto"  # Default game mode

    @property
    def game_id(self) -> str:
        """Get the current game ID or raise an exception if there is no active game."""
        if not self._game_id:
            raise GameStateError("No active game. Call start_new_game() first.")
        return self._game_id

    @game_id.setter
    def game_id(self, value: str) -> None:
        """
        Set the game ID. If None or empty string is provided,
        a new random 6-character alphanumeric ID will be generated automatically.
        """
        if value is None or value.strip() == "":
            # Generate a new game ID
            characters = string.ascii_uppercase + string.digits
            self._game_id = "".join(
                secrets.choice(characters) for _ in range(DEFAULT_GAME_ID_LENGTH)
            )
        else:
            self._game_id = value

        if logger is not None:
            logger.info(f"New game ID: {self._game_id}")

    @log_method("DEBUG")
    def start_new_game(self) -> str:
        """Start a new game by selecting a random target word."""
        # Prefer common words for the target, but fall back to all words if needed
        common_words = list(self.word_manager.common_words)
        all_words = list(self.word_manager.all_words)

        if common_words:
            # 70% chance to pick from common words, 30% from all words
            if secrets.randbelow(10) < 7:  # 7 out of 10 = 70%
                self.target_word = secrets.choice(common_words)
            else:
                self.target_word = secrets.choice(all_words)
        else:
            self.target_word = secrets.choice(all_words) if all_words else "AUDIO"

        self.guesses = []
        self.game_active = True
        self.game_id = ""  # This will trigger the setter to generate a new ID

        # Set the game ID in the logging context
        set_game_id(self._game_id)

        return self.target_word

    @log_method("DEBUG")
    def make_guess(self, guess: str, mode: str = None) -> Tuple[str, bool]:
        """
        Make a guess and return the result pattern and whether the game is won.

        Args:
            guess: The word being guessed
            mode: Optional game mode identifier (manual, solver, etc.)

        Returns:
            (result_pattern, is_solved)
        """
        if not self.game_active:
            raise GameStateError("No active game. Call start_new_game() first.")

        # Update game mode if provided
        if mode:
            self.game_mode = mode

        guess = guess.upper()
        if len(guess) != 5:
            raise InputLengthError("Guess", len(guess))

        if not guess.isalpha():
            raise InvalidGuessError(guess, "must contain only letters")

        # Check if word is valid, bypassing validation if word_manager is in test mode
        if not self.word_manager.is_test_mode() and not self.word_manager.is_valid_word(
            guess
        ):
            raise InvalidWordError(guess)

        result = self._calculate_result(guess, self.target_word)
        self.guesses.append((guess, result))

        is_solved = result == ResultColor.GREEN.value * 5
        game_over = is_solved or len(self.guesses) >= self.max_guesses

        if game_over:
            self.game_active = False
            # Automatically save the game when it ends
            self._save_game(is_solved)

        return result, is_solved

    @log_method("DEBUG")
    def _save_game(self, is_solved: bool) -> None:
        """
        Save the completed game to history.

        Args:
            is_solved: Whether the game was won
        """
        if self.stats_manager:
            try:
                self.stats_manager._record_game(
                    self.guesses,
                    is_solved,
                    len(self.guesses),
                    game_id=self._game_id,
                    target_word=self.target_word,
                    mode=self.game_mode,
                )
            except Exception as e:
                # Log the error but don't prevent game from ending
                if logger:
                    logger.error(f"Failed to save game: {e}")

    @log_method("DEBUG")
    def _calculate_result(self, guess: str, target: str) -> str:
        """Calculate the result pattern for a guess against the target word."""
        result = [ResultColor.BLACK.value] * 5
        guess = guess.upper()
        target = target.upper()

        # Create a dictionary to track remaining target letters
        target_chars = {}
        for char in target:
            if char not in target_chars:
                target_chars[char] = 0
            target_chars[char] += 1

        # First pass: Mark all correct positions (greens)
        for i, (g_char, t_char) in enumerate(zip(guess, target)):
            if g_char == t_char:
                result[i] = ResultColor.GREEN.value
                target_chars[g_char] -= 1

        # Second pass: Mark misplaced letters (yellows)
        for i, g_char in enumerate(guess):
            if (
                result[i] != ResultColor.GREEN.value
                and g_char in target_chars
                and target_chars[g_char] > 0
            ):
                result[i] = ResultColor.YELLOW.value
                target_chars[g_char] -= 1

        return "".join(result)

    @log_method("DEBUG")
    def get_remaining_guesses(self) -> int:
        """Get number of remaining guesses."""
        return self.max_guesses - len(self.guesses)

    @log_method("DEBUG")
    def is_game_won(self) -> bool:
        """Check if the game has been won."""
        return bool(self.guesses and self.guesses[-1][1] == ResultColor.GREEN.value * 5)

    @log_method("DEBUG")
    def is_game_over(self) -> bool:
        """Check if the game is over (won or max guesses reached)."""
        return (
            self.is_game_won()
            or len(self.guesses) >= self.max_guesses
            or not self.game_active
        )

    @log_method("DEBUG")
    def get_game_state(self) -> Dict[str, object]:
        """Get current game state."""
        is_won = self.is_game_won()
        is_over = self.is_game_over()

        return {
            "active": self.game_active,
            "guesses_made": len(self.guesses),
            "guesses_remaining": self.get_remaining_guesses(),
            "is_won": is_won,
            "is_over": is_over,
            "guesses_history": self.guesses.copy(),
            "target_word": self.target_word if is_over else None,
            "game_id": self.game_id,
        }

    @log_method("DEBUG")
    def get_hint(self) -> str:
        """Get a hint for the current game."""
        if not self.game_active:
            return "No active game."

        # Choose a random position that hasn't been guessed correctly
        incorrect_positions = []

        if not self.guesses:
            # For first guess, hint at a random letter from the target
            pos = secrets.randbelow(5)  # Generate number between 0 and 4 inclusive
            return (
                f"The word contains the letter '{self.target_word[pos]}'. "
                f"Try starting with a word like 'ADIEU' or 'AUDIO' that contains many vowels."
            )

        # Find positions that haven't been guessed correctly
        last_guess = self.guesses[-1]
        for i, result_char in enumerate(last_guess[1]):
            if result_char != "G":
                incorrect_positions.append(i)

        if not incorrect_positions:
            return "You've already guessed all letters correctly!"

        # Choose a random incorrect position
        # Need to implement secrets.choice as it's not directly available
        pos = incorrect_positions[secrets.randbelow(len(incorrect_positions))]

        return f"The letter in position {pos+1} is '{self.target_word[pos]}'."
