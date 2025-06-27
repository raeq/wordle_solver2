# src/modules/backend/solver/hybrid_frequency_entropy_strategy.py
"""
Hybrid frequency-entropy strategy combining corpus frequency with information theory.
"""
import math
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from .solver_strategy import SolverStrategy

if TYPE_CHECKING:
    from ..word_manager import WordManager


class HybridFrequencyEntropyStrategy(SolverStrategy):
    """
    Strategy that combines frequency-based scoring with entropy for optimal word suggestions.
    Uses actual corpus frequency data when available, falls back to calculated frequency.
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
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
    ) -> List[str]:
        """Get top N suggestions based on hybrid frequency-entropy scoring."""
        if not possible_words:
            return []

        if len(possible_words) <= count:
            # If we have few words left, sort by combined score
            return self._sort_by_hybrid_score(
                possible_words, common_words, word_manager
            )

        # For the first guess, use high-entropy words with reasonable frequency
        if not guesses_so_far:
            return self._get_optimal_starters(
                possible_words, common_words, count, word_manager
            )

        # Score words based on hybrid frequency-entropy metric
        word_scores = self._score_words_hybrid(
            possible_words, guesses_so_far, word_manager
        )

        # Sort by score (highest combined score first)
        sorted_words = [
            word
            for word, score in sorted(
                word_scores.items(), key=lambda x: x[1], reverse=True
            )
        ]

        # Apply balanced selection favoring common words
        return self._build_balanced_result(sorted_words, common_words, count)

    def _sort_by_hybrid_score(
        self, words: List[str], common_words: List[str], word_manager
    ) -> List[str]:
        """Sort words by hybrid score, prioritizing common words."""
        if word_manager is None:
            # Fallback to simple sorting
            common_possible = [w for w in words if w in common_words]
            other_possible = [w for w in words if w not in common_words]
            return sorted(common_possible) + sorted(other_possible)

        # Calculate hybrid scores for all words
        word_scores = {}
        for word in words:
            frequency = word_manager.get_word_frequency(word)
            entropy = word_manager.get_word_entropy(word)

            # Normalize scores
            freq_score = self._normalize_frequency(frequency)
            entropy_score = self._normalize_entropy(entropy)

            # Combine scores
            hybrid_score = (
                self.frequency_weight * freq_score + self.entropy_weight * entropy_score
            )

            # Boost common words slightly
            if word in common_words:
                hybrid_score *= 1.1

            word_scores[word] = hybrid_score

        # Sort by hybrid score
        return sorted(word_scores.keys(), key=lambda w: word_scores[w], reverse=True)

    def _score_words_hybrid(
        self, words: List[str], guesses_so_far: List[Tuple[str, str]], word_manager
    ) -> Dict[str, float]:
        """Score words using hybrid frequency-entropy metric."""
        word_scores = {}

        for word in words:
            if word_manager is not None:
                # Get frequency and entropy data
                frequency = word_manager.get_word_frequency(word)
                entropy = word_manager.get_word_entropy(word)

                # Normalize scores to 0-1 range
                freq_score = self._normalize_frequency(frequency)
                entropy_score = self._normalize_entropy(entropy)

                # Combine with weights
                base_score = (
                    self.frequency_weight * freq_score
                    + self.entropy_weight * entropy_score
                )
            else:
                # Fallback scoring
                base_score = self._calculate_fallback_score(word)

            # Apply penalty for letter overlap with previous guesses
            if guesses_so_far:
                overlap_penalty = 0.0
                for guess, _ in guesses_so_far:
                    shared_letters = len(set(word).intersection(set(guess)))
                    overlap_penalty += shared_letters * 0.05  # Small penalty
                base_score = max(0.0, base_score - overlap_penalty)

            word_scores[word] = base_score

        return word_scores

    def _normalize_frequency(self, frequency: int) -> float:
        """Normalize frequency to 0-1 range using log scale."""
        if frequency <= 0:
            return 0.0
        # Use log scale for frequency (typical range: 1 to 1M+)
        log_freq = math.log10(max(1, frequency))
        # Normalize assuming max frequency around 1M (log10(1M) = 6)
        return min(log_freq / 6.0, 1.0)

    def _normalize_entropy(self, entropy: float) -> float:
        """Normalize entropy to 0-1 range."""
        if entropy <= 0:
            return 0.0
        # Entropy typically ranges from 0 to ~10 for 5-letter words
        return min(entropy / 10.0, 1.0)

    def _calculate_fallback_score(self, word: str) -> float:
        """Calculate fallback score when no word_manager is available."""
        # Simple scoring based on unique letters and common letter patterns
        unique_letters = len(set(word))
        common_letters = set("ETAOINSHRDLU")
        common_count = len(set(word).intersection(common_letters))

        return (unique_letters / 5.0) * 0.6 + (common_count / 5.0) * 0.4

    def _get_optimal_starters(
        self,
        possible_words: List[str],
        common_words: List[str],
        count: int,
        word_manager,
    ) -> List[str]:
        """Get optimal starting words balancing frequency and entropy."""
        if word_manager is None:
            # Fallback to predefined starters
            starters = ["ADIEU", "AUDIO", "SOARE", "ROATE", "RAISE", "SLATE", "CRANE"]
            valid_starters = [w for w in starters if w in possible_words]
            return (
                valid_starters[:count]
                if len(valid_starters) >= count
                else valid_starters
            )

        # Find words with high entropy and reasonable frequency
        candidates = possible_words[
            : min(len(possible_words), 100)
        ]  # Limit for performance
        starter_scores = {}

        for word in candidates:
            frequency = word_manager.get_word_frequency(word)
            entropy = word_manager.get_word_entropy(word)

            # For starters, weight entropy more heavily
            freq_score = self._normalize_frequency(frequency)
            entropy_score = self._normalize_entropy(entropy)

            # Starter-specific weighting (favor entropy for first guess)
            starter_score = 0.3 * freq_score + 0.7 * entropy_score

            # Slight boost for common words
            if word in common_words:
                starter_score *= 1.05

            starter_scores[word] = starter_score

        # Return top starters by score
        sorted_starters = sorted(
            starter_scores.keys(), key=lambda w: starter_scores[w], reverse=True
        )
        return sorted_starters[:count]

    def _build_balanced_result(
        self, sorted_words: List[str], common_words: List[str], count: int
    ) -> List[str]:
        """Build balanced result favoring common words."""
        common_matches = [w for w in sorted_words if w in common_words]
        other_matches = [w for w in sorted_words if w not in common_words]

        # Allocate spots (favor common words but don't exclude others)
        common_count = min(
            len(common_matches), max(count // 2, count - len(other_matches))
        )

        result = []
        result.extend(common_matches[:common_count])
        result.extend(other_matches[: count - len(result)])

        return result[:count]
