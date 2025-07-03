# src/modules/backend/solver/stateless_two_step_strategy.py
"""
Stateless two-step strategy for Wordle that uses a two-step lookahead approach.
"""
import math
from collections import defaultdict
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

from .solver_utils import calculate_pattern
from .stateless_solver_strategy import StatelessSolverStrategy

if TYPE_CHECKING:
    from ..stateless_word_manager import StatelessWordManager
    from ..word_manager import WordManager


class StatelessTwoStepStrategy(StatelessSolverStrategy):
    """
    Stateless strategy that looks ahead two steps to choose optimal guesses.
    """

    def __init__(self, max_patterns_to_evaluate: int = 20):
        """
        Initialize the two-step strategy.

        Args:
            max_patterns_to_evaluate: Maximum number of patterns to evaluate for performance
        """
        self.max_patterns_to_evaluate = max_patterns_to_evaluate

    def get_top_suggestions(
        self,
        constraints: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """Get top N suggestions based on two-step lookahead using stateless filtering."""

        # Get filtered words using stateless methods
        possible_words, common_words = self._get_filtered_words(
            constraints, word_manager, stateless_word_manager, word_set
        )

        if not possible_words:
            return []

        # For very few words, use simple sorting
        if len(possible_words) <= 5:
            return self._sort_by_preference(
                possible_words,
                common_words,
                word_manager,
                stateless_word_manager,
                prefer_common,
            )

        # For early game or large search spaces, fallback to entropy-based selection
        if not constraints or len(possible_words) > 100:
            return self._get_entropy_based_suggestions(
                possible_words,
                common_words,
                count,
                word_manager,
                stateless_word_manager,
                prefer_common,
            )

        # Use two-step analysis for medium-sized search spaces
        return self._get_two_step_suggestions(
            possible_words,
            common_words,
            constraints,
            count,
            word_manager,
            stateless_word_manager,
            prefer_common,
        )

    def _get_two_step_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        constraints: List[Tuple[str, str]],
        count: int,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
    ) -> List[str]:
        """Get suggestions using two-step lookahead analysis."""

        # Get candidates to evaluate (limit for performance)
        candidates = self._get_limited_candidates(
            possible_words, common_words, max_candidates=30
        )

        # Score each candidate using two-step analysis
        candidate_scores = {}

        for candidate in candidates:
            score = self._evaluate_two_step_candidate(
                candidate,
                possible_words,
                constraints,
                word_manager,
                stateless_word_manager,
            )
            candidate_scores[candidate] = score

        # Sort candidates by score
        sorted_candidates = sorted(
            candidate_scores.items(), key=lambda x: x[1], reverse=True
        )

        # Extract top candidates
        top_candidates = [word for word, _ in sorted_candidates[: count * 2]]

        # Apply balanced selection if prefer_common is True
        if prefer_common:
            return self._balance_common_and_other(top_candidates, common_words, count)
        else:
            return top_candidates[:count]

    def _evaluate_two_step_candidate(
        self,
        candidate: str,
        possible_words: List[str],
        constraints: List[Tuple[str, str]],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> float:
        """Evaluate a candidate using two-step lookahead."""

        # Simulate all possible patterns for this candidate
        pattern_groups = defaultdict(list)

        for target_word in possible_words:
            pattern = calculate_pattern(candidate, target_word)
            pattern_groups[pattern].append(target_word)

        # Calculate expected value of second step
        total_score = 0.0
        total_words = len(possible_words)

        # Limit patterns evaluated for performance
        patterns_to_evaluate = list(pattern_groups.items())[
            : self.max_patterns_to_evaluate
        ]

        for pattern, remaining_words in patterns_to_evaluate:
            if len(remaining_words) == 1:
                # Perfect - game would be won
                score = 1.0
            elif len(remaining_words) <= 3:
                # Very good - easy to finish
                score = 0.9
            else:
                # Need to evaluate second step
                score = self._evaluate_second_step(
                    remaining_words,
                    constraints + [(candidate, pattern)],
                    word_manager,
                    stateless_word_manager,
                )

            # Weight by probability of this pattern
            probability = len(remaining_words) / total_words
            total_score += probability * score

        return total_score

    def _evaluate_second_step(
        self,
        remaining_words: List[str],
        updated_constraints: List[Tuple[str, str]],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> float:
        """Evaluate the quality of second step options."""

        if len(remaining_words) <= 1:
            return 1.0

        # Get potential second guesses (limit for performance)
        second_candidates = (
            remaining_words[:10] if len(remaining_words) > 10 else remaining_words
        )

        best_second_score = 0.0

        for second_candidate in second_candidates:
            # Simulate second guess
            second_pattern_groups = defaultdict(list)

            for target in remaining_words:
                pattern = calculate_pattern(second_candidate, target)
                second_pattern_groups[pattern].append(target)

            # Calculate expected remaining words after second guess
            expected_remaining = 0.0
            for pattern, final_words in second_pattern_groups.items():
                probability = len(final_words) / len(remaining_words)
                expected_remaining += probability * len(final_words)

            # Score inversely proportional to expected remaining words
            if expected_remaining > 0:
                second_score = 1.0 / expected_remaining
            else:
                second_score = 1.0

            best_second_score = max(best_second_score, second_score)

        return min(1.0, best_second_score)

    def _get_entropy_based_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        count: int,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
    ) -> List[str]:
        """Fallback to entropy-based suggestions for early game or large spaces."""

        # Use entropy scoring as fallback
        word_scores = {}

        for word in possible_words[:50]:  # Limit for performance
            entropy = self._get_word_entropy(word, word_manager, stateless_word_manager)
            frequency = self._get_word_frequency(
                word, word_manager, stateless_word_manager
            )

            # Combine entropy and frequency
            normalized_entropy = min(1.0, entropy / 10.0) if entropy > 0 else 0.0
            normalized_frequency = (
                min(1.0, math.log10(frequency + 1) / 6.0) if frequency > 0 else 0.0
            )

            combined_score = 0.7 * normalized_entropy + 0.3 * normalized_frequency

            word_scores[word] = combined_score

        # Sort by combined score
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        top_words = [word for word, _ in sorted_words[: count * 2]]

        # Apply balanced selection if prefer_common is True
        if prefer_common:
            return self._balance_common_and_other(top_words, common_words, count)
        else:
            return top_words[:count]

    def _get_limited_candidates(
        self,
        possible_words: List[str],
        common_words: List[str],
        max_candidates: int = 30,
    ) -> List[str]:
        """Get a limited set of candidates for evaluation."""
        # Include possible words (limited)
        candidates = possible_words[: max_candidates // 2]

        # Add some common words not already included
        existing_candidates = set(candidates)
        additional_common = [
            word for word in common_words if word not in existing_candidates
        ][: max_candidates // 2]

        return candidates + additional_common

    def _sort_by_preference(
        self,
        words: List[str],
        common_words: List[str],
        prefer_common: bool = True,
    ) -> List[str]:
        """Sort words by preference when few options remain."""
        if not prefer_common:
            return sorted(words)

        # Separate common and other words
        common_set = set(common_words)
        common_words_filtered = [w for w in words if w in common_set]
        other_words = [w for w in words if w not in common_set]

        # Sort each group (can add frequency-based sorting here if needed)
        common_sorted = sorted(common_words_filtered)
        other_sorted = sorted(other_words)

        return common_sorted + other_sorted

    def _balance_common_and_other(
        self, candidates: List[str], common_words: List[str], count: int
    ) -> List[str]:
        """Balance common and other words in final suggestions."""
        common_set = set(common_words)
        common_candidates = [w for w in candidates if w in common_set]
        other_candidates = [w for w in candidates if w not in common_set]

        # For two-step strategy, prefer 80% common words
        common_target = max(1, int(count * 0.8))
        other_target = count - common_target

        # Build result
        result = []
        result.extend(common_candidates[:common_target])
        result.extend(other_candidates[:other_target])

        # Fill remaining slots
        remaining_slots = count - len(result)
        if remaining_slots > 0:
            remaining_candidates = [w for w in candidates if w not in result]
            result.extend(remaining_candidates[:remaining_slots])

        return result[:count]
