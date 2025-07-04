# src/modules/backend/solver/stateless_minimax_strategy.py
"""
Stateless minimax strategy for Wordle that minimizes the worst-case number of remaining words.
"""
from collections import defaultdict
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

from .solver_utils import calculate_pattern
from .stateless_solver_strategy import StatelessSolverStrategy

if TYPE_CHECKING:
    from ..legacy_word_manager import WordManager
    from ..stateless_word_manager import StatelessWordManager


class StatelessMinimaxStrategy(StatelessSolverStrategy):
    """
    Stateless strategy that uses minimax algorithm to minimize worst-case remaining words.
    """

    def get_top_suggestions(
        self,
        constraints: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """Get top N suggestions based on minimax strategy using stateless filtering."""

        # Get filtered words using stateless methods
        possible_words, common_words = self._get_filtered_words(
            constraints, word_manager, stateless_word_manager, word_set
        )

        if not possible_words:
            return []

        # Handle cases with few words
        if len(possible_words) <= count:
            return self._prioritize_common_words(
                possible_words, common_words, prefer_common
            )

        # For the first guess, use predefined strong starters
        if not constraints:
            return self._get_good_starters(possible_words, common_words, count)

        # Get optimized candidates for evaluation (limit for performance)
        candidates_to_evaluate = self._get_optimized_candidates(
            possible_words, common_words
        )

        # Score and sort candidates using minimax
        scored_candidates = self._score_candidates_minimax(
            candidates_to_evaluate, possible_words
        )

        # Build the final prioritized result
        return self._build_prioritized_result(
            scored_candidates, possible_words, common_words, count, prefer_common
        )

    def _score_candidates_minimax(
        self, candidates: List[str], possible_words: List[str]
    ) -> List[Tuple[str, int]]:
        """Score candidates using minimax algorithm."""
        candidate_scores = []

        for candidate in candidates:
            max_remaining = self._calculate_max_remaining_words(
                candidate, possible_words
            )
            candidate_scores.append((candidate, max_remaining))

        # Sort by minimax score (lower is better)
        return sorted(candidate_scores, key=lambda x: x[1])

    def _calculate_max_remaining_words(
        self, candidate: str, possible_words: List[str]
    ) -> int:
        """Calculate the maximum number of words that could remain after this guess."""
        pattern_groups = defaultdict(list)

        # Group words by their pattern with the candidate
        for target_word in possible_words:
            pattern = calculate_pattern(candidate, target_word)
            pattern_groups[pattern].append(target_word)

        # Return the size of the largest group (worst case)
        if pattern_groups:
            return max(len(group) for group in pattern_groups.values())
        else:
            return 0

    def _get_good_starters(
        self, possible_words: List[str], common_words: List[str], count: int
    ) -> List[str]:
        """Get good starting words for the first guess."""
        # Predefined strong starters known to have good minimax properties
        strong_starters = [
            "SLATE",
            "CRANE",
            "ADIEU",
            "AUDIO",
            "RAISE",
            "TEARS",
            "ROATE",
        ]

        # Filter available starters
        available_starters = [
            word for word in strong_starters if word in possible_words
        ]

        if len(available_starters) >= count:
            return available_starters[:count]

        # Add common words if needed
        available_starter_set = set(available_starters)
        additional_common = [
            word for word in common_words if word not in available_starter_set
        ][: count - len(available_starters)]

        return available_starters + additional_common

    def _get_optimized_candidates(
        self, possible_words: List[str], common_words: List[str]
    ) -> List[str]:
        """Get optimized set of candidates for evaluation."""
        max_candidates = 30  # Limit for performance

        # Start with possible words (limited)
        candidates = possible_words[: max_candidates // 2]

        # Add common words not already included
        existing_candidates = set(candidates)
        additional_common = [
            word for word in common_words if word not in existing_candidates
        ][: max_candidates // 2]

        return candidates + additional_common

    def _prioritize_common_words(
        self,
        possible_words: List[str],
        common_words: List[str],
        prefer_common: bool = True,
    ) -> List[str]:
        """Prioritize common words when we have few options."""
        if not prefer_common:
            return sorted(possible_words)

        common_set = set(common_words)
        common_possible = [w for w in possible_words if w in common_set]
        other_possible = [w for w in possible_words if w not in common_set]

        return sorted(common_possible) + sorted(other_possible)

    def _build_prioritized_result(
        self,
        scored_candidates: List[Tuple[str, int]],
        possible_words: List[str],
        common_words: List[str],
        count: int,
        prefer_common: bool = True,
    ) -> List[str]:
        """Build prioritized result favoring words that could be the answer."""
        # Extract words from scored candidates
        candidate_words = [word for word, _ in scored_candidates]

        # Separate candidates that could be the answer vs. those that can't
        possible_set = set(possible_words)
        possible_candidates = [w for w in candidate_words if w in possible_set]
        impossible_candidates = [w for w in candidate_words if w not in possible_set]

        # Within each group, apply common word preference if enabled
        if prefer_common:
            common_set = set(common_words)

            # Split possible candidates
            possible_common = [w for w in possible_candidates if w in common_set]
            possible_other = [w for w in possible_candidates if w not in common_set]

            # Split impossible candidates
            impossible_common = [w for w in impossible_candidates if w in common_set]
            impossible_other = [w for w in impossible_candidates if w not in common_set]

            # Prioritize: possible common > possible other > impossible common > impossible other
            result = (
                possible_common + possible_other + impossible_common + impossible_other
            )
        else:
            # No common word preference
            result = possible_candidates + impossible_candidates

        return result[:count]
