# tests/test_review_integration.py
"""
Integration tests for the complete review feature functionality.
"""
import json
import tempfile
import unittest
from unittest.mock import Mock, patch

from src.frontend.cli_interface import CLIInterface
from src.modules.app import WordleSolverApp
from src.modules.backend.game_history_manager import GameHistoryManager


class TestReviewIntegration(unittest.TestCase):
    """Integration tests for the review feature."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_history_data = [
            {
                "timestamp": "2025-07-01T12:01:54.056006",
                "guesses": [
                    ["AUDIO", "BYBBB", "entropy"],
                    ["CRUEL", "BBYYB", "entropy"],
                    ["ENSUE", "YYBGB", "entropy"],
                    ["BEGUN", "GGGGG", "entropy"],
                ],
                "won": True,
                "attempts": 4,
                "game_id": "CGVWFZ",
                "target_word": "BEGUN",
            },
            {
                "timestamp": "2025-07-01T12:03:22.680855",
                "guesses": [
                    ["AUDIO", "BYYGB", "entropy"],
                    ["FLUID", "GGGGG", "entropy"],
                ],
                "won": True,
                "attempts": 2,
                "game_id": "Z0T6R0",
                "target_word": "FLUID",
            },
        ]

    def test_complete_review_workflow(self):
        """Test the complete review workflow from start to finish."""
        # Create a temporary file with sample game history
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            json.dump(self.sample_history_data, temp_file)
            temp_file_path = temp_file.name

        try:
            # Test GameHistoryManager functionality
            manager = GameHistoryManager(temp_file_path)

            # Load games
            games = manager.load_game_history()
            self.assertEqual(len(games), 2)

            # Format games for display
            formatted_games = [manager.format_game_summary(game) for game in games]
            self.assertEqual(len(formatted_games), 2)
            self.assertEqual(formatted_games[0]["game_id"], "CGVWFZ")
            self.assertEqual(formatted_games[1]["game_id"], "Z0T6R0")

            # Test pagination
            pages = manager.paginate_games(formatted_games, page_size=1)
            self.assertEqual(len(pages), 2)  # Should create 2 pages with 1 game each

            # Test game retrieval by ID
            game = manager.get_game_by_id(games, "CGVWFZ")
            self.assertIsNotNone(game)
            self.assertEqual(game["target_word"], "BEGUN")

            # Test CLI interface formatting
            cli = CLIInterface()

            # Test that colorize result works (used in simulation)
            colored_result = cli._colorize_result("AUDIO", "BYBBB")
            self.assertIsNotNone(colored_result)

        finally:
            import os

            os.unlink(temp_file_path)

    @patch("src.modules.app.get_container")
    @patch("src.modules.app.get_settings")
    def test_app_review_mode_integration(self, mock_settings, mock_container):
        """Test the app's review mode integration."""
        # Mock the container and settings
        mock_container.return_value.get.return_value = Mock()
        mock_settings.return_value = Mock()
        mock_settings.return_value.solver.default_strategy = "entropy"

        # Create app instance
        app = WordleSolverApp()

        # Mock UI component
        mock_ui = Mock()
        app._components["ui"] = mock_ui

        # Test that review mode is correctly handled in get_game_mode
        mock_ui.get_game_mode.return_value = "review"
        mock_ui.ask_play_again.return_value = False
        mock_ui.get_strategy_selection.return_value = None

        # Mock stats manager
        mock_stats = Mock()
        mock_stats.get_stats.return_value = {
            "games_played": 0,
            "games_won": 0,
            "win_rate": 0,
            "avg_attempts": 0,
        }
        app._components["stats_manager"] = mock_stats

        # Mock the review mode to avoid actual file operations
        with patch.object(app, "_run_review_mode") as mock_review:
            app.run()

            # Verify review mode was called
            mock_review.assert_called_once()

    def test_cli_interface_review_methods(self):
        """Test all CLI interface review methods work together."""
        cli = CLIInterface()

        # Sample data for testing
        games_page = [
            {
                "game_id": "CGVWFZ",
                "date": "2025-07-01 12:01",
                "target": "BEGUN",
                "attempts": "4",
                "result": "Won",
            }
        ]

        sample_game = {
            "game_id": "CGVWFZ",
            "timestamp": "2025-07-01T12:01:54.056006",
            "target_word": "BEGUN",
            "won": True,
            "attempts": 4,
            "guesses": [["AUDIO", "BYBBB", "entropy"], ["BEGUN", "GGGGG", "entropy"]],
        }

        # Test display methods don't raise errors
        with patch("rich.console.Console.print"):
            cli.display_review_mode_start()
            cli.display_game_list(games_page, 1, 1)

        with patch("rich.prompt.Prompt.ask", return_value=""):
            with patch("rich.console.Console.print"):
                cli.simulate_game_display(sample_game)

        # Test navigation actions
        with patch("rich.prompt.Prompt.ask", return_value="q"):
            with patch("rich.console.Console.print"):
                action = cli.get_game_review_action(1, 1)
                self.assertEqual(action, "q")

    def test_game_history_manager_edge_cases(self):
        """Test GameHistoryManager handles edge cases properly."""
        manager = GameHistoryManager()

        # Test with empty games list
        pages = manager.paginate_games([])
        self.assertEqual(pages, [])

        # Test with single game
        single_game = [{"game_id": "TEST01", "target_word": "TESTS"}]
        pages = manager.paginate_games(single_game)
        self.assertEqual(len(pages), 1)
        self.assertEqual(len(pages[0]), 1)

        # Test game lookup with various cases
        self.assertIsNone(manager.get_game_by_id([], "NOTFOUND"))

        # Test validation
        self.assertTrue(manager.validate_game_id("ABC123"))
        self.assertFalse(manager.validate_game_id("ABC"))
        self.assertFalse(manager.validate_game_id("ABC-123"))

    def test_error_handling_integration(self):
        """Test error handling across the review feature."""
        # Test with non-existent file
        manager = GameHistoryManager("/non/existent/path.json")
        games = manager.load_game_history()
        self.assertEqual(games, [])

        # Test with invalid JSON file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_file.write("invalid json")
            temp_file_path = temp_file.name

        try:
            manager = GameHistoryManager(temp_file_path)
            with self.assertRaises(Exception):  # Should raise GameHistoryError
                manager.load_game_history()
        finally:
            import os

            os.unlink(temp_file_path)

    def test_menu_integration(self):
        """Test that the menu system properly integrates the review option."""
        cli = CLIInterface()

        # Test that review option is available in choices
        with patch("rich.prompt.Prompt.ask", return_value="3"):
            mode = cli.get_game_mode()
            self.assertEqual(mode, "review")

        with patch("rich.prompt.Prompt.ask", return_value="review"):
            mode = cli.get_game_mode()
            self.assertEqual(mode, "review")

    def test_data_format_compatibility(self):
        """Test that the review feature handles different data formats."""
        manager = GameHistoryManager()

        # Test with minimal game data
        minimal_game = {"game_id": "TEST01"}
        formatted = manager.format_game_summary(minimal_game)
        self.assertEqual(formatted["game_id"], "TEST01")
        self.assertEqual(formatted["target"], "Unknown")
        self.assertEqual(formatted["result"], "Lost")

        # Test with complete game data
        complete_game = {
            "game_id": "TEST02",
            "timestamp": "2025-07-01T12:01:54.056006",
            "target_word": "TESTS",
            "won": True,
            "attempts": 3,
        }
        formatted = manager.format_game_summary(complete_game)
        self.assertEqual(formatted["game_id"], "TEST02")
        self.assertEqual(formatted["target"], "TESTS")
        self.assertEqual(formatted["result"], "Won")
        self.assertEqual(formatted["attempts"], "3")

    def test_performance_with_large_dataset(self):
        """Test performance with a large number of games."""
        # Create a large dataset
        large_dataset = []
        for i in range(1000):
            game = {
                "game_id": f"GAME{i:04d}",
                "timestamp": "2025-07-01T12:01:54.056006",
                "target_word": "TESTS",
                "won": i % 2 == 0,  # Alternate between won/lost
                "attempts": (i % 6) + 1,
                "guesses": [["AUDIO", "BYBBB", "entropy"]],
            }
            large_dataset.append(game)

        manager = GameHistoryManager()

        # Test formatting large dataset
        formatted_games = [manager.format_game_summary(game) for game in large_dataset]
        self.assertEqual(len(formatted_games), 1000)

        # Test pagination of large dataset
        pages = manager.paginate_games(formatted_games, page_size=10)
        self.assertEqual(len(pages), 100)  # 1000 games / 10 per page = 100 pages
        self.assertEqual(len(pages[0]), 10)
        self.assertEqual(len(pages[-1]), 10)

        # Test game lookup in large dataset
        game = manager.get_game_by_id(large_dataset, "GAME0500")
        self.assertIsNotNone(game)
        self.assertEqual(game["game_id"], "GAME0500")


if __name__ == "__main__":
    unittest.main()
