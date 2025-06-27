# src/modules/backend/solver/common_utils.py
"""
Common utility functions to reduce code duplication across solver strategies.
"""
import heapq
import math
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Tuple

from .solver_utils import calculate_pattern

if TYPE_CHECKING:
    from ..word_manager import WordManager


class WordSorter:
    """Utility class for sorting words by commonness and other criteria."""

    @staticmethod
    def sort_by_commonness_priority(
        words: List[str],
        common_words: List[str],
        word_manager: Optional["WordManager"] = None,
    ) -> List[str]:
        """Sort words prioritizing common words first, then by frequency if available."""
        if not words:
            return []

        common_possible = [w for w in words if w in common_words]
        other_possible = [w for w in words if w not in common_words]

        if word_manager is not None:
            # Sort each group by frequency (highest first)
            def get_frequency(w: str) -> float:
                return word_manager.get_word_frequency(w)  # type: ignore

            common_possible.sort(key=get_frequency, reverse=True)
            other_possible.sort(key=get_frequency, reverse=True)
        else:
            # Fallback to alphabetical sorting
            common_possible.sort()
            other_possible.sort()

        return common_possible + other_possible

    @staticmethod
    def balance_common_and_other(
        sorted_words: List[str], common_words: List[str], count: int
    ) -> List[str]:
        """Balance the result between common and uncommon words."""
        common_matches = [w for w in sorted_words if w in common_words]
        other_matches = [w for w in sorted_words if w not in common_words]

        # Use about half for common words, but ensure we fill the count
        common_to_include = min(
            len(common_matches), max(count // 2, count - len(other_matches))
        )

        result = []
        result.extend(common_matches[:common_to_include])
        result.extend(other_matches[: count - len(result)])

        return result[:count]


class EntropyCalculator:
    """Utility class for calculating entropy scores."""

    @staticmethod
    def calculate_entropy(candidate: str, possible_answers: List[str]) -> float:
        """
        Calculate the entropy (information gain) for a candidate word.
        Higher entropy means more information is gained by guessing this word.
        """
        if not possible_answers:
            return 0.0

        # Count how many words would remain for each possible feedback pattern
        pattern_counts: Dict[str, int] = defaultdict(int)

        # For each possible answer, determine what pattern the candidate would give
        for answer in possible_answers:
            pattern = calculate_pattern(candidate, answer)
            pattern_counts[pattern] += 1

        # Calculate entropy using Shannon's formula
        total_answers = len(possible_answers)
        entropy = 0.0

        for count in pattern_counts.values():
            if count > 0:
                probability = count / total_answers
                entropy -= probability * math.log2(probability)

        return entropy

    @staticmethod
    def calculate_entropy_with_early_termination(
        candidate: str,
        possible_answers: List[str],
        excellent_threshold: float = float("inf"),
    ) -> float:
        """Calculate entropy with early termination for performance optimization."""
        if not possible_answers:
            return 0.0

        # Use simpler calculation when threshold is infinite
        if excellent_threshold == float("inf"):
            return EntropyCalculator.calculate_entropy(candidate, possible_answers)

        return EntropyCalculator._calculate_with_early_termination(
            candidate, possible_answers, excellent_threshold
        )

    @staticmethod
    def _calculate_with_early_termination(
        candidate: str, possible_answers: List[str], excellent_threshold: float
    ) -> float:
        """Helper method for early termination calculation."""
        pattern_counts: Dict[str, int] = defaultdict(int)
        total_answers = len(possible_answers)
        patterns_seen = 0

        for answer in possible_answers:
            pattern = calculate_pattern(candidate, answer)
            pattern_counts[pattern] += 1
            patterns_seen += 1

            # Early termination check every 20 evaluations for performance
            if patterns_seen % 20 == 0 and patterns_seen > 40:
                estimated_entropy = EntropyCalculator._estimate_final_entropy(
                    pattern_counts, patterns_seen, total_answers
                )
                if estimated_entropy > excellent_threshold:
                    return estimated_entropy

        # Calculate final entropy
        return EntropyCalculator._calculate_final_entropy(pattern_counts, total_answers)

    @staticmethod
    def _estimate_final_entropy(
        pattern_counts: Dict[str, int], patterns_seen: int, total_answers: int
    ) -> float:
        """Estimate final entropy based on partial calculation."""
        partial_entropy = 0.0
        for count in pattern_counts.values():
            if count > 0:
                probability = count / patterns_seen
                partial_entropy -= probability * math.log2(probability)

        # Scale to estimated final entropy
        return partial_entropy * (total_answers / patterns_seen)

    @staticmethod
    def _calculate_final_entropy(
        pattern_counts: Dict[str, int], total_answers: int
    ) -> float:
        """Calculate final entropy from pattern counts."""
        entropy = 0.0
        for count in pattern_counts.values():
            if count > 0:
                probability = count / total_answers
                entropy -= probability * math.log2(probability)
        return entropy


class CandidateSelector:
    """Utility class for managing candidate selection with performance optimizations."""

    @staticmethod
    def get_limited_candidates(
        possible_words: List[str],
        common_words: List[str],
        max_possible: int = 100,
        max_additional_common: int = 10,
    ) -> List[str]:
        """Get a limited set of candidates for evaluation to improve performance."""
        candidates_to_evaluate = possible_words.copy()

        # If we have too many possible words, limit the evaluation set
        if len(possible_words) > max_possible:
            candidates_to_evaluate = possible_words[:max_possible]

            # Add some common words that aren't in possible words
            additional_common = [w for w in common_words if w not in possible_words][
                :max_additional_common
            ]
            candidates_to_evaluate.extend(additional_common)

        return candidates_to_evaluate

    @staticmethod
    def get_good_starters(
        possible_words: List[str], common_words: List[str], count: int
    ) -> List[str]:
        """Return good starting words based on predefined choices and vowel content."""
        # Strong starting words based on high entropy and vowel diversity
        starters = [
            "ADIEU",
            "AUDIO",
            "SOARE",
            "ROATE",
            "RAISE",
            "SLATE",
            "CRANE",
            "TRACE",
        ]

        # Filter out any starters that aren't in our dictionary
        valid_starters = [w for w in starters if w in possible_words]

        # If we have enough valid starters, return those
        if len(valid_starters) >= count:
            return valid_starters[:count]

        # Add high vowel-count words
        vowel_scores = {}
        for word in common_words:
            if word not in valid_starters:
                vowel_count = sum(1 for letter in set(word) if letter in "AEIOU")
                unique_letters = len(set(word))
                # Score based on unique letters and vowels
                vowel_scores[word] = unique_letters + (vowel_count * 0.5)

        # Sort by vowel score
        vowel_words = [
            word
            for word, score in sorted(
                vowel_scores.items(), key=lambda x: x[1], reverse=True
            )
        ]

        # Combine starters with vowel-rich words
        valid_starters.extend(vowel_words[: count - len(valid_starters)])
        return valid_starters[:count]


class MemoryOptimizedWordProcessor:
    """Memory-efficient word processing using generators."""

    @staticmethod
    def word_score_generator(
        candidates: List[str], scoring_func, *args
    ) -> Generator[Tuple[str, float], None, None]:
        """Generate word scores one at a time to reduce memory usage."""
        for word in candidates:
            score = scoring_func(word, *args)
            yield word, score

    @staticmethod
    def get_top_n_words(
        word_score_gen: Generator[Tuple[str, float], None, None],
        n: int,
        reverse: bool = True,
    ) -> List[str]:
        """Get top N words from a generator without storing all scores in memory."""
        # Use a heap to maintain top N items efficiently
        if reverse:
            # For highest scores, use negative values in min-heap
            heap: List[Tuple[float, str]] = []
            for word, score in word_score_gen:
                if len(heap) < n:
                    heapq.heappush(heap, (-score, word))
                elif -score > heap[0][0]:
                    heapq.heapreplace(heap, (-score, word))

            # Extract and reverse the order
            return [word for _, word in sorted(heap, reverse=True)]

        # For lowest scores, use regular min-heap
        min_heap: List[Tuple[float, str]] = []
        for word, score in word_score_gen:
            if len(min_heap) < n:
                heapq.heappush(min_heap, (score, word))
            elif score < min_heap[0][0]:
                heapq.heapreplace(min_heap, (score, word))

        return [word for _, word in sorted(min_heap)]


class ObjectPool:
    """Simple object pool for frequently created objects."""

    def __init__(self, factory_func, max_size: int = 100):
        self._factory = factory_func
        self._pool: List[Any] = []
        self._max_size = max_size

    def get(self):
        """Get an object from the pool or create a new one."""
        if self._pool:
            return self._pool.pop()
        return self._factory()

    def return_object(self, obj):
        """Return an object to the pool."""
        if len(self._pool) < self._max_size:
            # Reset object state if it has a reset method
            if hasattr(obj, "reset"):
                obj.reset()
            self._pool.append(obj)


# Global object pools for commonly used objects
_pattern_count_pool = ObjectPool(lambda: defaultdict(int), max_size=50)
_word_score_pool = ObjectPool(dict, max_size=50)


def get_pattern_counter():
    """Get a pattern counter from the pool."""
    return _pattern_count_pool.get()


def return_pattern_counter(counter):
    """Return a pattern counter to the pool."""
    counter.clear()
    _pattern_count_pool.return_object(counter)


def get_word_score_dict():
    """Get a word score dictionary from the pool."""
    return _word_score_pool.get()


def return_word_score_dict(score_dict):
    """Return a word score dictionary to the pool."""
    score_dict.clear()
    _word_score_pool.return_object(score_dict)
