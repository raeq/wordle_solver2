# src/modules/backend/solver/two_step_strategy.py
"""
Two-step strategy for Wordle that uses a two-step lookahead approach.
"""
import math
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from .common_utils import (
    CandidateSelector,
    EntropyCalculator,
    MemoryOptimizedWordProcessor,
    WordSorter,
    get_pattern_counter,
    return_pattern_counter,
)
from .constants import (
    DEFAULT_SUGGESTIONS_COUNT,
    PERFECT_SCORE,
    TWO_STEP_COUNT_MULTIPLIER,
    TWO_STEP_FEW_WORDS_THRESHOLD,
    TWO_STEP_LARGE_SEARCH_THRESHOLD,
    TWO_STEP_MAX_ADDITIONAL_COMMON,
    TWO_STEP_MAX_PATTERNS_DEFAULT,
    TWO_STEP_MAX_POSSIBLE_CANDIDATES,
    TWO_STEP_SECOND_STEP_CANDIDATE_LIMIT,
)
from .entropy_strategy import EntropyStrategy
from .solver_strategy import SolverStrategy
from .solver_utils import calculate_pattern

if TYPE_CHECKING:
    from ..word_manager import WordManager


class TwoStepStrategy(SolverStrategy):
    """
    Strategy that looks ahead two steps to choose optimal guesses.

    For each candidate guess, it simulates all possible feedback patterns,
    then for each resulting game state, it finds the best second guess.
    The strategy chooses the first guess that leads to the best expected
    outcome after two steps.
    """

    def __init__(self, max_patterns_to_evaluate: int = TWO_STEP_MAX_PATTERNS_DEFAULT):
        """
        Initialize the two-step strategy.

        Args:
            max_patterns_to_evaluate: Maximum number of patterns to evaluate for performance
        """
        self.max_patterns_to_evaluate = max_patterns_to_evaluate
        self.entropy_fallback = EntropyStrategy()

    def get_top_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: List[Tuple[str, str]],
        count: int = DEFAULT_SUGGESTIONS_COUNT,
        word_manager: Optional["WordManager"] = None,
    ) -> List[str]:
        """Get top N suggestions based on two-step lookahead."""
        if not possible_words:
            return []

        # For very few words, use simple sorting
        if len(possible_words) <= TWO_STEP_FEW_WORDS_THRESHOLD:
            return WordSorter.sort_by_commonness_priority(
                possible_words, common_words, word_manager
            )

        # For early game or large search spaces, fallback to entropy
        if not guesses_so_far or len(possible_words) > TWO_STEP_LARGE_SEARCH_THRESHOLD:
            result = self.entropy_fallback.get_top_suggestions(
                possible_words, common_words, guesses_so_far, count, word_manager
            )
            return list(result)  # Ensure return type is List[str]

        # Use memory-optimized candidate selection for two-step analysis
        candidates_to_evaluate = CandidateSelector.get_limited_candidates(
            possible_words,
            common_words,
            max_possible=TWO_STEP_MAX_POSSIBLE_CANDIDATES,
            max_additional_common=TWO_STEP_MAX_ADDITIONAL_COMMON,
        )

        # Use memory-optimized processing for two-step scoring
        def two_step_scoring_func(word: str, pw: List[str]) -> float:
            return float(self._calculate_two_step_score_optimized(word, pw))

        word_score_gen = MemoryOptimizedWordProcessor.word_score_generator(
            candidates_to_evaluate, two_step_scoring_func, possible_words
        )

        sorted_words = MemoryOptimizedWordProcessor.get_top_n_words(
            word_score_gen,
            min(count * TWO_STEP_COUNT_MULTIPLIER, len(candidates_to_evaluate)),
            reverse=True,
        )

        # Use common utility for balanced distribution
        return WordSorter.balance_common_and_other(sorted_words, common_words, count)

    def _calculate_two_step_score_optimized(
        self, candidate: str, possible_answers: List[str]
    ) -> float:
        """
        Calculate two-step score with memory optimization.
        """
        if not possible_answers:
            return 0.0

        # Use object pooling for pattern counting
        pattern_counts = get_pattern_counter()

        try:
            # First step: get all possible patterns and their frequencies
            for answer in possible_answers:
                pattern = calculate_pattern(candidate, answer)
                pattern_counts[pattern] += 1

            # Limit patterns to evaluate for performance
            sorted_patterns = sorted(
                pattern_counts.items(), key=lambda x: x[1], reverse=True
            )[: self.max_patterns_to_evaluate]

            total_score = 0.0
            total_answers = len(possible_answers)

            # Second step: for each pattern, calculate the best follow-up entropy
            for pattern, count in sorted_patterns:
                if count == 0:
                    continue

                # Simulate remaining words after this pattern
                remaining_words = self._get_remaining_words_after_pattern(
                    candidate, pattern, possible_answers
                )

                if len(remaining_words) <= 1:
                    # If only one word remains, perfect outcome
                    second_step_score = PERFECT_SCORE
                else:
                    # Calculate best entropy for remaining words
                    second_step_score = self._get_best_second_step_entropy(
                        remaining_words
                    )

                # Weight by probability of this pattern
                probability = count / total_answers
                total_score += probability * second_step_score

            return float(total_score)

        finally:
            # Return object to pool
            return_pattern_counter(pattern_counts)

    def _get_remaining_words_after_pattern(
        self, guess: str, pattern: str, possible_words: List[str]
    ) -> List[str]:
        """Get words that would remain after a specific guess-pattern combination."""
        remaining = []
        for word in possible_words:
            if calculate_pattern(guess, word) == pattern:
                remaining.append(word)
        return remaining

    def _get_best_second_step_entropy(self, remaining_words: List[str]) -> float:
        """Get the best entropy score for the second step with limited candidates."""
        if len(remaining_words) <= 1:
            return PERFECT_SCORE  # Perfect score for single word

        # For performance, only evaluate a subset of candidates for second step
        candidates = remaining_words[
            : min(TWO_STEP_SECOND_STEP_CANDIDATE_LIMIT, len(remaining_words))
        ]

        best_entropy = 0.0
        for candidate in candidates:
            entropy = EntropyCalculator.calculate_entropy(candidate, remaining_words)
            best_entropy = max(best_entropy, entropy)

        return best_entropy

    # Add backward compatibility methods for tests
    def _group_by_pattern(
        self, candidate: str, possible_answers: List[str]
    ) -> Dict[str, List[str]]:
        """Group possible answers by the pattern they would produce with the candidate."""
        groups = defaultdict(list)
        for answer in possible_answers:
            pattern = calculate_pattern(candidate, answer)
            groups[pattern].append(answer)
        return dict(groups)

    def _calculate_entropy_from_groups(
        self, groups: Dict[str, List[str]], total_count: int
    ) -> float:
        """Calculate entropy from grouped patterns."""
        entropy = 0.0
        for group in groups.values():
            if len(group) > 0:
                probability = len(group) / total_count
                entropy -= probability * math.log2(probability)
        return entropy

    def _calculate_two_step_score(
        self, candidate: str, possible_words: List[str], common_words: List[str]
    ) -> float:
        """Backward compatibility method for tests."""
        score = self._calculate_two_step_score_optimized(candidate, possible_words)
        # Normalize score to 0-1 range for test compatibility
        # Two-step scores can be high, so normalize by a reasonable maximum
        max_score = 10.0  # Maximum theoretical score
        return float(min(score / max_score, 1.0))
