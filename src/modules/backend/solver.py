# src/modules/backend/solver.py
"""
Module containing the core Wordle solver logic.
"""
from collections import Counter
from typing import List, Tuple, Dict
from .word_manager import WordManager
from .result_color import ResultColor


class Solver:
    """Core solver that manages game state and suggests optimal guesses."""

    def __init__(self, word_manager: WordManager):
        self.word_manager = word_manager
        self.guesses: List[Tuple[str, str]] = []  # (guess, result) pairs
        self.max_guesses = 6

    def add_guess(self, guess: str, result: str) -> None:
        """Add a guess and its result to the history and filter words."""
        guess = guess.upper()
        result = result.upper()
        self.guesses.append((guess, result))
        self.word_manager.filter_words(guess, result)

    def suggest_next_guess(self) -> str:
        """Suggest the next best guess using advanced logic."""
        suggestions = self.get_top_suggestions(1)
        return suggestions[0] if suggestions else "No valid words remaining"

    def get_top_suggestions(self, count: int = 10) -> List[str]:
        """Get top N suggestions in order of likelihood, common words first."""
        possible_words = self.word_manager.get_possible_words()

        if not possible_words:
            return []

        if len(possible_words) <= count:
            # If we have few words left, prioritize common ones first
            common_possible = self.word_manager.get_common_possible_words()
            other_possible = [w for w in possible_words if w not in common_possible]
            return common_possible + other_possible

        # Calculate letter frequency scores
        letter_freq = self._calculate_letter_frequency(possible_words)

        # Separate common and uncommon words
        common_possible = self.word_manager.get_common_possible_words()
        other_possible = [w for w in possible_words if w not in common_possible]

        # Score both groups separately
        common_scored = self._score_words(common_possible, letter_freq)
        other_scored = self._score_words(other_possible, letter_freq)

        # Sort by score (highest first)
        common_sorted = [
            word
            for word, score in sorted(
                common_scored.items(), key=lambda x: x[1], reverse=True
            )
        ]
        other_sorted = [
            word
            for word, score in sorted(
                other_scored.items(), key=lambda x: x[1], reverse=True
            )
        ]

        # Combine with common words first, then fill with other words
        suggestions = []

        # Add common words first (up to count/2 or all common words)
        common_count = min(
            len(common_sorted), max(count // 2, count - len(other_sorted))
        )
        suggestions.extend(common_sorted[:common_count])

        # Add other words to fill up to count
        suggestions.extend(other_sorted[: count - len(suggestions)])

        return suggestions[:count]

    def _calculate_letter_frequency(self, words: List[str]) -> Dict[str, int]:
        """Calculate letter frequency in the given list of words."""
        letter_count = Counter()
        position_count = [{} for _ in range(5)]  # Position-specific counts

        for word in words:
            # Skip words that aren't exactly 5 letters
            if len(word) != 5:
                continue

            # Count each unique letter in the word
            for letter in set(word):
                letter_count[letter] += 1

            # Count letters at specific positions
            for i, letter in enumerate(word):
                if i < 5:  # Ensure we don't exceed the position_count length
                    if letter not in position_count[i]:
                        position_count[i][letter] = 0
                    position_count[i][letter] += 1

        return letter_count

    def _score_words(
        self, words: List[str], letter_freq: Dict[str, int]
    ) -> Dict[str, float]:
        """Score words based on letter frequency and uniqueness."""
        word_scores = {}

        for word in words:
            # Base score: sum of letter frequencies for unique letters
            unique_letters = set(word)
            score = sum(letter_freq.get(letter, 0) for letter in unique_letters)

            # Penalty for repeated letters (less information gain)
            if len(unique_letters) < 5:
                score *= 0.8 + (
                    0.04 * len(unique_letters)
                )  # Scale penalty by uniqueness

            # Special scoring for first guesses
            if not self.guesses:
                # Prefer starting words with more vowels
                vowels = sum(1 for letter in unique_letters if letter in "AEIOU")
                score *= 1.0 + (vowels * 0.05)

                # Hard-coded preferred starters
                if word in ["ADIEU", "AUDIO", "AROSE", "RAISE", "SOARE"]:
                    score *= 1.25

            word_scores[word] = score

        return word_scores

    def get_remaining_guesses(self) -> int:
        """Get number of remaining guesses."""
        return self.max_guesses - len(self.guesses)

    def is_game_won(self) -> bool:
        """Check if the game has been won."""
        return self.guesses and self.guesses[-1][1] == ResultColor.GREEN.value * 5

    def is_game_over(self) -> bool:
        """Check if the game is over (won or max guesses reached)."""
        return self.is_game_won() or len(self.guesses) >= self.max_guesses

    def reset(self) -> None:
        """Reset the solver for a new game."""
        self.guesses = []
        self.word_manager.reset()

    def get_game_state(self) -> Dict:
        """Get current game state."""
        return {
            "guesses_made": len(self.guesses),
            "guesses_remaining": self.get_remaining_guesses(),
            "possible_words_count": len(self.word_manager.get_possible_words()),
            "is_game_won": self.is_game_won(),
            "is_game_over": self.is_game_over(),
            "guesses_history": self.guesses.copy(),
        }
