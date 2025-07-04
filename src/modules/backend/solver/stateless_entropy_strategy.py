# src/modules/backend/solver/stateless_entropy_strategy.py
"""
Stateless entropy-based solver strategy for Wordle using information theory principles.
"""
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

from .entropy_mixin import EntropyCalculationMixin
from .stateless_solver_strategy import StatelessSolverStrategy

if TYPE_CHECKING:
    from ..legacy_word_manager import WordManager
    from ..stateless_word_manager import StatelessWordManager


class StatelessEntropyStrategy(StatelessSolverStrategy, EntropyCalculationMixin):
    """Stateless strategy that uses information theory to maximize information gain."""

    def get_top_suggestions(
        self,
        constraints: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """Get top N suggestions based on entropy (information gain) using stateless filtering."""

        # Get filtered words using stateless methods
        possible_words, common_words = self._get_filtered_words(
            constraints, word_manager, stateless_word_manager, word_set
        )

        if not possible_words:
            return []

        if len(possible_words) <= count:
            # Use common utility for sorting by commonness
            return self._sort_by_entropy_and_commonness(
                possible_words,
                common_words,
                word_manager,
                stateless_word_manager,
                prefer_common,
            )

        # For the first guess (no constraints), use predefined strong starters
        if not constraints:
            return self._get_good_starters(
                possible_words,
                common_words,
                count,
                word_manager,
                stateless_word_manager,
            )

        # Use memory-optimized candidate selection
        candidates_to_evaluate = self._get_limited_candidates(
            possible_words, common_words, max_possible=50, max_additional_common=10
        )

        # Calculate entropy scores for candidates
        def entropy_scoring_func(word: str) -> float:
            # Use pre-calculated entropy if available
            precalc_entropy = self._get_word_entropy(
                word, word_manager, stateless_word_manager
            )
            if precalc_entropy > 0:
                return float(precalc_entropy)
            # Fallback to calculated entropy using shared mixin method
            return float(self._calculate_entropy_optimized(word, possible_words))

        # Use generator-based processing to reduce memory usage
        word_scores = [
            (word, entropy_scoring_func(word)) for word in candidates_to_evaluate
        ]
        word_scores.sort(key=lambda x: x[1], reverse=True)

        # Get top candidates
        top_candidates = [word for word, _ in word_scores[: count * 2]]

        # Handle late game optimization
        if len(possible_words) <= 5:
            # In late game, favor words that could be the answer
            possible_matches = [w for w in top_candidates if w in possible_words]
            other_matches = [w for w in top_candidates if w not in possible_words]
            return (possible_matches + other_matches)[:count]

        # Balance common and other words if prefer_common is True
        if prefer_common:
            return self._balance_common_and_other(top_candidates, common_words, count)
        else:
            return top_candidates[:count]

    def _get_good_starters(
        self,
        possible_words: List[str],
        common_words: List[str],
        count: int,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> List[str]:
        """Get good starting words based on entropy."""
        # Predefined strong starters with high entropy
        strong_starters = [
            "SLATE",
            "CRANE",
            "ADIEU",
            "AUDIO",
            "RAISE",
            "TEARS",
            "ROATE",
        ]

        # Filter starters that are available in the word set
        available_starters = [
            word for word in strong_starters if word in possible_words
        ]

        if len(available_starters) >= count:
            return available_starters[:count]

        # If not enough predefined starters, add more based on entropy
        remaining_words = [w for w in possible_words if w not in available_starters]

        # Sort remaining words by entropy
        remaining_with_entropy = [
            (word, self._get_word_entropy(word, word_manager, stateless_word_manager))
            for word in remaining_words[:100]  # Limit for performance
        ]
        remaining_with_entropy.sort(key=lambda x: x[1], reverse=True)

        additional_words = [
            word
            for word, _ in remaining_with_entropy[: count - len(available_starters)]
        ]

        return available_starters + additional_words

    def _get_limited_candidates(
        self,
        possible_words: List[str],
        common_words: List[str],
        max_possible: int = 50,
        max_additional_common: int = 10,
    ) -> List[str]:
        """Get a limited set of candidates for evaluation to improve performance."""
        # Start with possible words (limited)
        candidates = possible_words[:max_possible]

        # Add common words that aren't already included
        existing_candidates = set(candidates)
        additional_common = [
            word for word in common_words if word not in existing_candidates
        ][: max_possible // 3]

        return candidates + additional_common

    def _sort_by_entropy_and_commonness(
        self,
        words: List[str],
        common_words: List[str],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
    ) -> List[str]:
        """Sort words by entropy with optional common word priority."""
        if not prefer_common:
            # Simple entropy sort
            return sorted(
                words,
                key=lambda w: self._get_word_entropy(
                    w, word_manager, stateless_word_manager
                ),
                reverse=True,
            )

        # Separate common and non-common words
        common_set = set(common_words)
        common_words_filtered = [w for w in words if w in common_set]
        other_words = [w for w in words if w not in common_set]

        # Sort each group by entropy
        common_sorted = sorted(
            common_words_filtered,
            key=lambda w: self._get_word_entropy(
                w, word_manager, stateless_word_manager
            ),
            reverse=True,
        )
        other_sorted = sorted(
            other_words,
            key=lambda w: self._get_word_entropy(
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
