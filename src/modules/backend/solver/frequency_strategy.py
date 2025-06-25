# src/modules/backend/solver/frequency_strategy.py
"""
Frequency-based solver strategy for Wordle.
"""
from typing import Dict, List, Tuple

from ...logging_utils import log_method
from .solver_strategy import SolverStrategy
from .solver_utils import calculate_letter_frequencies


class FrequencyStrategy(SolverStrategy):
    """Strategy that uses letter frequency analysis to suggest words."""

    @log_method("DEBUG")
    def get_top_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: List[Tuple[str, str]],
        count: int = 10,
    ) -> List[str]:
        """Get top N suggestions in order of likelihood, common words first."""
        if not possible_words:
            return []

        if len(possible_words) <= count:
            # If we have few words left, prioritize common ones first
            other_possible = [w for w in possible_words if w not in common_words]
            return common_words + other_possible

        # Calculate letter frequency scores
        letter_freq = calculate_letter_frequencies(possible_words)
        # Convert from normalized frequencies to counts for scoring
        total_words = len(possible_words)
        letter_count = {letter: freq * total_words for letter, freq in letter_freq.items()}

        # Separate common and uncommon words
        other_possible = [w for w in possible_words if w not in common_words]

        # Score both groups separately
        common_scored = self._score_words(common_words, letter_count, guesses_so_far)
        other_scored = self._score_words(other_possible, letter_count, guesses_so_far)

        # Sort by score (highest first)
        common_sorted = [
            word for word, score in sorted(common_scored.items(), key=lambda x: x[1], reverse=True)
        ]
        other_sorted = [
            word for word, score in sorted(other_scored.items(), key=lambda x: x[1], reverse=True)
        ]

        # Combine with common words first, then fill with other words
        suggestions = []

        # Add common words first (up to count/2 or all common words)
        common_count = min(len(common_sorted), max(count // 2, count - len(other_sorted)))
        suggestions.extend(common_sorted[:common_count])

        # Add other words to fill up to count
        suggestions.extend(other_sorted[: count - len(suggestions)])

        return suggestions[:count]

    @log_method("DEBUG")
    def _score_words(
        self, words: List[str], letter_freq: Dict[str, float], guesses_so_far: List[Tuple[str, str]]
    ) -> Dict[str, float]:
        """Score words based on letter frequency and uniqueness."""
        word_scores: Dict[str, float] = {}

        for word in words:
            # Base score: sum of letter frequencies for unique letters
            unique_letters = set(word)
            score: float = sum(letter_freq.get(letter, 0) for letter in unique_letters)

            # Penalty for repeated letters (less information gain)
            if len(unique_letters) < len(word):
                repeated_count = len(word) - len(unique_letters)
                score *= (5 - repeated_count) / 5  # Slight penalty for repeats

            # Adjust score based on previous guesses (avoid similar patterns)
            if guesses_so_far:
                overlap_penalty: float = 0.0
                for guess, _ in guesses_so_far:
                    # Count shared letters
                    shared_letters = len(set(word).intersection(set(guess)))
                    overlap_penalty += shared_letters * 0.1  # Small penalty per shared letter
                score -= overlap_penalty

            word_scores[word] = score

        return word_scores
