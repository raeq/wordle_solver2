# src/modules/backend/solver/entropy_strategy.py
"""
Entropy-based solver strategy for Wordle that maximizes information gain.
"""
import math
from collections import defaultdict
from typing import Dict, List, Tuple

from ...logging_utils import log_method
from .solver_strategy import SolverStrategy
from .solver_utils import calculate_pattern


class EntropyStrategy(SolverStrategy):
    """Strategy that uses information theory to maximize information gain."""

    @log_method("DEBUG")
    def get_top_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: List[Tuple[str, str]],
        count: int = 10,
    ) -> List[str]:
        """Get top N suggestions based on entropy (information gain)."""
        if not possible_words:
            return []

        if len(possible_words) <= count:
            # If we have few words left, prioritize common ones first
            common_possible = [w for w in possible_words if w in common_words]
            other_possible = [w for w in possible_words if w not in common_words]
            return common_possible + other_possible

        # For the first guess, use predefined strong starters instead of computing entropy
        if not guesses_so_far:
            return self._get_good_starters(possible_words, common_words, count)

        # Calculate entropy for each possible guess
        all_candidates = possible_words.copy()

        # For efficiency, if there are too many candidates, limit to a reasonable number
        # but ensure we include all possible solutions plus some additional words
        if len(all_candidates) > 1000:
            # Always include all possible matches (possible_words) plus some common words
            additional_candidates = [w for w in common_words if w not in possible_words]

            # Limit the total number of candidates to evaluate
            max_additional = 500 - len(possible_words)
            if max_additional > 0:
                additional_candidates = additional_candidates[:max_additional]

            all_candidates = possible_words + additional_candidates

        # Score all candidates based on entropy
        word_scores = {}
        for word in all_candidates:
            word_scores[word] = self._calculate_entropy(word, possible_words)

        # Sort by score (highest entropy first)
        sorted_words = [word for word, score in sorted(word_scores.items(), key=lambda x: x[1], reverse=True)]

        # Prioritize common words in the results
        common_matches = []
        other_matches = []

        for word in sorted_words:
            if word in common_words:
                common_matches.append(word)
            else:
                other_matches.append(word)

        # If we're in a late game with few possibilities, prioritize possible words
        if len(possible_words) <= 5:
            # In late game, favor words that could be the answer
            possible_matches = [w for w in common_matches + other_matches if w in possible_words]
            other_matches = [w for w in common_matches + other_matches if w not in possible_words]
            return (possible_matches + other_matches)[:count]

        # Combine with balanced distribution - about half should be common words
        result = []
        common_to_include = min(len(common_matches), max(count // 2, 1))

        result.extend(common_matches[:common_to_include])
        result.extend(other_matches[: count - len(result)])

        return result[:count]

    @log_method("DEBUG")
    def _get_good_starters(self, possible_words: List[str], common_words: List[str], count: int) -> List[str]:
        """Return good starting words based on predefined choices and vowel content."""
        # Strong starting words based on high entropy and vowel diversity
        starters = ["ADIEU", "AUDIO", "SOARE", "ROATE", "RAISE", "SLATE", "CRANE", "TRACE"]

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
        vowel_words = [word for word, score in sorted(vowel_scores.items(), key=lambda x: x[1], reverse=True)]

        # Combine starters with vowel-rich words
        valid_starters.extend(vowel_words[: count - len(valid_starters)])
        return valid_starters[:count]

    @log_method("DEBUG")
    def _calculate_entropy(self, candidate: str, possible_answers: List[str]) -> float:
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

        # Calculate entropy using information theory
        total_answers = len(possible_answers)
        entropy = 0.0

        for count in pattern_counts.values():
            probability = count / total_answers
            entropy -= probability * math.log2(probability)  # Shannon entropy formula

        return entropy
