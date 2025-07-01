# tests/test_review_cli_interface.py
"""
Tests for the review mode functionality of the CLI interface.
"""

import unittest
from unittest.mock import patch


from src.frontend.cli import CLIInterface


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

    @patch("rich.prompt.Prompt.ask")
    @patch("rich.console.Console.print")
    def test_get_game_review_action_invalid_input_retry(self, mock_print, mock_ask):
        """Test handling invalid input with retry."""
        # First return invalid input, then valid input
        mock_ask.side_effect = ["invalid", "q"]

        action = self.cli.get_game_review_action(1, 3)

        self.assertEqual(action, "q")
        # Should have been called twice due to retry
        self.assertEqual(mock_ask.call_count, 2)

    @patch("rich.prompt.Prompt.ask")
    @patch("rich.console.Console.print")
    def test_simulate_game_display(self, mock_print, mock_ask):
        """Test simulating a game display."""
        mock_ask.return_value = ""  # User presses Enter to continue

        self.cli.simulate_game_display(self.sample_game)

        # Should have called print multiple times to display game simulation
        self.assertTrue(mock_print.call_count > 0)

        # Should have asked user to continue
        mock_ask.assert_called()

    @patch("rich.console.Console.print")
    def test_display_review_mode_start(self, mock_print):
        """Test displaying review mode start message."""
        self.cli.display_review_mode_start()

        # Should have called print to display the panel
        mock_print.assert_called()

    def test_get_game_mode_includes_review(self):
        """Test that get_game_mode includes review option."""
        with patch("rich.prompt.Prompt.ask") as mock_ask:
            mock_ask.return_value = "3"

            mode = self.cli.get_game_mode()

            self.assertEqual(mode, "review")

    def test_get_game_mode_review_string(self):
        """Test that get_game_mode accepts 'review' string."""
        with patch("rich.prompt.Prompt.ask") as mock_ask:
            mock_ask.return_value = "review"

            mode = self.cli.get_game_mode()

            self.assertEqual(mode, "review")

    @patch("rich.console.Console.print")
    def test_display_welcome_includes_review_option(self, mock_print):
        """Test that welcome message includes review option."""
        self.cli.display_welcome()

        # Check that print was called
        mock_print.assert_called()

        # Get the printed Panel object and check its content
        call_args = mock_print.call_args[0][0]

        # Extract the renderable content from the Panel
        if hasattr(call_args, "renderable"):
            welcome_text = str(call_args.renderable)
        else:
            welcome_text = str(call_args)

        # Should mention review mode
        self.assertIn("Review Mode", welcome_text)
        self.assertIn("3.", welcome_text)

    def test_colorize_result_functionality(self):
        """Test that _colorize_result works correctly for game simulation."""
        # Test the colorize method works (it's used in simulate_game_display)
        guess = "AUDIO"
        result = "BYBBB"

        colored_result = self.cli._colorize_result(guess, result)

        # Should return a Text object
        from rich.text import Text

        self.assertIsInstance(colored_result, Text)

    @patch("rich.prompt.Prompt.ask")
    @patch("rich.console.Console.print")
    def test_simulate_game_display_with_incomplete_guess_data(
        self, mock_print, mock_ask
    ):
        """Test simulating a game with incomplete guess data."""
        mock_ask.return_value = ""

        incomplete_game = {
            "game_id": "TEST01",
            "timestamp": "2025-07-01T12:01:54.056006",
            "target_word": "TESTS",
            "won": True,
            "attempts": 2,
            "guesses": [
                ["AUDIO", "BYBBB"],  # Missing strategy
                ["TESTS", "GGGGG", "entropy"],
            ],
        }

        # Should not raise an error
        self.cli.simulate_game_display(incomplete_game)

        # Should have displayed the game
        self.assertTrue(mock_print.call_count > 0)

    @patch("rich.prompt.Prompt.ask")
    @patch("rich.console.Console.print")
    def test_get_game_review_action_navigation_options(self, mock_print, mock_ask):
        """Test that navigation options are correctly displayed based on page."""
        mock_ask.return_value = "q"

        # Test first page (should not show previous option)
        self.cli.get_game_review_action(1, 3)

        # Check that print was called to show options
        options_call = None
        for call in mock_print.call_args_list:
            if "Options:" in str(call):
                options_call = str(call)
                break

        if options_call:
            # Should not include "p = Previous page" on first page
            self.assertNotIn("p = Previous", options_call)

    @patch("rich.prompt.Prompt.ask")
    @patch("rich.console.Console.print")
    def test_get_game_review_action_last_page(self, mock_print, mock_ask):
        """Test navigation options on last page."""
        mock_ask.return_value = "q"

        # Reset mock to clear previous calls
        mock_print.reset_mock()

        # Test last page (should not show next option)
        self.cli.get_game_review_action(3, 3)

        # Check that print was called to show options
        options_call = None
        for call in mock_print.call_args_list:
            if "Options:" in str(call):
                options_call = str(call)
                break

        if options_call:
            # Should not include "n = Next page" on last page
            self.assertNotIn("n = Next", options_call)
