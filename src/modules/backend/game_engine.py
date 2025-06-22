# src/modules/backend/game_engine.py
"""
Game engine module for handling the game logic when the computer selects a target word.
"""
import random
from typing import Dict, List, Tuple

from .exceptions import (
    GameStateError,
    InputLengthError,
    InvalidGuessError,
    InvalidWordError,
)
from .result_color import ResultColor
from .word_manager import WordManager


class GameEngine:
    """Handles the computer vs player game mode."""

    def __init__(self, word_manager: WordManager):
        self.word_manager = word_manager
        self.target_word = ""
        self.guesses: List[Tuple[str, str]] = []
        self.max_guesses = 6
        self.game_active = False

    def start_new_game(self) -> str:
        """Start a new game by selecting a random target word."""
        # Prefer common words for the target, but fall back to all words if needed
        common_words = list(self.word_manager.common_words)
        all_words = list(self.word_manager.all_words)

        if common_words:
            # 70% chance to pick from common words, 30% from all words
            if random.random() < 0.7:
                self.target_word = random.choice(common_words)
            else:
                self.target_word = random.choice(all_words)
        else:
            self.target_word = random.choice(all_words) if all_words else "AUDIO"

        self.guesses = []
        self.game_active = True
        return self.target_word

    def make_guess(self, guess: str) -> Tuple[str, bool]:
        """
        Make a guess and return the result pattern and whether the game is won.
        Returns: (result_pattern, is_solved)
        """
        if not self.game_active:
            raise GameStateError("No active game. Call start_new_game() first.")

        guess = guess.upper()
        if len(guess) != 5:
            raise InputLengthError("Guess", len(guess))

        if not guess.isalpha():
            raise InvalidGuessError(guess, "must contain only letters")

        if not self.word_manager.is_valid_word(guess):
            raise InvalidWordError(guess)

        result = self._calculate_result(guess, self.target_word)
        self.guesses.append((guess, result))

        is_solved = result == ResultColor.GREEN.value * 5

        if is_solved or len(self.guesses) >= self.max_guesses:
            self.game_active = False

        return result, is_solved

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
            if result[i] != ResultColor.GREEN.value and g_char in target_chars and target_chars[g_char] > 0:
                result[i] = ResultColor.YELLOW.value
                target_chars[g_char] -= 1

        return "".join(result)

    def get_remaining_guesses(self) -> int:
        """Get number of remaining guesses."""
        return self.max_guesses - len(self.guesses)

    def is_game_won(self) -> bool:
        """Check if the game has been won."""
        return bool(self.guesses and self.guesses[-1][1] == ResultColor.GREEN.value * 5)

    def is_game_over(self) -> bool:
        """Check if the game is over (won or max guesses reached)."""
        return self.is_game_won() or len(self.guesses) >= self.max_guesses or not self.game_active

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
        }

    def get_hint(self) -> str:
        """Get a hint for the current game."""
        if not self.game_active:
            return "No active game."

        # Choose a random position that hasn't been guessed correctly
        incorrect_positions = []

        if not self.guesses:
            # For first guess, hint at a random letter from the target
            pos = random.randint(0, 4)
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
        pos = random.choice(incorrect_positions)

        return f"The letter in position {pos+1} is '{self.target_word[pos]}'."
