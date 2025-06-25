# src/modules/backend/solver/solver_utils.py
"""
Utility functions for Wordle solver strategies.

This module contains common functionality used by multiple solver strategies,
extracted to avoid code duplication and promote reusability.
"""
from collections import Counter
from typing import Dict, List, Tuple

from ...logging_utils import log_method
from ..result_color import ResultColor


@log_method("DEBUG")
def calculate_pattern(guess: str, target: str) -> str:
    """
    Calculate the result pattern for a guess against a potential target word.

    Args:
        guess: The guess word
        target: The target word to compare against

    Returns:
        A string representing the pattern (using ResultColor values)
    """
    # Initialize all positions as black (not matched)
    result = [ResultColor.BLACK.value] * 5
    guess = guess.upper()
    target = target.upper()

    # Make a copy of the target for tracking available letters
    remaining_target = list(target)

    # First pass: Mark green (correct position)
    for i in range(min(len(guess), len(target))):
        if guess[i] == target[i]:
            result[i] = ResultColor.GREEN.value
            # Mark this position as used in the target
            remaining_target[i] = "_"

    # Second pass: Mark yellow (letter exists elsewhere)
    for i in range(min(len(guess), len(target))):
        # Only check positions that weren't marked green
        if result[i] != ResultColor.GREEN.value:
            for j, t_letter in enumerate(remaining_target):
                if guess[i] == t_letter:
                    result[i] = ResultColor.YELLOW.value
                    remaining_target[j] = "_"  # Mark as used
                    break

    return "".join(result)


@log_method("DEBUG")
def filter_by_guesses(words: List[str], guesses_so_far: List[Tuple[str, str]]) -> List[str]:
    """
    Filter words based on previous guesses and their feedback patterns.

    Args:
        words: List of candidate words to filter
        guesses_so_far: List of (guess, pattern) tuples from previous guesses

    Returns:
        List of words consistent with all previous guesses
    """
    filtered_words = words.copy()

    for guess, pattern in guesses_so_far:
        # Filter the list further with each guess
        filtered_words = [word for word in filtered_words if is_word_consistent(word, guess, pattern)]

    return filtered_words


def is_word_consistent(candidate: str, guess: str, pattern: str) -> bool:
    """
    Check if a candidate word is consistent with a previous guess and its feedback pattern.

    Args:
        candidate: The word to check
        guess: A previous guess
        pattern: The feedback pattern for that guess

    Returns:
        True if the candidate is consistent with the feedback pattern
    """
    # The pattern we would get if candidate was the hidden word
    expected_pattern = calculate_pattern(guess, candidate)

    # The word is consistent if the patterns match
    return expected_pattern == pattern


@log_method("DEBUG")
def calculate_position_frequencies(words: List[str]) -> List[Dict[str, float]]:
    """
    Calculate the frequency of each letter at each position in the word list.

    Args:
        words: List of words to analyze

    Returns:
        A list of dictionaries, one for each position (normalized frequencies)
    """
    position_freqs: List[Dict[str, float]] = [{} for _ in range(5)]

    for word in words:
        for i, letter in enumerate(word[:5]):  # Ensure we only use first 5 letters
            if letter not in position_freqs[i]:
                position_freqs[i][letter] = 0.0
            position_freqs[i][letter] += 1.0

    # Normalize frequencies to 0-1 range
    for i in range(5):
        total = sum(position_freqs[i].values())
        if total > 0:
            for letter in position_freqs[i]:
                position_freqs[i][letter] /= total

    return position_freqs


@log_method("DEBUG")
def calculate_letter_frequencies(words: List[str]) -> Dict[str, float]:
    """
    Calculate the overall frequency of each letter in the word list.

    Args:
        words: List of words to analyze

    Returns:
        Dictionary mapping letters to their normalized frequencies
    """
    letter_counts: Counter[str] = Counter()

    for word in words:
        for letter in set(word):  # Use set to count each unique letter once per word
            letter_counts[letter] += 1

    # Normalize to 0-1 range
    total_words = len(words)
    if total_words > 0:
        normalized = {letter: count / total_words for letter, count in letter_counts.items()}
    else:
        normalized = {}

    return normalized
