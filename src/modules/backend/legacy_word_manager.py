# src/modules/backend/legacy_word_manager.py
"""
Module for managing word lists and word filtering logic.
"""
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..logging_utils import log_method
from .exceptions import InputLengthError, InvalidResultError, InvalidWordError
from .result_color import ResultColor


class WordManager:
    """Manages the list of valid words and filtering based on game constraints."""

    def __init__(self, words_file: Optional[str] = None):
        # Set default path to words.txt relative to the project root
        if words_file is None:
            words_file = str(Path(__file__).parents[3] / "src/data/words.txt")

        # Load words with frequency and entropy data
        self.word_data = self._load_word_data(words_file)
        self.all_words = set(self.word_data.keys())

        # Create common_words as high-frequency words for backward compatibility
        # Use top 30% of words by frequency as "common" words
        sorted_by_freq = sorted(
            self.word_data.items(), key=lambda x: x[1][0], reverse=True
        )
        common_count = max(1, len(sorted_by_freq) * 30 // 100)
        self.common_words = {word for word, _ in sorted_by_freq[:common_count]}

        self.possible_words = self.all_words.copy()
        self._is_test_mode = False  # Added attribute for test mode

    @log_method("DEBUG")
    def _load_word_data(self, filename: str) -> Dict[str, Tuple[int, float]]:
        """Load words with frequency and entropy data from file.

        Returns:
            Dict mapping word -> (frequency, entropy)
        """
        word_data = {}
        try:
            with open(filename, encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue

                    # Parse space-delimited format: word frequency entropy
                    parts = line.split()
                    if len(parts) < 3:
                        continue

                    try:
                        word = parts[0].strip().upper()
                        frequency = int(parts[1])
                        entropy = float(parts[2])

                        # Check that word is 5 letters and alphabetical
                        if len(word) == 5 and word.isalpha():
                            word_data[word] = (frequency, entropy)

                    except (ValueError, IndexError):
                        # Skip lines that don't match expected format
                        continue
        except FileNotFoundError:
            print(f"Warning: Word file not found: {filename}")

        return word_data

    @log_method("DEBUG")
    def _load_words(self, _filename: str) -> Set[str]:
        """Legacy method for backward compatibility.

        Args:
            _filename: Filename parameter (unused but kept for backward compatibility)
        """
        return set(self.word_data.keys()) if hasattr(self, "word_data") else set()

    @log_method("DEBUG")
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

    @log_method("DEBUG")
    def _matches_green_positions(self, word: str, guess: str, result: str) -> bool:
        """Check if word matches the green positions from the guess."""
        for i in range(5):
            if result[i] == ResultColor.GREEN.value and word[i] != guess[i]:
                return False
        return True

    @log_method("DEBUG")
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

    @log_method("DEBUG")
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

    @log_method("DEBUG")
    def get_possible_words(self) -> List[str]:
        """Get current list of possible words."""
        return sorted(self.possible_words)

    @log_method("DEBUG")
    def get_common_possible_words(self) -> List[str]:
        """Get list of common words that are still possible."""
        return sorted(
            [word for word in self.possible_words if word in self.common_words]
        )

    @log_method("DEBUG")
    def get_possible_words_stateless(
        self, constraints: List[Tuple[str, str]] = None
    ) -> List[str]:
        """Get possible words using stateless filtering from constraints.

        Args:
            constraints: List of (guess, result) tuples to apply. If None, returns all words.

        Returns:
            List of words that satisfy all constraints
        """
        if constraints is None or len(constraints) == 0:
            return sorted(self.all_words)

        return self.apply_multiple_constraints(constraints)

    @log_method("DEBUG")
    def get_common_possible_words_stateless(
        self, constraints: List[Tuple[str, str]] = None
    ) -> List[str]:
        """Get common words using stateless filtering from constraints.

        Args:
            constraints: List of (guess, result) tuples to apply. If None, returns all common words.

        Returns:
            List of common words that satisfy all constraints
        """
        if constraints is None or len(constraints) == 0:
            return sorted(self.common_words)

        possible_words = set(self.apply_multiple_constraints(constraints))
        return sorted([word for word in possible_words if word in self.common_words])

    @log_method("DEBUG")
    def is_valid_word(self, word: str) -> bool:
        """Check if a word is in the word list."""
        return word.upper() in self.all_words

    @log_method("DEBUG")
    def reset(self) -> None:
        """Reset the list of possible words."""
        self.possible_words = self.all_words.copy()

    @log_method("DEBUG")
    def get_word_count(self) -> int:
        """Return the number of possible words."""
        return len(self.possible_words)

    @log_method("DEBUG")
    def filter_words(self, guess: str, result: str) -> None:
        """Filter possible words based on the guess and result.

        Note: This method maintains state for backward compatibility.
        For stateless filtering, use apply_single_constraint or apply_multiple_constraints.
        """
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
                        f"Invalid result character: {char}",
                        "Must use valid result colors",
                    )

        # Use stateless filtering internally, then update state
        filtered_words = self.apply_single_constraint(
            guess, result, self.possible_words
        )
        self.possible_words = set(filtered_words)

    @log_method("DEBUG")
    def get_word_frequency(self, word: str) -> int:
        """Get the frequency count for a word."""
        word = word.upper()
        if word in self.word_data:
            return self.word_data[word][0]
        return 0

    @log_method("DEBUG")
    def get_word_entropy(self, word: str) -> float:
        """Get the entropy value for a word."""
        word = word.upper()
        if word in self.word_data:
            return self.word_data[word][1]
        return 0.0

    @log_method("DEBUG")
    def get_words_by_frequency_range(
        self,
        min_freq: int = 0,
        max_freq: float = float("inf"),
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """Get words within a frequency range, sorted by frequency descending.

        Args:
            min_freq: Minimum frequency threshold
            max_freq: Maximum frequency threshold
            word_set: Optional set of words to filter. If None, uses possible_words for compatibility.

        Returns:
            List of words within frequency range, sorted by frequency descending
        """
        if word_set is None:
            word_set = self.possible_words

        filtered_words = [
            word
            for word, (freq, _) in self.word_data.items()
            if min_freq <= freq <= max_freq and word in word_set
        ]
        return sorted(filtered_words, key=lambda w: self.word_data[w][0], reverse=True)

    @log_method("DEBUG")
    def get_words_by_entropy_range(
        self,
        min_entropy: float = 0.0,
        max_entropy: float = float("inf"),
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """Get words within an entropy range, sorted by entropy descending.

        Args:
            min_entropy: Minimum entropy threshold
            max_entropy: Maximum entropy threshold
            word_set: Optional set of words to filter. If None, uses possible_words for compatibility.

        Returns:
            List of words within entropy range, sorted by entropy descending
        """
        if word_set is None:
            word_set = self.possible_words

        filtered_words = [
            word
            for word, (_, entropy) in self.word_data.items()
            if min_entropy <= entropy <= max_entropy and word in word_set
        ]
        return sorted(filtered_words, key=lambda w: self.word_data[w][1], reverse=True)

    @log_method("DEBUG")
    def is_test_mode(self) -> bool:
        """Check if the word manager is in test mode (public method)."""
        return self._is_test_mode

    @log_method("DEBUG")
    def set_test_mode(self, test_mode: bool) -> None:
        """Set test mode for the word manager (public method)."""
        self._is_test_mode = test_mode

    @log_method("DEBUG")
    def apply_single_constraint(
        self, guess: str, result: str, word_set: Optional[Set[str]] = None
    ) -> List[str]:
        """Apply a single guess-result constraint to filter words statlessly.

        Args:
            guess: The guessed word
            result: The result pattern (G/Y/B for Green/Yellow/Black)
            word_set: Optional set of words to filter. If None, uses all words.

        Returns:
            List of words that match the constraint
        """
        if word_set is None:
            word_set = self.all_words.copy()

        guess = guess.upper()
        result = result.upper()

        # Validate inputs unless in test mode
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
                        f"Invalid result character: {char}",
                        "Must use valid result colors",
                    )

        # Filter words based on the guess result
        filtered_words = {
            word for word in word_set if self._word_matches_result(word, guess, result)
        }

        return sorted(filtered_words)

    @log_method("DEBUG")
    def apply_multiple_constraints(
        self, constraints: List[Tuple[str, str]], word_set: Optional[Set[str]] = None
    ) -> List[str]:
        """Apply multiple guess-result constraints sequentially.

        Args:
            constraints: List of (guess, result) tuples
            word_set: Optional set of words to filter. If None, uses all words.

        Returns:
            List of words that match all constraints
        """
        if word_set is None:
            current_words = self.all_words.copy()
        else:
            current_words = word_set.copy()

        for guess, result in constraints:
            current_words = set(
                self.apply_single_constraint(guess, result, current_words)
            )

        return sorted(current_words)

    @log_method("DEBUG")
    def get_words_matching_pattern(
        self, pattern: Dict[int, str], word_set: Optional[Set[str]] = None
    ) -> List[str]:
        """Get words that match a specific positional pattern.

        Args:
            pattern: Dictionary mapping positions (0-4) to required letters
            word_set: Optional set of words to filter. If None, uses all words.

        Returns:
            List of words matching the pattern
        """
        if word_set is None:
            word_set = self.all_words.copy()

        filtered_words = set()

        for word in word_set:
            matches = True
            for position, letter in pattern.items():
                if position < 0 or position > 4:
                    raise ValueError(f"Invalid position: {position}. Must be 0-4.")
                if word[position] != letter.upper():
                    matches = False
                    break
            if matches:
                filtered_words.add(word)

        return sorted(filtered_words)

    @log_method("DEBUG")
    def get_words_containing_letters(
        self, letters: List[str], word_set: Optional[Set[str]] = None
    ) -> List[str]:
        """Get words that contain all specified letters anywhere.

        Args:
            letters: List of letters that must be present in the word
            word_set: Optional set of words to filter. If None, uses all words.

        Returns:
            List of words containing all specified letters
        """
        if word_set is None:
            word_set = self.all_words.copy()

        letters_upper = [letter.upper() for letter in letters]

        filtered_words = {
            word for word in word_set if all(letter in word for letter in letters_upper)
        }

        return sorted(filtered_words)

    @log_method("DEBUG")
    def get_words_excluding_letters(
        self, letters: List[str], word_set: Optional[Set[str]] = None
    ) -> List[str]:
        """Get words that exclude all specified letters.

        Args:
            letters: List of letters that must not be present in the word
            word_set: Optional set of words to filter. If None, uses all words.

        Returns:
            List of words not containing any of the specified letters
        """
        if word_set is None:
            word_set = self.all_words.copy()

        letters_upper = [letter.upper() for letter in letters]

        filtered_words = {
            word
            for word in word_set
            if not any(letter in word for letter in letters_upper)
        }

        return sorted(filtered_words)

    @log_method("DEBUG")
    def get_words_with_yellow_constraints(
        self,
        yellow_constraints: Dict[int, List[str]],
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """Get words that satisfy yellow letter constraints.

        Args:
            yellow_constraints: Dictionary mapping positions to lists of letters
                               that must be in the word but not at those positions
            word_set: Optional set of words to filter. If None, uses all words.

        Returns:
            List of words satisfying yellow constraints
        """
        if word_set is None:
            word_set = self.all_words.copy()

        filtered_words = set()

        for word in word_set:
            matches = True
            for position, letters in yellow_constraints.items():
                if position < 0 or position > 4:
                    raise ValueError(f"Invalid position: {position}. Must be 0-4.")

                for letter in letters:
                    letter_upper = letter.upper()
                    # Letter must be in word but not at this position
                    if letter_upper not in word or word[position] == letter_upper:
                        matches = False
                        break

                if not matches:
                    break

            if matches:
                filtered_words.add(word)

        return sorted(filtered_words)
