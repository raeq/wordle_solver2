# src/tests/test_game_id_validation.py
"""
Tests specifically focused on ensuring game IDs are properly generated, validated, and stored.
This test file was created to address a regression where games were being stored without proper IDs.
"""

import unittest
from typing import List

from ..modules.backend.game_engine import GameEngine
from ..modules.backend.stats_manager import StatsManager


class TestGameIDValidation(unittest.TestCase):
    """Test cases for game ID generation, validation and storage."""

    def setUp(self):
        """Set up test fixtures."""
        # Create stats manager with in-memory storage
        self.stats_manager = StatsManager(history_file=":memory:")

        # Ensure each test starts with a clean history
        self.stats_manager.history = []

        # Create game engine with its own internal WordManager
        self.game_engine = GameEngine()

        # Configure the game engine's word manager for testing
        self.game_engine.word_manager._is_test_mode = True

        # Replace the game engine's stats manager with our test one
        self.game_engine.stats_manager = self.stats_manager

        # Sample game data
        self.sample_guesses = [["AUDIO", "BBBBY"], ["HELLO", "BGGGG"]]

    def record_game(
        self,
        guesses: List[List[str]],
        won: bool,
        attempts: int,
        game_id: str = "",
        target_word: str = "",
        mode: str = "manual",
    ) -> None:
        """
        Test helper method to record a game in the stats manager.

        This exists only for testing purposes to maintain compatibility with existing tests
        while preserving the architectural decision that only the game engine should
        call record_game in production code.
        """
        self.stats_manager._record_game(
            guesses, won, attempts, game_id=game_id, target_word=target_word, mode=mode
        )

    def test_empty_game_id_raises_error(self):
        """Test that StatsManager rejects empty game IDs."""
        with self.assertRaises(ValueError) as context:
            self.record_game(
                self.sample_guesses,
                won=True,
                attempts=2,
                game_id="",  # Empty game ID
                target_word="HELLO",
                mode="manual",
            )

        self.assertIn("Missing game ID", str(context.exception))

    def test_game_engine_always_generates_id(self):
        """Test that GameEngine always generates a game ID when starting a new game."""
        # Start a new game and verify ID is generated
        self.game_engine.start_new_game()

        # Get the game ID and verify it's not empty
        game_id = self.game_engine.game_id
        self.assertTrue(game_id, "Game ID should not be empty")
        self.assertEqual(len(game_id), 6, "Game ID should be 6 characters")

        # Get the game state and verify ID is included
        game_state = self.game_engine.get_game_state()
        self.assertEqual(
            game_state["game_id"], game_id, "Game ID should be in game state"
        )

    def test_record_game_receives_game_id(self):
        """Test that GameEngine passes a valid game ID when recording games."""
        # Start a game
        self.game_engine.start_new_game()
        self.game_engine.target_word = "TESTS"  # Set fixed target for testing

        # Store the game ID to check later
        game_id = self.game_engine.game_id

        # Ensure game ID is valid
        self.assertTrue(game_id, "Game ID should be generated")
        self.assertEqual(len(game_id), 6, "Game ID should be 6 characters")

        # Make a winning guess - this should trigger the game engine to record the game
        result, is_solved = self.game_engine.make_guess("TESTS")

        # Verify the game was recorded properly
        self.assertTrue(is_solved, "Game should be solved")
        self.assertEqual(len(self.stats_manager.history), 1, "Game should be recorded")

        # Check that the recorded game has the correct ID
        recorded_game = self.stats_manager.history[0]
        self.assertEqual(
            recorded_game["game_id"],
            game_id,
            "Game should be recorded with the correct ID",
        )

    def test_manual_mode_game_id_generation(self):
        """Test that manual mode games also generate proper game IDs."""
        # This simulates how enhanced_app.py records manual games
        self.game_engine.start_new_game()
        game_id = self.game_engine.game_id

        # Verify the ID exists
        self.assertTrue(game_id, "Game ID should not be empty")

        # Test recording a manual game
        self.record_game(
            self.sample_guesses,
            won=True,
            attempts=2,
            game_id=game_id,  # Use the engine's game ID
            target_word="HELLO",
            mode="manual",
        )

        # Verify the game was recorded with the ID
        history = self.stats_manager.history
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["game_id"], game_id)

    def test_enhanced_solver_game_id_generation(self):
        """Test that enhanced solver mode games generate proper game IDs."""
        # This simulates how enhanced_app.py might record solver games
        self.game_engine.start_new_game()
        self.game_engine.game_mode = "enhanced_solver"
        game_id = self.game_engine.game_id

        # Make a winning guess that will cause the game to end and be recorded
        self.game_engine.target_word = "TESTS"  # Set fixed target

        # GameEngine should automatically record the game when it's solved
        result, is_solved = self.game_engine.make_guess("TESTS")
        self.assertTrue(is_solved, "Game should be solved with the correct guess")

        # Verify history contains a game with the ID
        history = self.stats_manager.history
        self.assertEqual(len(history), 1, "Game should be recorded in history")
        self.assertEqual(history[0]["game_id"], game_id, "Game ID should match")
        self.assertEqual(
            history[0]["mode"], "enhanced_solver", "Game mode should match"
        )


if __name__ == "__main__":
    unittest.main()
