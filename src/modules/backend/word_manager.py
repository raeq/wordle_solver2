# src/modules/backend/word_manager.py
"""
Module for managing word lists and word filtering logic.
"""
from pathlib import Path
from typing import List, Optional, Set

from .exceptions import InputLengthError, InvalidResultError, InvalidWordError
from .result_color import ResultColor


class WordManager:
    """Manages the list of valid words and filtering based on game constraints."""

    def __init__(self, common_words_file: Optional[str] = None, all_words_file: Optional[str] = None):
        # Set default paths relative to the project root
        if common_words_file is None:
            common_words_file = str(Path(__file__).parents[3] / "src/common_words.txt")
        if all_words_file is None:
            all_words_file = str(Path(__file__).parents[3] / "src/words.txt")

        self.all_words = self._load_words(all_words_file)
        self.common_words = self._load_words(common_words_file)
        self.all_words = self.all_words.union(self.common_words)

        self.possible_words = self.all_words.copy()
        self._is_test_mode = False  # Added attribute for test mode

    def _load_words(self, filename: str) -> Set[str]:
        """Load words from file."""
        words = set()
        try:
            with open(filename, encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue

                    # Extract only alphabetical parts from each line
                    parts = line.split()
                    if not parts:
                        continue

                    try:
                        if len(parts) >= 3 and parts[0].isdigit():  # Format: [index] [frequency] [word]
                            word = parts[2].strip().upper()
                        else:
                            word = parts[0].strip().upper()

                        # Check that word is 5 letters and alphabetical
                        if len(word) == 5 and word.isalpha():
                            words.add(word)
                    except IndexError:
                        # Skip lines that don't match expected format
                        continue
        except FileNotFoundError:
            print(f"Warning: Word file not found: {filename}")

        return words

    def _word_matches_result(self, word: str, guess: str, result: str) -> bool:
        """Check if a word matches the given guess result."""
        if len(word) != 5 or len(guess) != 5 or len(result) != 5:
            return False

        # Step 1: Check green letters (exact matches)
        if not self._matches_green_positions(word, guess, result):
            return False

        # Step 2: Check yellow letters (letters in wrong positions)
        if not self._matches_yellow_positions(word, guess, result):
            return False

        # Step 3: Handle black letters (letters not in the word or already accounted for)
        if not self._matches_black_positions(word, guess, result):
            return False

        return True

    def _matches_green_positions(self, word: str, guess: str, result: str) -> bool:
        """Check if word matches the green positions from the guess."""
        for i in range(5):
            if result[i] == ResultColor.GREEN.value and word[i] != guess[i]:
                return False
        return True

    def _matches_yellow_positions(self, word: str, guess: str, result: str) -> bool:
        """Check if word matches the yellow positions from the guess."""
        for i in range(5):
            if result[i] == ResultColor.YELLOW.value:
                # The letter must be in the word but NOT in this position
                if word[i] == guess[i]:
                    return False
                # The letter must appear somewhere in the word
                if guess[i] not in word:
                    return False
        return True

    def _matches_black_positions(self, word: str, guess: str, result: str) -> bool:
        """Check if word correctly handles black letters from the guess."""
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
        return sorted([word for word in self.possible_words if word in self.common_words])

    def is_valid_word(self, word: str) -> bool:
        """Check if a word is in the word list."""
        return word.upper() in self.all_words

    def reset(self) -> None:
        """Reset the list of possible words."""
        self.possible_words = self.all_words.copy()

    def get_word_count(self) -> int:
        """Return the number of possible words."""
        return len(self.possible_words)

    def filter_words(self, guess: str, result: str) -> None:
        """Filter possible words based on the guess and result."""
        guess = guess.upper()
        result = result.upper()

        # Validate input lengths unless in test mode
        if not self._is_test_mode:
            if len(guess) != 5:
                raise InputLengthError("Guess must be 5 letters", len(guess), 5)
            if len(result) != 5:
                raise InputLengthError("Result must be 5 characters", len(result), 5)
            if not self.is_valid_word(guess):
                raise InvalidWordError(f"{guess} is not a valid word")
            for char in result:
                if char not in [c.value for c in ResultColor]:
                    raise InvalidResultError(
                        f"Invalid result character: {char}", "Must use valid result colors"
                    )

        # Filter words based on the guess result
        self.possible_words = {
            word for word in self.possible_words if self._word_matches_result(word, guess, result)
        }
