# src/modules/backend/solver/stateless_frequency_strategy.py
"""
Stateless frequency-based solver strategy for Wordle using corpus frequency data.
"""
import math
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

from .stateless_solver_strategy import StatelessSolverStrategy

if TYPE_CHECKING:
    from ..stateless_word_manager import StatelessWordManager
    from ..word_manager import WordManager


class StatelessFrequencyStrategy(StatelessSolverStrategy):
    """Stateless strategy that uses actual word frequency data from corpus to suggest words."""

    def get_top_suggestions(
        self,
        constraints: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """Get top N suggestions based on actual word frequency from corpus using stateless filtering."""

        # Get filtered words using stateless methods
        possible_words, common_words = self._get_filtered_words(
            constraints, word_manager, stateless_word_manager, word_set
        )

        if not possible_words:
            return []

        if len(possible_words) <= count:
            # Use common utility for sorting by frequency with common priority
            return self._sort_by_frequency_and_commonness(
                possible_words,
                common_words,
                word_manager,
                stateless_word_manager,
                prefer_common,
            )

        # Use memory-optimized word processing with generators
        def frequency_scoring_func(word: str) -> float:
            return self._get_frequency_score(
                word, constraints, word_manager, stateless_word_manager
            )

        # Use generator-based processing to reduce memory usage
        word_scores = [(word, frequency_scoring_func(word)) for word in possible_words]
        word_scores.sort(key=lambda x: x[1], reverse=True)

        # Get top candidates
        top_candidates = [word for word, _ in word_scores[: count * 2]]

        # Balance common and other words if prefer_common is True
        if prefer_common:
            return self._balance_common_and_other(top_candidates, common_words, count)
        else:
            return top_candidates[:count]

    def _get_frequency_score(
        self,
        word: str,
        constraints: List[Tuple[str, str]],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> float:
        """Get frequency score for a word with adjustments for previous guesses."""

        # Get base frequency score
        base_score = float(
            self._get_word_frequency(word, word_manager, stateless_word_manager)
        )

        # Normalize score to a reasonable range (log scale for very high frequencies)
        if base_score > 0:
            # Use log scale to prevent extremely high frequencies from dominating
            normalized_score = math.log10(base_score + 1)
        else:
            normalized_score = 0.0

        # Apply small bonus for words not similar to previous guesses
        uniqueness_bonus = self._calculate_uniqueness_bonus(word, constraints)

        return normalized_score + uniqueness_bonus

    def _calculate_uniqueness_bonus(
        self, word: str, constraints: List[Tuple[str, str]]
    ) -> float:
        """Calculate a small bonus for words that are different from previous guesses."""
        if not constraints:
            return 0.0

        # Small bonus for words that share fewer letters with previous guesses
        previous_letters: set[str] = set()
        for guess, _ in constraints:
            previous_letters.update(guess.upper())

        word_letters = set(word.upper())
        shared_letters = len(word_letters.intersection(previous_letters))
        total_letters = len(word_letters)

        # Small bonus (max 0.5) for words with fewer shared letters
        uniqueness_ratio = (
            1.0 - (shared_letters / total_letters) if total_letters > 0 else 0.0
        )
        return uniqueness_ratio * 0.5

    def _sort_by_frequency_and_commonness(
        self,
        words: List[str],
        common_words: List[str],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
    ) -> List[str]:
        """Sort words by frequency with optional common word priority."""
        if not prefer_common:
            # Simple frequency sort
            return sorted(
                words,
                key=lambda w: self._get_word_frequency(
                    w, word_manager, stateless_word_manager
                ),
                reverse=True,
            )

        # Separate common and non-common words
        common_set = set(common_words)
        common_words_filtered = [w for w in words if w in common_set]
        other_words = [w for w in words if w not in common_set]

        # Sort each group by frequency
        common_sorted = sorted(
            common_words_filtered,
            key=lambda w: self._get_word_frequency(
                w, word_manager, stateless_word_manager
            ),
            reverse=True,
        )
        other_sorted = sorted(
            other_words,
            key=lambda w: self._get_word_frequency(
                w, word_manager, stateless_word_manager
            ),
            reverse=True,
        )

        # Combine with common words first
        return common_sorted + other_sorted

    def _balance_common_and_other(
        self, candidates: List[str], common_words: List[str], count: int
    ) -> List[str]:
        """Balance common and other words in the final suggestions."""
        common_set = set(common_words)
        common_candidates = [w for w in candidates if w in common_set]
        other_candidates = [w for w in candidates if w not in common_set]

        # Aim for roughly 60% common words, 40% other words
        common_target = max(1, int(count * 0.6))
        other_target = count - common_target

        # Take up to target from each group
        result = []
        result.extend(common_candidates[:common_target])
        result.extend(other_candidates[:other_target])

        # Fill remaining slots with best candidates overall
        remaining_slots = count - len(result)
        if remaining_slots > 0:
            remaining_candidates = [w for w in candidates if w not in result]
            result.extend(remaining_candidates[:remaining_slots])

        return result[:count]

    def _fallback_frequency_score(self, word: str) -> float:
        """Fallback scoring based on word characteristics when no frequency data available."""
        # Simple heuristic: prefer words with common letters
        common_letters = set("ETAOINSHRDLCUMWFGYPBVKJXQZ")
        word_letters = set(word.upper())

        # Score based on how many common letters the word contains
        common_count = len(word_letters.intersection(common_letters))
        return float(common_count) / len(word_letters) if word_letters else 0.0
