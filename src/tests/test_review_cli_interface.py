# src/tests/test_review_cli_interface.py
"""
Tests for the review mode functionality of the CLI interface.
"""

import unittest
from unittest.mock import patch

from ..frontend.cli import CLIInterface


class TestReviewCLIInterface(unittest.TestCase):
    """Test cases for review functionality in CLI interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = CLIInterface()
        self.sample_games_page = [
            {
                "game_id": "CGVWFZ",
                "date": "2025-07-01 12:01",
                "target": "BEGUN",
                "attempts": "4",
                "result": "Won",
            },
            {
                "game_id": "Z0T6R0",
                "date": "2025-07-01 12:03",
                "target": "FLUID",
                "attempts": "2",
                "result": "Won",
            },
            {
                "game_id": "X9Y2Z1",
                "date": "2025-07-01 12:13",
                "target": "BYTES",
                "attempts": "6",
                "result": "Lost",
            },
        ]

        self.sample_game = {
            "game_id": "CGVWFZ",
            "timestamp": "2025-07-01T12:01:54.056006",
            "target_word": "BEGUN",
            "won": True,
            "attempts": 4,
            "guesses": [
                ["AUDIO", "BYBBB", "entropy"],
                ["CRUEL", "BBYYB", "entropy"],
                ["ENSUE", "YYBGB", "entropy"],
                ["BEGUN", "GGGGG", "entropy"],
            ],
        }

    @patch("rich.console.Console.print")
    def test_display_game_list_with_games(self, mock_print):
        """Test displaying a list of games."""
        self.cli.display_game_list(self.sample_games_page, 1, 3)

        # Should have called print to display the table
        mock_print.assert_called()

        # Check that the call was made (table would be passed as argument)
        call_args = mock_print.call_args_list
        self.assertTrue(len(call_args) > 0)

    @patch("rich.console.Console.print")
    def test_display_game_list_empty(self, mock_print):
        """Test displaying an empty game list."""
        self.cli.display_game_list([], 1, 1)

        # Should print a message about no games found
        mock_print.assert_called_with("[yellow]No games found in history.[/yellow]")

    @patch("rich.prompt.Prompt.ask")
    @patch("rich.console.Console.print")
    def test_get_game_review_action_quit(self, mock_print, mock_ask):
        """Test getting quit action from user."""
        mock_ask.return_value = "q"

        action = self.cli.get_game_review_action(1, 3)

        self.assertEqual(action, "q")
        mock_ask.assert_called()

    @patch("rich.prompt.Prompt.ask")
    @patch("rich.console.Console.print")
    def test_get_game_review_action_next_page(self, mock_print, mock_ask):
        """Test getting next page action from user."""
        mock_ask.return_value = "n"

        action = self.cli.get_game_review_action(1, 3)

        self.assertEqual(action, "n")

    @patch("rich.prompt.Prompt.ask")
    @patch("rich.console.Console.print")
    def test_get_game_review_action_previous_page(self, mock_print, mock_ask):
        """Test getting previous page action from user."""
        mock_ask.return_value = "p"

        action = self.cli.get_game_review_action(2, 3)

        self.assertEqual(action, "p")

    @patch("rich.prompt.Prompt.ask")
    @patch("rich.console.Console.print")
    def test_get_game_review_action_game_id(self, mock_print, mock_ask):
        """Test getting game ID from user."""
        mock_ask.return_value = "CGVWFZ"

        action = self.cli.get_game_review_action(1, 3)

        self.assertEqual(action, "CGVWFZ")

    @patch("rich.console.Console.print")
    @patch("src.frontend.cli.input_handler.InputHandler.get_continue_prompt")
    def test_simulate_game_display(self, mock_get_continue_prompt, mock_print):
        """Test displaying game simulation."""
        # Mock the input handler to avoid stdin issues
        mock_get_continue_prompt.return_value = ""

        self.cli.simulate_game_display(self.sample_game)

        # Should have called print to display game information
        mock_print.assert_called()

        # Check that multiple print calls were made for game details
        call_args = mock_print.call_args_list
        self.assertGreater(len(call_args), 0)

    @patch("rich.console.Console.print")
    def test_display_review_mode_start(self, mock_print):
        """Test displaying review mode start message."""
        self.cli.display_review_mode_start()

        # Should have called print to display the start message
        mock_print.assert_called()

        # Check that the call was made
        call_args = mock_print.call_args_list
        self.assertTrue(len(call_args) > 0)


if __name__ == "__main__":
    unittest.main()
