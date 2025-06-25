# src/modules/backend/solver/two_step_strategy.py
"""
Two-step look-ahead solver strategy for Wordle that optimizes for future moves.
"""
import math
from collections import defaultdict
from typing import Dict, List, Tuple

from ...logging_utils import log_method
from .entropy_strategy import EntropyStrategy
from .solver_strategy import SolverStrategy
from .solver_utils import calculate_pattern


class TwoStepStrategy(SolverStrategy):
    """
    Strategy that uses a two-step look-ahead approach to optimize word choices.

    This strategy evaluates not just the current guess, but also considers
    how effective the next guess would be in various scenarios. It optimizes
    for the expected number of words remaining after two guesses.
    """

    def __init__(self, max_patterns_to_evaluate: int = 10):
        """
        Initialize the two-step strategy.

        Args:
            max_patterns_to_evaluate: Maximum number of resulting patterns to evaluate
                for the second step to limit computational complexity
        """
        self.max_patterns_to_evaluate = max_patterns_to_evaluate
        # Using EntropyStrategy as the base for the second step evaluation
        self.second_step_strategy = EntropyStrategy()

    @log_method("DEBUG")
    def get_top_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: List[Tuple[str, str]],
        count: int = 10,
    ) -> List[str]:
        """Get top N suggestions based on two-step look-ahead strategy."""
        if not possible_words:
            return []

        if len(possible_words) <= count:
            # If we have few words left, prioritize common ones first
            common_possible = [w for w in possible_words if w in common_words]
            other_possible = [w for w in possible_words if w not in common_words]
            return common_possible + other_possible

        # For the first guess, use predefined strong starters instead of computing
        # (computing two steps ahead for many words is very expensive)
        if not guesses_so_far:
            return self._get_good_starters(possible_words, common_words, count)

        # For very small word lists, just return them all sorted by commonness
        if len(possible_words) <= 2:
            common_possible = [w for w in possible_words if w in common_words]
            other_possible = [w for w in possible_words if w not in common_words]
            return common_possible + other_possible

        # If we're down to very few words, use entropy for final guess
        if len(possible_words) <= 5:
            return self.second_step_strategy.get_top_suggestions(
                possible_words, common_words, guesses_so_far, count
            )

        # Calculate two-step look-ahead scores for a limited set of candidates
        # to make computation feasible
        candidates = self._select_candidates_to_evaluate(possible_words, common_words)

        # Score each candidate based on expected performance after two guesses
        word_scores = {}
        for word in candidates:
            word_scores[word] = self._calculate_two_step_score(word, possible_words, common_words)

        # Sort by score (highest score first, which means lowest expected words remaining)
        sorted_words = [word for word, score in sorted(word_scores.items(), key=lambda x: x[1], reverse=True)]

        # Prioritize common words in the results
        common_matches = []
        other_matches = []

        for word in sorted_words:
            if word in common_words:
                common_matches.append(word)
            else:
                other_matches.append(word)

        # Combine with balanced distribution
        result = []
        common_to_include = min(len(common_matches), max(count // 2, 1))
        result.extend(common_matches[:common_to_include])
        result.extend(other_matches[: count - len(result)])

        return result[:count]

    @log_method("DEBUG")
    def _select_candidates_to_evaluate(self, possible_words: List[str], common_words: List[str]) -> List[str]:
        """Select a subset of words to evaluate to make computation feasible."""
        candidates = []

        # Always include all possible words if they're few enough
        if len(possible_words) <= 50:
            candidates.extend(possible_words)
        else:
            # Otherwise, include a sample of possible words (prioritizing common ones)
            common_possible = [w for w in possible_words if w in common_words]
            other_possible = [w for w in possible_words if w not in common_words]

            # Take up to 25 common possible words
            candidates.extend(common_possible[:25])

            # Take up to 25 other possible words
            candidates.extend(other_possible[:25])

            # Ensure we don't have duplicates
            candidates = list(set(candidates))

        return candidates

    @log_method("DEBUG")
    def _calculate_two_step_score(
        self, candidate: str, possible_answers: List[str], common_words: List[str]
    ) -> float:
        """
        Calculate the two-step look-ahead score for a candidate word.

        The score represents the expected (average) effectiveness after two guesses,
        where effectiveness is measured by the inverse of the number of words remaining.
        A higher score is better.
        """
        if not possible_answers:
            return 0.0

        # Group possible answers by the pattern they would give for the candidate
        pattern_groups = self._group_by_pattern(candidate, possible_answers)

        # Calculate the weighted average score across all possible patterns
        total_words = len(possible_answers)
        weighted_score = 0.0

        # Only evaluate the most likely patterns to save computation
        patterns_to_evaluate = sorted(pattern_groups.items(), key=lambda x: len(x[1]), reverse=True)[
            : self.max_patterns_to_evaluate
        ]

        for _pattern, words in patterns_to_evaluate:
            pattern_probability = len(words) / total_words

            # The score for this pattern is based on the best next guess
            # We invert the number of remaining words, so a smaller remaining set gives a higher score
            pattern_score = self._evaluate_second_step(words, common_words)
            weighted_score += pattern_probability * pattern_score

        return weighted_score

    @log_method("DEBUG")
    def _evaluate_second_step(self, remaining_words: List[str], common_words: List[str]) -> float:
        """
        Evaluate the expected performance of the second step.

        Returns a score based on how well the best next guess would perform.
        Higher score is better (fewer words expected to remain).
        """
        if not remaining_words:
            return 1.0  # Perfect score if no words remain (we've found the answer)

        if len(remaining_words) == 1:
            return 1.0  # Perfect score if only one word remains

        # Use entropy to determine the best next guess
        candidates = remaining_words[: min(len(remaining_words), 25)]  # Limit candidates for efficiency

        best_entropy = 0.0
        for word in candidates:
            # Use the group by pattern function to determine how this word would partition the remaining words
            groups = self._group_by_pattern(word, remaining_words)

            # Calculate entropy based on these groups
            entropy = self._calculate_entropy_from_groups(groups, len(remaining_words))
            best_entropy = max(best_entropy, entropy)

        # Higher entropy means better partitioning, which means fewer words expected to remain
        # We normalize it to be between 0 and 1, where 1 is perfect partitioning
        return min(best_entropy / 5.0, 1.0)  # 5.0 bits of entropy is considered very good

    @log_method("DEBUG")
    def _calculate_entropy_from_groups(self, groups: Dict[str, List[str]], total_words: int) -> float:
        """
        Calculate entropy from word groups.

        Higher entropy means better information gain (better word partitioning).
        """
        entropy = 0.0
        for words in groups.values():
            probability = len(words) / total_words
            # Shannon entropy formula
            entropy -= probability * (math.log2(probability) if probability > 0 else 0)
        return entropy

    @log_method("DEBUG")
    def _group_by_pattern(self, candidate: str, possible_answers: List[str]) -> Dict[str, List[str]]:
        """Group possible answers by the pattern they would give for the candidate."""
        pattern_groups = defaultdict(list)

        for answer in possible_answers:
            pattern = calculate_pattern(candidate, answer)
            pattern_groups[pattern].append(answer)

        return pattern_groups

    @log_method("DEBUG")
    def _get_good_starters(self, possible_words: List[str], common_words: List[str], count: int) -> List[str]:
        """Return good starting words based on predefined choices."""
        # Strong starting words based on information theory and entropy
        starters = ["SOARE", "ROATE", "RAISE", "CRANE", "SLATE", "TRACE", "ADIEU", "AUDIO"]

        # Filter out any starters that aren't in our dictionary
        valid_starters = [w for w in starters if w in possible_words]

        # If we have enough valid starters, return those
        if len(valid_starters) >= count:
            return valid_starters[:count]

        # Add high information words from common words
        entropy_strategy = EntropyStrategy()
        remaining_count = count - len(valid_starters)

        # Get additional suggestions from entropy strategy
        additional_suggestions = entropy_strategy.get_top_suggestions(
            [w for w in possible_words if w not in valid_starters],
            common_words,
            [],  # No guesses so far
            remaining_count,
        )

        # Combine starters with additional suggestions
        valid_starters.extend(additional_suggestions)
        return valid_starters[:count]
