# src/modules/backend/solver/stateless_weighted_gain_strategy.py
"""
Stateless weighted Information Gain solver strategy for Wordle that combines multiple metrics.
"""
import math
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

from .solver_utils import calculate_position_frequencies
from .stateless_solver_strategy import StatelessSolverStrategy

if TYPE_CHECKING:
    from ..stateless_word_manager import StatelessWordManager
    from ..word_manager import WordManager


class StatelessWeightedGainStrategy(StatelessSolverStrategy):
    """
    Stateless strategy that combines multiple information metrics for better word suggestions.

    This strategy uses a weighted combination of:
    - Shannon entropy (information gain)
    - Positional information (value of exact position matches)
    - Word frequency (likelihood of being the answer)
    """

    def __init__(
        self,
        entropy_weight: float = 0.5,
        positional_weight: float = 0.3,
        frequency_weight: float = 0.2,
    ):
        """
        Initialize the weighted information gain strategy with customizable weights.

        Args:
            entropy_weight: Weight for Shannon entropy (0-1)
            positional_weight: Weight for positional information (0-1)
            frequency_weight: Weight for word frequency information (0-1)
        """
        # Normalize weights to ensure they sum to 1.0
        total = entropy_weight + positional_weight + frequency_weight
        self.entropy_weight = entropy_weight / total
        self.positional_weight = positional_weight / total
        self.frequency_weight = frequency_weight / total

    def get_top_suggestions(
        self,
        constraints: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
        word_set: Optional[Set[str]] = None,
    ) -> List[str]:
        """Get top N suggestions based on weighted information gain using stateless filtering."""

        # Get filtered words using stateless methods
        possible_words, common_words = self._get_filtered_words(
            constraints, word_manager, stateless_word_manager, word_set
        )

        if not possible_words:
            return []

        # Handle cases with few words
        if len(possible_words) <= count:
            return self._sort_by_weighted_score(
                possible_words,
                common_words,
                word_manager,
                stateless_word_manager,
                prefer_common,
            )

        # For large word lists, use efficient candidate selection
        if len(possible_words) > 100:
            candidates = self._get_limited_candidates(
                possible_words, common_words, max_candidates=50
            )
        else:
            candidates = possible_words

        # Calculate weighted scores for candidates
        word_scores = self._calculate_weighted_scores(
            candidates,
            possible_words,
            constraints,
            word_manager,
            stateless_word_manager,
        )

        # Sort by weighted score
        sorted_candidates = sorted(
            word_scores.items(), key=lambda x: x[1], reverse=True
        )
        top_candidates = [word for word, _ in sorted_candidates[: count * 2]]

        # Apply balanced selection if prefer_common is True
        if prefer_common:
            return self._balance_common_and_other(top_candidates, common_words, count)
        else:
            return top_candidates[:count]

    def _calculate_weighted_scores(
        self,
        candidates: List[str],
        possible_words: List[str],
        constraints: List[Tuple[str, str]],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> Dict[str, float]:
        """Calculate weighted scores for candidate words."""
        word_scores = {}

        # Calculate positional frequencies for possible words
        position_frequencies = calculate_position_frequencies(possible_words)

        for candidate in candidates:
            # 1. Entropy component
            entropy_score = self._calculate_entropy_score(candidate, possible_words)

            # 2. Positional information component
            positional_score = self._calculate_positional_score(
                candidate, position_frequencies
            )

            # 3. Frequency component
            frequency_score = self._calculate_frequency_score(
                candidate, word_manager, stateless_word_manager
            )

            # 4. Uniqueness bonus
            uniqueness_bonus = self._calculate_uniqueness_bonus(candidate, constraints)

            # Combine weighted scores
            weighted_score = (
                self.entropy_weight * entropy_score
                + self.positional_weight * positional_score
                + self.frequency_weight * frequency_score
                + 0.1 * uniqueness_bonus  # Small uniqueness bonus
            )

            word_scores[candidate] = weighted_score

        return word_scores

    def _calculate_entropy_score(
        self, candidate: str, possible_words: List[str]
    ) -> float:
        """Calculate normalized entropy score for a candidate."""
        if len(possible_words) <= 1:
            return 1.0

        # Calculate pattern distribution
        from collections import defaultdict

        from .solver_utils import calculate_pattern

        pattern_counts = defaultdict(int)
        for target in possible_words:
            pattern = calculate_pattern(candidate, target)
            pattern_counts[pattern] += 1

        # Calculate Shannon entropy
        total_words = len(possible_words)
        entropy = 0.0

        for count in pattern_counts.values():
            if count > 0:
                prob = count / total_words
                entropy -= prob * math.log2(prob)

        # Normalize entropy (max entropy for 5-letter words is ~log2(243) ≈ 7.9)
        max_entropy = min(math.log2(len(possible_words)), 7.9)
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _calculate_positional_score(
        self, candidate: str, position_frequencies: Dict
    ) -> float:
        """Calculate positional information score for a candidate."""
        positional_score = 0.0

        for i, letter in enumerate(candidate.upper()):
            if i in position_frequencies and letter in position_frequencies[i]:
                # Score based on how informative this letter is at this position
                letter_freq = position_frequencies[i][letter]
                total_words = sum(position_frequencies[i].values())

                if total_words > 0:
                    # Use inverse frequency - rare letters at positions are more informative
                    info_value = 1.0 - (letter_freq / total_words)
                    positional_score += info_value

        # Normalize by word length
        return positional_score / 5.0

    def _calculate_frequency_score(
        self,
        candidate: str,
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
    ) -> float:
        """Calculate normalized frequency score for a candidate."""
        frequency = self._get_word_frequency(
            candidate, word_manager, stateless_word_manager
        )

        if frequency <= 0:
            return 0.0

        # Use log transformation and normalize
        return min(1.0, math.log10(frequency + 1) / 6.0)

    def _calculate_uniqueness_bonus(
        self, candidate: str, constraints: List[Tuple[str, str]]
    ) -> float:
        """Calculate bonus for words different from previous guesses."""
        if not constraints:
            return 0.0

        # Get letters from previous guesses
        previous_letters = set()
        for guess, _ in constraints:
            previous_letters.update(guess.upper())

        candidate_letters = set(candidate.upper())
        shared_letters = len(candidate_letters.intersection(previous_letters))
        total_letters = len(candidate_letters)

        # Return uniqueness ratio
        return 1.0 - (shared_letters / total_letters) if total_letters > 0 else 0.0

    def _get_limited_candidates(
        self,
        possible_words: List[str],
        common_words: List[str],
        max_candidates: int = 50,
    ) -> List[str]:
        """Get a limited set of candidates for evaluation."""
        # Include possible words (limited)
        candidates = possible_words[: max_candidates // 2]

        # Add common words not already included
        existing_candidates = set(candidates)
        additional_common = [
            word for word in common_words if word not in existing_candidates
        ][: max_candidates // 2]

        return candidates + additional_common

    def _sort_by_weighted_score(
        self,
        words: List[str],
        common_words: List[str],
        word_manager: Optional["WordManager"] = None,
        stateless_word_manager: Optional["StatelessWordManager"] = None,
        prefer_common: bool = True,
    ) -> List[str]:
        """Sort words by weighted score, optionally prioritizing common words."""
        # Calculate weighted scores for all words
        word_scores = self._calculate_weighted_scores(
            words, words, [], word_manager, stateless_word_manager
        )

        if not prefer_common:
            return sorted(words, key=lambda w: word_scores.get(w, 0.0), reverse=True)

        # Separate common and other words, sort each by score
        common_set = set(common_words)
        common_words_filtered = [w for w in words if w in common_set]
        other_words = [w for w in words if w not in common_set]

        common_sorted = sorted(
            common_words_filtered, key=lambda w: word_scores.get(w, 0.0), reverse=True
        )
        other_sorted = sorted(
            other_words, key=lambda w: word_scores.get(w, 0.0), reverse=True
        )

        return common_sorted + other_sorted

    def _balance_common_and_other(
        self, candidates: List[str], common_words: List[str], count: int
    ) -> List[str]:
        """Balance common and other words in final suggestions."""
        common_set = set(common_words)
        common_candidates = [w for w in candidates if w in common_set]
        other_candidates = [w for w in candidates if w not in common_set]

        # For weighted gain strategy, prefer 65% common words
        common_target = max(1, int(count * 0.65))
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
