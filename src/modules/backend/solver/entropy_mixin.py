# src/modules/backend/solver/entropy_mixin.py
"""
Mixin class for entropy calculation functionality used in entropy-based strategies.
"""
import math
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Tuple

from .constants import DEFAULT_PATTERN_COUNT_THRESHOLD

if TYPE_CHECKING:
    pass


class EntropyCalculationMixin:
    """
    A mixin class that provides entropy calculation methods for entropy-based strategies.

    This mixin is used by both legacy and stateless entropy-based strategies to share
    common entropy calculation functionality.
    """

    def calculate_entropy(
        self,
        word: str,
        possible_words: List[str],
        word_manager=None,
        stateless_word_manager=None,
    ) -> float:
        """
        Calculate the entropy (information gain) for a given word.

        Args:
            word: The word to calculate entropy for
            possible_words: List of possible target words
            word_manager: Optional traditional WordManager instance
            stateless_word_manager: Optional StatelessWordManager instance

        Returns:
            The entropy value as a float
        """
        if not possible_words:
            return 0.0

        # Count the pattern distribution
        pattern_counts: Dict[str, int] = defaultdict(int)
        total_patterns = len(possible_words)

        # Use either the stateless or traditional word manager's functionality
        if stateless_word_manager is not None:
            for possible_word in possible_words:
                pattern = stateless_word_manager.calculate_pattern(word, possible_word)
                pattern_counts[pattern] += 1
        elif word_manager is not None:
            for possible_word in possible_words:
                pattern = word_manager.calculate_pattern(word, possible_word)
                pattern_counts[pattern] += 1
        else:
            raise ValueError(
                "Either word_manager or stateless_word_manager must be provided"
            )

        # Calculate entropy using the pattern distribution
        entropy = 0.0
        for pattern, count in pattern_counts.items():
            probability = count / total_patterns
            if probability > 0:  # Avoid log(0)
                entropy -= probability * math.log2(probability)

        return entropy

    def calculate_entropy_for_words(
        self,
        words: List[str],
        possible_words: List[str],
        word_manager=None,
        stateless_word_manager=None,
    ) -> Dict[str, float]:
        """
        Calculate entropy for multiple words efficiently.

        Args:
            words: List of words to calculate entropy for
            possible_words: List of possible target words
            word_manager: Optional traditional WordManager instance
            stateless_word_manager: Optional StatelessWordManager instance

        Returns:
            Dictionary mapping each word to its entropy value
        """
        result = {}

        # Optimization for large number of words
        if len(words) > DEFAULT_PATTERN_COUNT_THRESHOLD:
            # For large word sets, we could optimize pattern calculation
            # but currently using the same approach as for small sets
            for word in words:
                result[word] = self.calculate_entropy(
                    word, possible_words, word_manager, stateless_word_manager
                )
        else:
            # For smaller word sets, calculate directly
            for word in words:
                result[word] = self.calculate_entropy(
                    word, possible_words, word_manager, stateless_word_manager
                )

        return result

    def _group_words_by_pattern(
        self,
        words: List[str],
        possible_words: List[str],
        word_manager=None,
        stateless_word_manager=None,
    ) -> Dict[str, List[Tuple[str, str]]]:
        """
        Group words by pattern for more efficient entropy calculation.

        This is an optimization for handling large word sets.

        Args:
            words: List of words to process
            possible_words: List of possible target words
            word_manager: Optional traditional WordManager instance
            stateless_word_manager: Optional StatelessWordManager instance

        Returns:
            Dictionary grouping words by their patterns
        """
        grouped_words = defaultdict(list)

        for i, word in enumerate(words):
            for j, possible_word in enumerate(possible_words):
                if stateless_word_manager is not None:
                    pattern = stateless_word_manager.calculate_pattern(
                        word, possible_word
                    )
                elif word_manager is not None:
                    pattern = word_manager.calculate_pattern(word, possible_word)
                else:
                    raise ValueError(
                        "Either word_manager or stateless_word_manager must be provided"
                    )

                grouped_words[pattern].append((word, possible_word))

        return grouped_words
