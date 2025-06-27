# src/modules/backend/solver/frequency_strategy.py
"""
Frequency-based solver strategy for Wordle using corpus frequency data.
"""
import math
from typing import TYPE_CHECKING, List, Optional, Tuple

from src.modules.backend.solver.solver_strategy import SolverStrategy

from .common_utils import (
    MemoryOptimizedWordProcessor,
    WordSorter,
)
from .memory_profiler import profile_memory

if TYPE_CHECKING:
    from ..word_manager import WordManager


class FrequencyStrategy(SolverStrategy):
    """Strategy that uses actual word frequency data from corpus to suggest words."""

    @profile_memory("FrequencyStrategy.get_top_suggestions")
    def get_top_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
    ) -> List[str]:
        """Get top N suggestions based on actual word frequency from corpus."""
        if not possible_words:
            return []

        if len(possible_words) <= count:
            # Use common utility for sorting by frequency with common priority
            return WordSorter.sort_by_commonness_priority(
                possible_words, common_words, word_manager
            )

        # Use memory-optimized word processing with generators
        def frequency_scoring_func(
            word: str, gs: List[Tuple[str, str]], wm: "WordManager"
        ) -> float:
            return self._get_frequency_score(word, gs, wm)

        # Use generator-based processing to reduce memory usage
        word_score_gen = MemoryOptimizedWordProcessor.word_score_generator(
            possible_words, frequency_scoring_func, guesses_so_far, word_manager
        )

        sorted_words = MemoryOptimizedWordProcessor.get_top_n_words(
            word_score_gen, min(count * 2, len(possible_words)), reverse=True
        )

        # Use common utility for balanced distribution
        return WordSorter.balance_common_and_other(sorted_words, common_words, count)

    def _get_frequency_score(
        self, word: str, guesses_so_far: List[Tuple[str, str]], word_manager=None
    ) -> float:
        """Get frequency score for a word with adjustments for previous guesses."""
        if word_manager is not None:
            # Use actual corpus frequency data
            base_score = float(word_manager.get_word_frequency(word))

            # Normalize score to a reasonable range (log scale for very high frequencies)
            if base_score > 0:
                # Use log scale to prevent extremely high frequencies from dominating
                normalized_score = math.log10(base_score + 1)
            else:
                normalized_score = 0.0

            # Apply small bonus for words not similar to previous guesses
            uniqueness_bonus = self._calculate_uniqueness_bonus(word, guesses_so_far)

            return normalized_score + uniqueness_bonus
        # Fallback scoring based on word characteristics
        return self._fallback_frequency_score(word)

    def _calculate_uniqueness_bonus(
        self, word: str, guesses_so_far: List[Tuple[str, str]]
    ) -> float:
        """Calculate a small bonus for words that are different from previous guesses."""
        if not guesses_so_far:
            return 0.0

        # Small bonus for words that share fewer letters with previous guesses
        previous_letters: set[str] = set()
        for guess, _ in guesses_so_far:
            previous_letters.update(guess.upper())

        word_letters = set(word.upper())
        shared_letters = len(word_letters.intersection(previous_letters))
        total_letters = len(word_letters)

        # Small bonus (max 0.5) for words with fewer shared letters
        uniqueness_ratio = (
            1.0 - (shared_letters / total_letters) if total_letters > 0 else 0.0
        )
        return uniqueness_ratio * 0.5

    def _fallback_frequency_score(self, word: str) -> float:
        """Fallback scoring when no word_manager is available."""
        # Score based on vowel content and common letter patterns
        vowel_count = sum(1 for letter in word.upper() if letter in "AEIOU")
        unique_letters = len(set(word.upper()))

        # Common starting letters get slight bonus
        common_starters = "TSRNA"
        starter_bonus = 0.1 if word[0].upper() in common_starters else 0.0

        return vowel_count + (unique_letters * 0.5) + starter_bonus
