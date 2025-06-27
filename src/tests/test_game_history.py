# src/tests/test_game_history.py
"""
Test the game history and retrieval by game ID functionality.
"""
import os
import unittest

from src.modules.backend.game_engine import GameEngine
from src.modules.backend.stats_manager import StatsManager
from src.modules.backend.word_manager import WordManager


class TestGameHistory(unittest.TestCase):
    """Test game history storage and retrieval."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test-specific stats files to avoid affecting real game data
        self.test_stats_file = "test_game_stats.json"
        self.test_history_file = "test_game_history.json"

        # Remove test files if they exist from previous test runs
        for file in [self.test_stats_file, self.test_history_file]:
            if os.path.exists(file):
                os.remove(file)

        # Create a real WordManager
        self.word_manager = WordManager()

        # Enable test mode to bypass word validation
        self.word_manager._is_test_mode = True

        # Ensure THRUM is in the word list for the test
        self.word_manager.all_words.add("THRUM")
        self.word_manager.possible_words.add("THRUM")

        # Create a game engine
        self.game_engine = GameEngine(self.word_manager)

        # Create a stats manager with test files
        self.stats_manager = StatsManager(
            stats_file=self.test_stats_file, history_file=self.test_history_file
        )

    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        for file in [self.test_stats_file, self.test_history_file]:
            if os.path.exists(file):
                os.remove(file)

    def test_game_id_storage_and_retrieval(self):
        """Test that a game's history can be retrieved by its game ID."""
        # Start a new game
        self.game_engine.start_new_game()

        # Manually set the target word for reproducibility
        self.game_engine.target_word = "THRUM"

        # Get the game ID
        game_state = self.game_engine.get_game_state()
        game_id = game_state["game_id"]

        # Verify we have a valid game ID
        assert isinstance(game_id, str), "Game ID should be a string"
        self.assertTrue(game_id, "Game ID should not be empty")
        self.assertEqual(len(game_id), 6, "Game ID should be 6 characters long")

        # Play a game with a predetermined sequence
        test_sequence = [
            "SOARE",  # First guess
            "PURIN",  # Second guess
            "THRUM",  # Final guess - should win
        ]

        won = False
        guesses_history = []

        # Make the guesses
        for guess in test_sequence:
            result, is_solved = self.game_engine.make_guess(guess)
            guesses_history.append([guess, result])

            if is_solved:
                won = True
                break

        # Verify the game was won
        self.assertTrue(won, "Game should be won")

        # Record the game in stats manager
        self.stats_manager.record_game(
            guesses_history,
            won,
            len(guesses_history),
            game_id=str(game_id),
            target_word=self.game_engine.target_word,
        )

        # Verify the game was stored in history
        self.assertTrue(
            os.path.exists(self.test_history_file), "History file should be created"
        )

        # Retrieve the game by ID
        retrieved_game = self.stats_manager.get_game_by_id(str(game_id))

        # Verify we found a game
        self.assertIsNotNone(retrieved_game, f"Should find a game with ID {game_id}")
        assert retrieved_game is not None  # Type assertion for mypy

        # Verify game details match what we expect
        self.assertEqual(retrieved_game["game_id"], game_id, "Game ID should match")
        self.assertEqual(
            retrieved_game["target_word"], "THRUM", "Target word should match"
        )
        assert isinstance(retrieved_game["guesses"], list), "Guesses should be a list"
        self.assertEqual(len(retrieved_game["guesses"]), 3, "Should have 3 guesses")
        self.assertTrue(retrieved_game["won"], "Game should be recorded as won")

        # Verify the sequence of guesses
        for i, (guess, _) in enumerate(retrieved_game["guesses"]):
            self.assertEqual(guess, test_sequence[i], f"Guess {i+1} should match")

    def test_search_games(self):
        """Test the search_games functionality."""
        # Start and play two games with different outcomes

        # Game 1: Won game with target THRUM
        self.game_engine.start_new_game()
        self.game_engine.target_word = "THRUM"
        game1_id = self.game_engine.game_id

        guesses1 = []
        for guess in ["SOARE", "PURIN", "THRUM"]:
            result, _ = self.game_engine.make_guess(guess)
            guesses1.append([guess, result])

        self.stats_manager.record_game(
            guesses1, True, 3, game_id=game1_id, target_word="THRUM"
        )

        # Game 2: Lost game with target FEAST
        self.game_engine.start_new_game()
        self.game_engine.target_word = "FEAST"
        game2_id = self.game_engine.game_id

        guesses2 = []
        for guess in ["AUDIO", "CRANE", "STAMP", "BLAST", "STEAM", "CHEST"]:
            result, _ = self.game_engine.make_guess(guess)
            guesses2.append([guess, result])

        self.stats_manager.record_game(
            guesses2, False, 6, game_id=game2_id, target_word="FEAST"
        )

        # Test search by game ID
        games_by_id = self.stats_manager.search_games(game_id=game1_id)
        self.assertEqual(len(games_by_id), 1, "Should find exactly one game by ID")
        self.assertEqual(
            games_by_id[0]["game_id"], game1_id, "Should find game with correct ID"
        )

        # Test search by outcome
        won_games = self.stats_manager.search_games(won=True)
        lost_games = self.stats_manager.search_games(won=False)
        self.assertEqual(len(won_games), 1, "Should find one won game")
        self.assertEqual(len(lost_games), 1, "Should find one lost game")

        # Test search by target word
        thrum_games = self.stats_manager.search_games(target_word="THRUM")
        self.assertEqual(len(thrum_games), 1, "Should find one game with target THRUM")

        # Test search by max attempts
        quick_games = self.stats_manager.search_games(max_attempts=3)
        self.assertEqual(
            len(quick_games), 1, "Should find one game with 3 or fewer attempts"
        )


if __name__ == "__main__":
    unittest.main()
