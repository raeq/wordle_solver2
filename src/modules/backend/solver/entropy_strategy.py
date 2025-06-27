# src/modules/backend/solver/entropy_strategy.py
"""
Entropy-based solver strategy for Wordle using information theory principles.
"""
from typing import TYPE_CHECKING, List, Optional, Tuple

from .common_utils import (
    CandidateSelector,
    MemoryOptimizedWordProcessor,
    WordSorter,
)
from .entropy_mixin import EntropyCalculationMixin
from .memory_profiler import profile_memory
from .solver_strategy import SolverStrategy

if TYPE_CHECKING:
    from ..word_manager import WordManager


class EntropyStrategy(SolverStrategy, EntropyCalculationMixin):
    """Strategy that uses information theory to maximize information gain."""

    @profile_memory("EntropyStrategy.get_top_suggestions")
    def get_top_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
    ) -> List[str]:
        """Get top N suggestions based on entropy (information gain)."""
        if not possible_words:
            return []

        if len(possible_words) <= count:
            # Use common utility for sorting by commonness
            return WordSorter.sort_by_commonness_priority(
                possible_words, common_words, word_manager
            )

        # For the first guess, use predefined strong starters
        if not guesses_so_far:
            return CandidateSelector.get_good_starters(
                possible_words, common_words, count
            )

        # Use memory-optimized candidate selection
        candidates_to_evaluate = CandidateSelector.get_limited_candidates(
            possible_words, common_words, max_possible=50, max_additional_common=10
        )

        # Use memory-optimized word processing with generators
        def entropy_scoring_func(word: str) -> float:
            if word_manager is not None:
                # Use pre-calculated entropy from words.txt if available
                precalc_entropy = word_manager.get_word_entropy(word)
                if precalc_entropy > 0:
                    return float(precalc_entropy)
            # Fallback to calculated entropy using shared mixin method
            return float(self._calculate_entropy_optimized(word, possible_words))

        # Use generator-based processing to reduce memory usage
        word_score_gen = MemoryOptimizedWordProcessor.word_score_generator(
            candidates_to_evaluate, entropy_scoring_func
        )

        sorted_words = MemoryOptimizedWordProcessor.get_top_n_words(
            word_score_gen, min(count * 2, len(candidates_to_evaluate)), reverse=True
        )

        # Handle late game optimization
        if len(possible_words) <= 5:
            # In late game, favor words that could be the answer
            possible_matches = [w for w in sorted_words if w in possible_words]
            other_matches = [w for w in sorted_words if w not in possible_words]
            return (possible_matches + other_matches)[:count]

        # Use common utility for balanced distribution
        return WordSorter.balance_common_and_other(sorted_words, common_words, count)
