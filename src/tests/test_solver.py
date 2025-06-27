# src/tests/test_solver.py
"""
Unit tests for the Solver class.
"""
import unittest
from unittest.mock import Mock

from src.modules.backend.game_state_manager import GameStateManager
from src.modules.backend.result_color import ResultColor
from src.modules.backend.word_manager import WordManager


class TestSolver(unittest.TestCase):
    """Test cases for Solver."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock WordManager
        self.word_manager = Mock(spec=WordManager)

        # Configure the mock with proper return values
        self.word_manager.get_possible_words.return_value = [
            "CREAM",
            "BREAD",
            "CLEAR",
            "DESERT",
            "DREAM",
        ]
        self.word_manager.get_common_possible_words.return_value = ["CREAM", "BREAD"]

        # Mock frequency method to return integers instead of Mock objects
        self.word_manager.get_word_frequency.return_value = 1000
        self.word_manager.get_word_entropy.return_value = 2.5

        # Create solver instance with mock word manager
        self.solver = GameStateManager(self.word_manager)

    def test_add_guess(self):
        """Test adding a guess and result."""
        result_pattern = (
            ResultColor.GREEN.value
            + ResultColor.YELLOW.value
            + ResultColor.BLACK.value
            + ResultColor.YELLOW.value
            + ResultColor.BLACK.value
        )  # "GYBYB"
        self.solver.add_guess("BREAD", result_pattern)

        # Check that the guess was added to history
        self.assertEqual(len(self.solver.guesses), 1)
        self.assertEqual(self.solver.guesses[0], ("BREAD", result_pattern))

        # Check that filter_words was called on the word manager
        self.word_manager.filter_words.assert_called_once_with("BREAD", result_pattern)

    def test_suggest_next_guess(self):
        """Test suggesting the next guess."""
        result = self.solver.suggest_next_guess()

        # Should suggest a word from the possible words
        self.assertIn(result, self.word_manager.get_possible_words())

    def test_get_top_suggestions(self):
        """Test getting top suggestions."""
        suggestions = self.solver.get_top_suggestions(3)

        # Should return up to 3 suggestions
        self.assertTrue(len(suggestions) <= 3)

        # All suggestions should be in the possible words
        for suggestion in suggestions:
            self.assertIn(suggestion, self.word_manager.get_possible_words())

        # Common words should be prioritized
        if len(suggestions) >= 2:
            self.assertIn(suggestions[0], self.word_manager.get_common_possible_words())

    def test_reset(self):
        """Test resetting the solver."""
        result_pattern = (
            ResultColor.GREEN.value
            + ResultColor.YELLOW.value
            + ResultColor.BLACK.value
            + ResultColor.YELLOW.value
            + ResultColor.BLACK.value
        )  # "GYBYB"
        self.solver.add_guess("BREAD", result_pattern)
        self.assertEqual(len(self.solver.guesses), 1)

        self.solver.reset()

        # Guesses should be cleared
        self.assertEqual(len(self.solver.guesses), 0)

        # Word manager should be reset
        self.word_manager.reset.assert_called_once()

    def test_is_game_won(self):
        """Test checking if the game is won."""
        self.assertFalse(self.solver.is_game_won())

        all_green = ResultColor.GREEN.value * 5  # "GGGGG"
        self.solver.add_guess("BREAD", all_green)
        self.assertTrue(self.solver.is_game_won())

    def test_is_game_over(self):
        """Test checking if the game is over."""
        self.assertFalse(self.solver.is_game_over())

        # Game is over when won
        all_green = ResultColor.GREEN.value * 5  # "GGGGG"
        self.solver.add_guess("BREAD", all_green)
        self.assertTrue(self.solver.is_game_over())

        # Game is over when max guesses reached
        self.solver.reset()
        result_pattern = (
            ResultColor.GREEN.value
            + ResultColor.YELLOW.value
            + ResultColor.BLACK.value
            + ResultColor.BLACK.value
            + ResultColor.BLACK.value
        )  # "GYBBB"
        for _ in range(6):
            self.solver.add_guess("BREAD", result_pattern)
        self.assertTrue(self.solver.is_game_over())


if __name__ == "__main__":
    unittest.main()
