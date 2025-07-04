# src/tests/test_game_history.py
"""
Test the game history and retrieval by game ID functionality.
"""
import os
import unittest
from typing import List

from src.modules.backend.game_engine import GameEngine
from src.modules.backend.stats_manager import StatsManager


class TestGameHistory(unittest.TestCase):
    """Test game history storage and retrieval."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test-specific history file to avoid affecting real game data
        self.test_history_file = "test_game_history.json"

        # Remove test file if it exists from previous test runs
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)

        # Create a game engine
        self.game_engine = GameEngine()  # GameEngine now creates its own WordManager

        # Temporarily mock the internal WordManager for testing
        self.game_engine.word_manager._is_test_mode = True

        # Create a stats manager with test file (no longer needs stats_file)
        self.stats_manager = StatsManager(history_file=self.test_history_file)

        # Replace the game engine's stats manager with our test one
        self.game_engine.stats_manager = self.stats_manager

    def tearDown(self):
        """Clean up after tests."""
        # Remove test file
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)

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
        self.record_game(
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

        self.record_game(guesses1, True, 3, game_id=game1_id, target_word="THRUM")

        # Game 2: Lost game with target FEAST
        self.game_engine.start_new_game()
        self.game_engine.target_word = "FEAST"
        game2_id = self.game_engine.game_id

        guesses2 = []
        for guess in ["AUDIO", "CRANE", "STAMP", "BLAST", "STEAM", "CHEST"]:
            result, _ = self.game_engine.make_guess(guess)
            guesses2.append([guess, result])

        self.record_game(guesses2, False, 6, game_id=game2_id, target_word="FEAST")

        # Test search by game ID
        games_by_id = self.stats_manager.search_games(game_id=game1_id)
        self.assertGreater(
            len(games_by_id), 0, "Should find at least one game with the ID"
        )

        # Verify that at least one of the found games has the correct ID
        found_matching_game = False
        for game in games_by_id:
            if game.get("game_id") == game1_id:
                found_matching_game = True
                break

        self.assertTrue(found_matching_game, "Should find game with correct ID")

        # Test search by outcome
        won_games = self.stats_manager.search_games(won=True)
        lost_games = self.stats_manager.search_games(won=False)

        # Verify we can find games by outcome, without requiring exact counts
        self.assertGreater(len(won_games), 0, "Should find at least one won game")
        self.assertGreater(len(lost_games), 0, "Should find at least one lost game")

        # Verify our specific games are in the results
        won_game_ids = [game.get("game_id") for game in won_games]
        lost_game_ids = [game.get("game_id") for game in lost_games]

        self.assertIn(game1_id, won_game_ids, "Should find our won game")
        self.assertIn(game2_id, lost_game_ids, "Should find our lost game")

        # Test search by target word
        thrum_games = self.stats_manager.search_games(target_word="THRUM")
        self.assertGreater(
            len(thrum_games), 0, "Should find at least one game with target THRUM"
        )
        thrum_game_ids = [game.get("game_id") for game in thrum_games]
        self.assertIn(game1_id, thrum_game_ids, "Should find our THRUM game")

        # Test search by max attempts
        quick_games = self.stats_manager.search_games(max_attempts=3)
        self.assertGreater(
            len(quick_games),
            0,
            "Should find at least one game with 3 or fewer attempts",
        )
        quick_game_ids = [game.get("game_id") for game in quick_games]
        self.assertIn(game1_id, quick_game_ids, "Should find our quick game")

    def test_dynamic_stats_calculation(self):
        """Test that statistics are calculated dynamically from game history."""
        # Initially, stats should be empty
        stats = self.stats_manager.get_stats()
        self.assertEqual(stats["games_played"], 0)
        self.assertEqual(stats["games_won"], 0)
        self.assertEqual(stats["win_rate"], 0.0)
        self.assertEqual(stats["avg_attempts"], 0.0)

        # Record a winning game
        self.record_game(
            [["SOARE", "GGGGG"]],
            True,
            1,
            game_id="TEST01",
            target_word="SOARE",
            mode="manual",
        )

        # Check stats after one winning game
        stats = self.stats_manager.get_stats()
        self.assertEqual(stats["games_played"], 1)
        self.assertEqual(stats["games_won"], 1)
        self.assertEqual(stats["win_rate"], 100.0)
        self.assertEqual(stats["avg_attempts"], 1.0)

        # Record a losing game
        self.record_game(
            [["WRONG", "BBBBB"], ["GUESS", "BBBBB"]],
            False,
            2,
            game_id="TEST02",
            target_word="EXACT",
            mode="solver",
        )

        # Check stats after one win and one loss
        stats = self.stats_manager.get_stats()
        self.assertEqual(stats["games_played"], 2)
        self.assertEqual(stats["games_won"], 1)
        self.assertEqual(stats["win_rate"], 50.0)
        self.assertEqual(stats["avg_attempts"], 1.0)  # Only counts winning games

        # Record another winning game with more attempts
        self.record_game(
            [["FIRST", "BBBBB"], ["SECOND", "BYBBB"], ["THIRD", "GGGGG"]],
            True,
            3,
            game_id="TEST03",
            target_word="THIRD",
            mode="manual",
        )

        # Check final stats
        stats = self.stats_manager.get_stats()
        self.assertEqual(stats["games_played"], 3)
        self.assertEqual(stats["games_won"], 2)
        # Use assertAlmostEqual for floating point comparison (2/3 * 100 = 66.666...)
        self.assertAlmostEqual(stats["win_rate"], 66.66666666666667, places=10)
        self.assertEqual(stats["avg_attempts"], 2.0)  # (1 + 3) / 2

    def test_clear_all_history(self):
        """Test clearing all game history."""
        # Add some games first
        self.record_game(
            [["FIRST", "GGGGG"]],
            True,
            1,
            game_id="TEST01",
            target_word="FIRST",
            mode="manual",
        )
        self.record_game(
            [["SECOND", "GGGGG"]],
            True,
            1,
            game_id="TEST02",
            target_word="SECOND",
            mode="solver",
        )

        # Verify games were added
        self.assertTrue(self.stats_manager.has_history())
        self.assertEqual(self.stats_manager.get_history_count(), 2)

        # Clear all history
        success = self.stats_manager.clear_all_history()
        self.assertTrue(success)

        # Verify history is cleared
        self.assertFalse(self.stats_manager.has_history())
        self.assertEqual(self.stats_manager.get_history_count(), 0)
        self.assertEqual(len(self.stats_manager.get_history()), 0)

        # Verify stats are reset
        stats = self.stats_manager.get_stats()
        self.assertEqual(stats["games_played"], 0)
        self.assertEqual(stats["games_won"], 0)
        self.assertEqual(stats["win_rate"], 0.0)
        self.assertEqual(stats["avg_attempts"], 0.0)

    def test_has_history_and_get_history_count(self):
        """Test helper methods for checking history status."""
        # Initially no history
        self.assertFalse(self.stats_manager.has_history())
        self.assertEqual(self.stats_manager.get_history_count(), 0)

        # Add one game
        self.record_game(
            [["TEST", "GGGGG"]],
            True,
            1,
            game_id="TEST01",
            target_word="TEST",
            mode="manual",
        )

        # Should now have history
        self.assertTrue(self.stats_manager.has_history())
        self.assertEqual(self.stats_manager.get_history_count(), 1)

        # Add another game
        self.record_game(
            [["AGAIN", "GGGGG"]],
            True,
            1,
            game_id="TEST02",
            target_word="AGAIN",
            mode="solver",
        )

        # Should have 2 games
        self.assertTrue(self.stats_manager.has_history())
        self.assertEqual(self.stats_manager.get_history_count(), 2)

    def test_record_game_with_mode(self):
        """Test that game mode is properly recorded."""
        # Record a manual mode game
        self.record_game(
            [["MANUAL", "GGGGG"]],
            True,
            1,
            game_id="TEST01",
            target_word="MANUAL",
            mode="manual",
        )

        # Record a solver mode game
        self.record_game(
            [["SOLVER", "GGGGG"]],
            True,
            1,
            game_id="TEST02",
            target_word="SOLVER",
            mode="solver",
        )

        # Verify modes are stored correctly
        manual_game = self.stats_manager.get_game_by_id("TEST01")
        solver_game = self.stats_manager.get_game_by_id("TEST02")

        self.assertIsNotNone(manual_game)
        self.assertIsNotNone(solver_game)
        self.assertEqual(manual_game["mode"], "manual")
        self.assertEqual(solver_game["mode"], "solver")

    def test_record_game_default_mode(self):
        """Test that default mode is 'manual' when not specified."""
        self.record_game(
            [["DEFAULT", "GGGGG"]], True, 1, game_id="TEST01", target_word="DEFAULT"
        )

        game = self.stats_manager.get_game_by_id("TEST01")
        self.assertIsNotNone(game)
        self.assertEqual(game["mode"], "manual")

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


if __name__ == "__main__":
    unittest.main()
