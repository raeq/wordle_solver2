# src/modules/backend/word_manager.py
"""
Module for managing word lists and word filtering logic.
"""
from typing import List, Set
from pathlib import Path

from .result_color import ResultColor
from .exceptions import InputLengthError, InvalidResultError, InvalidWordError


class WordManager:
    """Manages the list of valid words and filtering based on game constraints."""

    def __init__(self, common_words_file: str = None, all_words_file: str = None):
        # Set default paths relative to the project root
        if common_words_file is None:
            common_words_file = str(Path(__file__).parents[3] / "src/common_words.txt")
        if all_words_file is None:
            all_words_file = str(Path(__file__).parents[3] / "src/words.txt")

        self.common_words = self._load_words(common_words_file)
        self.all_words = self._load_words(all_words_file)
        self.possible_words = self.all_words.copy()
        self._is_test_mode = False  # Added attribute for test mode

    def _load_words(self, filename: str) -> Set[str]:
        """Load words from file."""
        try:
            with open(filename, "r") as f:
                return {word.strip().upper() for word in f if len(word.strip()) == 5}
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Using empty word list.")
            return set()

    def filter_words(self, guess: str, result: str) -> None:
        """Filter possible words based on guess result."""
        guess = guess.upper()
        result = result.upper()

        # Validate the input
        if len(guess) != 5 or len(result) != 5:
            if len(guess) != 5:
                raise InputLengthError("Guess", len(guess))
            else:
                raise InputLengthError("Result", len(result))

        # Validate that the result contains only valid characters
        if not ResultColor.is_valid_result_string(result):
            raise InvalidResultError(result, "must contain only G, Y, or B characters")

        # In real mode, validate that the guess is a valid word
        # But allow invalid words for testing purposes
        if not self._is_test_mode and not self.is_valid_word(guess):
            raise InvalidWordError(guess)

        new_possible = set()

        for word in self.possible_words:
            if self._word_matches_result(word, guess, result):
                new_possible.add(word)

        self.possible_words = new_possible

    def _word_matches_result(self, word: str, guess: str, result: str) -> bool:
        """Check if a word matches the given guess result."""
        if len(word) != 5 or len(guess) != 5 or len(result) != 5:
            return False

        # First pass: Check green letters (exact matches)
        for i in range(5):
            if result[i] == ResultColor.GREEN.value:
                if word[i] != guess[i]:
                    return False

        # Special handling for yellow letters
        for i in range(5):
            if result[i] == ResultColor.YELLOW.value:
                # The letter must be in the word but NOT in this position
                if word[i] == guess[i]:
                    # Letter can't be at the same position as a yellow marker
                    return False

                # The letter must appear somewhere in the word
                if guess[i] not in word:
                    return False

        # Handle black letters
        for i in range(5):
            if result[i] == ResultColor.BLACK.value:
                # Count occurrences of this letter that are marked yellow/green
                marked_occurrences = sum(
                    1
                    for j in range(5)
                    if guess[j] == guess[i]
                    and result[j] in [ResultColor.YELLOW.value, ResultColor.GREEN.value]
                )

                # Count occurrences in the word
                word_occurrences = word.count(guess[i])

                # Black means the letter should not appear more times than accounted for
                if word_occurrences > marked_occurrences:
                    return False

        return True

    def get_possible_words(self) -> List[str]:
        """Get current list of possible words."""
        return sorted(list(self.possible_words))

    def get_common_possible_words(self) -> List[str]:
        """Get list of common words that are still possible."""
        return sorted(
            [word for word in self.possible_words if word in self.common_words]
        )

    def is_valid_word(self, word: str) -> bool:
        """Check if a word is in the word list."""
        return word.upper() in self.all_words

    def reset(self) -> None:
        """Reset the list of possible words."""
        self.possible_words = self.all_words.copy()

    def get_word_count(self) -> int:
        """Return the number of possible words."""
        return len(self.possible_words)
