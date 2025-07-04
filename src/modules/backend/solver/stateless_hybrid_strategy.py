# src/modules/backend/solver/stateless_hybrid_strategy.py
"""
Stateless hybrid frequency-entropy strategy combining corpus frequency with information theory.
"""
import math
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

from .stateless_solver_strategy import StatelessSolverStrategy

if TYPE_CHECKING:
    from ..legacy_word_manager import WordManager
    from ..stateless_word_manager import StatelessWordManager


class StatelessHybridStrategy(StatelessSolverStrategy):
    """
    Stateless strategy that combines frequency-based scoring with entropy for optimal word suggestions.
    """

    def __init__(self, frequency_weight: float = 0.4, entropy_weight: float = 0.6):
        """
        Initialize the hybrid strategy with customizable weights.

        Args:
            frequency_weight: Weight for word frequency (0-1)
            entropy_weight: Weight for entropy (0-1)
        """
        # Normalize weights to ensure they sum to 1.0
        total = frequency_weight + entropy_weight
        self.frequency_weight = frequency_weight / total
        self.entropy_weight = entropy_weight / total

    def get_top_suggestions(
        self,
        constraints: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """Get top N suggestions based on hybrid frequency-entropy scoring using stateless filtering."""

        # Get filtered words using stateless methods
        possible_words, common_words = self._get_filtered_words(
            constraints, word_manager, stateless_word_manager, word_set
        )

        if not possible_words:
            return []

        if len(possible_words) <= count:
            # If we have few words left, sort by combined score
            return self._sort_by_hybrid_score(
                possible_words,
                common_words,
                word_manager,
                stateless_word_manager,
                prefer_common,
            )

        # For the first guess, use high-entropy words with reasonable frequency
        if not constraints:
            return self._get_optimal_starters(
                possible_words,
                common_words,
                count,
                word_manager,
                stateless_word_manager,
            )

        # Score words based on hybrid frequency-entropy metric
        word_scores = self._score_words_hybrid(
            possible_words, constraints, word_manager, stateless_word_manager
        )

        # Sort by score (highest combined score first)
        sorted_words = [
            word
            for word, score in sorted(
                word_scores.items(), key=lambda x: x[1], reverse=True
            )
        ]

        # Apply balanced selection if prefer_common is True
        if prefer_common:
            return self._build_balanced_result(sorted_words, common_words, count)
        else:
            return sorted_words[:count]

    def _sort_by_hybrid_score(
        self,
        words: List[str],
        common_words: List[str],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
    ) -> List[str]:
        """Sort words by hybrid score, optionally prioritizing common words."""
        # Calculate hybrid scores for all words
        word_scores = {}
        for word in words:
            frequency = self._get_word_frequency(
                word, word_manager, stateless_word_manager
            )
            entropy = self._get_word_entropy(word, word_manager, stateless_word_manager)

            # Normalize scores
            freq_score = self._normalize_frequency(frequency)
            entropy_score = self._normalize_entropy(entropy)

            # Combine scores
            hybrid_score = (
                self.frequency_weight * freq_score + self.entropy_weight * entropy_score
            )

            # Boost common words slightly if prefer_common is True
            if prefer_common and word in common_words:
                hybrid_score *= 1.1

            word_scores[word] = hybrid_score

        # Sort by hybrid score
        return sorted(words, key=lambda w: word_scores[w], reverse=True)

    def _get_optimal_starters(
        self,
        possible_words: List[str],
        common_words: List[str],
        count: int,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> List[str]:
        """Get optimal starting words based on hybrid scoring."""
        # Predefined high-value starters
        optimal_starters = ["SLATE", "CRANE", "ADIEU", "AUDIO", "RAISE", "TEARS"]

        # Filter available starters
        available_starters = [
            word for word in optimal_starters if word in possible_words
        ]

        if len(available_starters) >= count:
            return available_starters[:count]

        # Score remaining words for hybrid quality
        remaining_words = [w for w in possible_words if w not in available_starters]
        word_scores = self._score_words_hybrid(
            remaining_words[:100],
            [],
            word_manager,
            stateless_word_manager,  # Limit for performance
        )

        # Add best scoring words
        additional_words = sorted(
            word_scores.items(), key=lambda x: x[1], reverse=True
        )[: count - len(available_starters)]

        return available_starters + [word for word, _ in additional_words]

    def _score_words_hybrid(
        self,
        words: List[str],
        constraints: List[Tuple[str, str]],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> dict:
        """Score words using hybrid frequency-entropy metric."""
        word_scores = {}

        for word in words:
            frequency = self._get_word_frequency(
                word, word_manager, stateless_word_manager
            )
            entropy = self._get_word_entropy(word, word_manager, stateless_word_manager)

            # Normalize scores
            freq_score = self._normalize_frequency(frequency)
            entropy_score = self._normalize_entropy(entropy)

            # Combine scores
            hybrid_score = (
                self.frequency_weight * freq_score + self.entropy_weight * entropy_score
            )

            # Apply uniqueness bonus
            uniqueness_bonus = self._calculate_uniqueness_bonus(word, constraints)
            hybrid_score += uniqueness_bonus * 0.1

            word_scores[word] = hybrid_score

        return word_scores

    def _normalize_frequency(self, frequency: int) -> float:
        """Normalize frequency to 0-1 scale using log transformation."""
        if frequency <= 0:
            return 0.0
        # Use log10 to normalize high frequencies
        return min(1.0, math.log10(frequency + 1) / 6.0)  # Assume max log10(freq) ~ 6

    def _normalize_entropy(self, entropy: float) -> float:
        """Normalize entropy to 0-1 scale."""
        if entropy <= 0:
            return 0.0
        # Assume entropy range 0-10
        return min(1.0, entropy / 10.0)

    def _calculate_uniqueness_bonus(
        self, word: str, constraints: List[Tuple[str, str]]
    ) -> float:
        """Calculate bonus for words different from previous guesses."""
        if not constraints:
            return 0.0

        # Get letters from previous guesses
        previous_letters = set()
        for guess, _ in constraints:
            previous_letters.update(guess.upper())

        word_letters = set(word.upper())
        shared_letters = len(word_letters.intersection(previous_letters))
        total_letters = len(word_letters)

        # Return uniqueness ratio (0-1)
        return 1.0 - (shared_letters / total_letters) if total_letters > 0 else 0.0

    def _build_balanced_result(
        self, sorted_words: List[str], common_words: List[str], count: int
    ) -> List[str]:
        """Build balanced result favoring common words."""
        common_set = set(common_words)
        common_candidates = [w for w in sorted_words if w in common_set]
        other_candidates = [w for w in sorted_words if w not in common_set]

        # Aim for 70% common words in hybrid strategy
        common_target = max(1, int(count * 0.7))
        other_target = count - common_target

        # Take up to target from each group
        result = []
        result.extend(common_candidates[:common_target])
        result.extend(other_candidates[:other_target])

        # Fill remaining slots with best candidates overall
        remaining_slots = count - len(result)
        if remaining_slots > 0:
            remaining_candidates = [w for w in sorted_words if w not in result]
            result.extend(remaining_candidates[:remaining_slots])

        return result[:count]
