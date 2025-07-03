"""
Regression tests for the StatelessMinimaxStrategy to catch specific bugs.
"""

import unittest
from typing import List

from src.modules.backend.solver.stateless_minimax_strategy import (
    StatelessMinimaxStrategy,
)


class TestMinimaxStrategyRegression(unittest.TestCase):
    """Regression tests to prevent previously fixed bugs from reappearing."""

    def setUp(self) -> None:
        """Set up the test environment."""
        self.strategy = StatelessMinimaxStrategy()

    def test_get_good_starters_no_undefined_variables(self) -> None:
        """Test that _get_good_starters doesn't use undefined variables."""
        # Sample word lists for testing
        possible_words: List[str] = [
            "CRANE",
            "SLATE",
            "STARE",
            "ROATE",
            "RAISE",
            "SOARE",
            "CARET",
            "TRACE",
            "ADIEU",
            "AUDIO",
        ]
        common_words: List[str] = [
            "SOARE",
            "CRANE",
            "STARE",
            "TRACE",
            "SLATE",
            "OTHER",
            "EXTRA",
            "HELLO",
            "WORLD",
            "GUESS",
        ]
        count = 5

        # Call the method
        result = self.strategy._get_good_starters(possible_words, common_words, count)

        # Verify basic functionality
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), count)
        self.assertGreater(len(result), 0)

        # Verify that at least one predefined starter was included
        self.assertTrue(
            any(word in ["SLATE", "CRANE", "ADIEU", "AUDIO"] for word in result)
        )

        # Test with no predefined starters in possible_words
        unique_words: List[str] = ["UNIQUE", "WORDS", "NEVER", "MATCH", "STARTERS"]
        result2 = self.strategy._get_good_starters(unique_words, common_words, count)

        # It should return some words (up to count) without raising exceptions
        self.assertIsInstance(result2, list)
        self.assertLessEqual(len(result2), count)

        # Test with empty common_words
        result3 = self.strategy._get_good_starters(possible_words, [], count)

        # Should still return predefined starters without error
        self.assertIsInstance(result3, list)
        self.assertGreater(len(result3), 0)

        # Test with count=1 (edge case)
        result4 = self.strategy._get_good_starters(possible_words, common_words, 1)

        # Should return exactly one word
        self.assertEqual(len(result4), 1)

    def test_get_optimized_candidates_integration(self) -> None:
        """Integration test between _get_good_starters and _get_optimized_candidates."""
        possible_words: List[str] = [
            "CRANE",
            "SLATE",
            "STARE",
            "ROATE",
            "RAISE",
            "SOARE",
            "CARET",
            "TRACE",
            "ADIEU",
            "AUDIO",
            "EXTRA",
            "HELLO",
            "WORLD",
            "GUESS",
            "TESTS",
        ]
        common_words: List[str] = [
            "CRANE",
            "SLATE",
            "STARE",
            "TRACE",
            "SOARE",
            "OTHER",
            "EXTRA",
            "HELLO",
            "WORLD",
            "GUESS",
        ]

        # First call _get_optimized_candidates which defines 'candidates' variable
        candidates = self.strategy._get_optimized_candidates(
            possible_words, common_words
        )
        self.assertIsInstance(candidates, list)

        # Now call _get_good_starters which should not reference 'candidates' variable
        starters = self.strategy._get_good_starters(possible_words, common_words, 5)
        self.assertIsInstance(starters, list)

        # Both methods should work independently without sharing variable scope
        self.assertGreater(len(candidates), 0)
        self.assertGreater(len(starters), 0)


if __name__ == "__main__":
    unittest.main()
