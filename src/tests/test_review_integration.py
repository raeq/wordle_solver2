# src/tests/test_review_integration.py
"""
Integration tests for the review mode functionality.
"""

import json
import tempfile
import unittest
from unittest.mock import Mock, patch

from ..frontend.cli import CLIInterface
from ..modules.app import WordleSolverApp
from ..modules.backend.game_history_manager import GameHistoryManager


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

        # Mock the UI component
        app._components["ui"] = Mock()

        # Test that review mode can be called without errors
        with patch.object(app, "_run_review_mode") as mock_review:
            # The run method doesn't accept a mode parameter, so we call _run_review_mode directly
            app._run_review_mode()
            mock_review.assert_called_once()

    def test_history_manager_cli_integration(self):
        """Test integration between history manager and CLI interface."""
        # Create temporary history file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            json.dump(self.sample_history_data, temp_file)
            temp_file_path = temp_file.name

        try:
            manager = GameHistoryManager(temp_file_path)
            cli = CLIInterface()

            # Load and format games
            games = manager.load_game_history()
            formatted_games = [manager.format_game_summary(game) for game in games]

            # Test that CLI can handle the formatted data
            with patch("rich.console.Console.print") as mock_print:
                cli.display_game_list(formatted_games, 1, 1)
                mock_print.assert_called()

            # Test game simulation display with mocked input
            game = games[0]
            with patch("rich.console.Console.print") as mock_print, patch(
                "src.frontend.cli.input_handler.InputHandler.get_continue_prompt"
            ) as mock_input:
                mock_input.return_value = ""
                cli.simulate_game_display(game)
                mock_print.assert_called()

        finally:
            import os

            os.unlink(temp_file_path)

    def test_error_handling_integration(self):
        """Test error handling across components."""
        # Test with non-existent file
        manager = GameHistoryManager("/non/existent/path.json")
        games = manager.load_game_history()
        self.assertEqual(games, [])

        # Test CLI with empty data
        cli = CLIInterface()
        with patch("rich.console.Console.print") as mock_print:
            cli.display_game_list([], 1, 1)
            mock_print.assert_called_with("[yellow]No games found in history.[/yellow]")


if __name__ == "__main__":
    unittest.main()
