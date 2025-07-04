# src/tests/test_game_sequence.py
"""
Integration test for a specific game sequence.
Tests the sequence:
1. SOARE BBBYB
2. PURIN BYGBB
3. THRUM GGGGG
"""
import unittest

from src.frontend.cli.game_state_manager import GameStateManager
from src.modules.backend.game_engine import GameEngine
from src.modules.backend.stateless_word_manager import StatelessWordManager


class TestGameSequence(unittest.TestCase):
    """Test a specific game sequence to ensure it leads to a successful game."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a stateless word manager for the game state manager
        self.word_manager = StatelessWordManager()
        self.word_manager._is_test_mode = True

        # Create a game state manager
        self.solver = GameStateManager(self.word_manager)

        # Create a game engine with its own internal WordManager
        self.game_engine = GameEngine()

        # Enable test mode on the internal word manager
        self.game_engine.word_manager._is_test_mode = True

        # The specific sequence we're testing
        self.test_sequence = [
            ("SOARE", "BBBYB"),
            ("PURIN", "BYGBB"),
            ("THRUM", "GGGGG"),
        ]

    def test_successful_game_sequence(self):
        """Test that the specified sequence leads to a successful game."""
        # Make sure THRUM is in the word list - for stateless implementation
        # we check this differently
        self.assertTrue(
            self.word_manager.is_valid_word("THRUM"),
            "Test word 'THRUM' must be in the word list",
        )

        # Reset the solver to start a new game
        self.solver.reset()

        # Apply each guess and result in sequence
        for guess, result in self.test_sequence:
            self.solver.add_guess(guess, result)

        # Verify that the final state is a won game
        self.assertTrue(
            self.solver.is_game_won(), "Game should be won after the sequence"
        )

        # With stateless implementation, we need to get possible words from the game state manager
        # not directly from the word manager
        possible_words = self.solver.get_possible_words()

        self.assertIn(
            "THRUM",
            possible_words,
            "THRUM should be in the possible words after filtering",
        )

        # Ideally there should only be one possible word left
        self.assertEqual(
            len(possible_words), 1, "There should be exactly one possible word left"
        )

    def test_game_engine_with_target_word(self):
        """Test the same sequence against the game engine with THRUM as target."""
        # Set up a new game and manually set the target word to THRUM
        self.game_engine.start_new_game()
        self.game_engine.target_word = "THRUM"

        # Verify the target word is set correctly
        self.assertEqual(self.game_engine.target_word, "THRUM")

        # Play the sequence
        won = False
        for i, (guess, expected_result) in enumerate(self.test_sequence):
            result, is_solved = self.game_engine.make_guess(guess)

            # Verify the result matches expected
            self.assertEqual(
                result,
                expected_result,
                f"Result for guess {i+1} ({guess}) should be {expected_result}",
            )

            # Check if we won on this guess
            if is_solved:
                won = True
                break

        # Verify we won the game
        self.assertTrue(won, "Game should be won after the sequence")
        self.assertTrue(self.game_engine.is_game_won(), "Game should report as won")
        self.assertEqual(
            len(self.game_engine.guesses), 3, "Game should have 3 guesses recorded"
        )


if __name__ == "__main__":
    unittest.main()
