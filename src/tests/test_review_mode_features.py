# src/tests/test_review_mode_features.py
"""
Test the new review mode features including clear history and timestamp formatting.
"""
import unittest
from unittest.mock import Mock, patch

from src.frontend.cli.display import DisplayManager
from src.frontend.cli.game_modes.review_mode import ReviewModeHandler
from src.frontend.cli.input_handler import InputHandler


class TestReviewModeFeatures(unittest.TestCase):
    """Test review mode UI features."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_display = Mock(spec=DisplayManager)
        self.mock_input_handler = Mock(spec=InputHandler)
        self.mock_console = Mock()
        self.mock_display.console = self.mock_console

        # Create review mode handler
        self.review_handler = ReviewModeHandler(
            self.mock_display, self.mock_input_handler
        )

    def test_get_navigation_input_includes_clear_option(self):
        """Test that navigation input prompt includes the clear option."""
        self.mock_input_handler.get_simple_input.return_value = "clear"

        result = self.review_handler.get_navigation_input()

        # Verify the prompt includes the clear option
        self.mock_input_handler.get_simple_input.assert_called_once()
        call_args = self.mock_input_handler.get_simple_input.call_args[0][0]
        self.assertIn("'clear' to clear all history", call_args)
        self.assertEqual(result, "clear")

    def test_confirm_clear_history_shows_warning(self):
        """Test that clear history confirmation shows proper warning."""
        self.mock_input_handler.get_simple_input.return_value = "DELETE ALL"

        result = self.review_handler.confirm_clear_history()

        # Verify warning messages were displayed
        self.assertEqual(self.mock_console.print.call_count, 2)

        # Check warning message content
        warning_calls = self.mock_console.print.call_args_list
        self.assertIn("WARNING", warning_calls[0][0][0])
        self.assertIn("permanently delete ALL game history", warning_calls[0][0][0])
        self.assertIn("cannot be undone", warning_calls[1][0][0])

        # Verify confirmation prompt
        self.mock_input_handler.get_simple_input.assert_called_once()
        prompt = self.mock_input_handler.get_simple_input.call_args[0][0]
        self.assertIn("DELETE ALL", prompt)

        self.assertTrue(result)

    def test_confirm_clear_history_requires_exact_match(self):
        """Test that clear history requires exact 'DELETE ALL' confirmation."""
        test_cases = [
            ("delete all", False),  # lowercase
            ("DELETE", False),  # incomplete
            ("DELETE ALL HISTORY", False),  # extra text
            ("DELETE ALL", True),  # exact match
            ("", False),  # empty
            ("cancel", False),  # different text
        ]

        for input_text, expected_result in test_cases:
            with self.subTest(input_text=input_text):
                self.mock_input_handler.get_simple_input.return_value = input_text
                result = self.review_handler.confirm_clear_history()
                self.assertEqual(result, expected_result)

    def test_display_clear_history_result_success(self):
        """Test successful clear history result display."""
        self.review_handler.display_clear_history_result(True, 15)

        self.mock_console.print.assert_called_once()
        message = self.mock_console.print.call_args[0][0]
        self.assertIn("Successfully cleared", message)
        self.assertIn("15 game records", message)
        self.assertIn("✅", message)

    def test_display_clear_history_result_failure(self):
        """Test failed clear history result display."""
        self.review_handler.display_clear_history_result(False, 10)

        self.mock_console.print.assert_called_once()
        message = self.mock_console.print.call_args[0][0]
        self.assertIn("Failed to clear", message)
        self.assertIn("❌", message)

    def test_format_timestamp_valid_iso(self):
        """Test timestamp formatting with valid ISO format."""
        # Test with a valid ISO timestamp
        iso_timestamp = "2025-07-01T14:30:45.123456"
        formatted = self.review_handler._format_timestamp(iso_timestamp)

        # Should return a human-readable format
        self.assertIn("July", formatted)
        self.assertIn("2025", formatted)
        self.assertIn(":", formatted)  # Time separator

    def test_format_timestamp_with_timezone(self):
        """Test timestamp formatting with timezone."""
        iso_timestamp = "2025-07-01T14:30:45.123456Z"
        formatted = self.review_handler._format_timestamp(iso_timestamp)

        # Should handle timezone and return readable format
        self.assertIn("July", formatted)
        self.assertIn("2025", formatted)

    def test_format_timestamp_unknown(self):
        """Test timestamp formatting with 'Unknown' input."""
        formatted = self.review_handler._format_timestamp("Unknown")
        self.assertEqual(formatted, "Unknown")

    def test_format_timestamp_empty(self):
        """Test timestamp formatting with empty input."""
        formatted = self.review_handler._format_timestamp("")
        self.assertEqual(formatted, "Unknown")

    def test_format_timestamp_invalid(self):
        """Test timestamp formatting with invalid input."""
        invalid_timestamp = "not-a-timestamp"
        formatted = self.review_handler._format_timestamp(invalid_timestamp)

        # Should return original string if parsing fails
        self.assertEqual(formatted, invalid_timestamp)

    def test_display_game_summary_with_mode_and_formatted_date(self):
        """Test that game summary displays mode and formatted date correctly."""
        test_game = {
            "game_id": "ABC123",
            "mode": "solver",
            "won": True,
            "attempts": 3,
            "target_word": "CRANE",
            "timestamp": "2025-07-01T14:30:45.123456",
        }

        self.review_handler._display_game_summary(test_game)

        # Verify console.print was called
        self.mock_console.print.assert_called_once()
        summary = self.mock_console.print.call_args[0][0]

        # Check that all expected fields are present
        self.assertIn("ABC123", summary)
        self.assertIn("Solver", summary)  # Mode should be title-cased
        self.assertIn("CRANE", summary)
        self.assertIn("🎉 Won", summary)
        self.assertIn("3 attempts", summary)
        # Date should be formatted, not raw ISO
        self.assertIn("July", summary)
        self.assertNotIn("2025-07-01T14:30:45.123456", summary)

    def test_display_detailed_game_review_with_formatted_date(self):
        """Test that detailed review displays formatted date."""
        test_game = {
            "game_id": "ABC123",
            "mode": "manual",
            "won": False,
            "attempts": 6,
            "target_word": "CRANE",
            "timestamp": "2025-07-01T14:30:45.123456",
            "guesses": [["AUDIO", "BBBBB"], ["CRANE", "GGGGG"]],
        }

        # Mock the _display_guess_detail and _display_game_analysis methods
        with patch.object(self.review_handler, "_display_guess_detail"), patch.object(
            self.review_handler, "_display_game_analysis"
        ):

            self.review_handler.display_detailed_game_review(test_game)

        # Verify header was printed with formatted date
        self.mock_console.print.assert_called()
        header_call = self.mock_console.print.call_args_list[0]
        header = header_call[0][0]

        self.assertIn("ABC123", header)
        self.assertIn("Manual", header)  # Mode should be title-cased
        self.assertIn("July", header)  # Date should be formatted
        self.assertNotIn(
            "2025-07-01T14:30:45.123456", header
        )  # Raw ISO should not appear


class TestAppClearHistoryIntegration(unittest.TestCase):
    """Test the app-level clear history integration."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the app and its dependencies
        from src.modules.app import WordleSolverApp

        self.app = WordleSolverApp()

        # Mock the stats manager
        self.mock_stats_manager = Mock()
        self.app._components["stats_manager"] = self.mock_stats_manager

        # Mock the UI
        self.mock_ui = Mock()
        self.app._components["ui"] = self.mock_ui

    def test_handle_clear_history_no_history(self):
        """Test clear history when no history exists."""
        self.mock_stats_manager.has_history.return_value = False

        result = self.app._handle_clear_history()

        self.assertFalse(result)
        self.mock_ui.console.print.assert_called_once()
        message = self.mock_ui.console.print.call_args[0][0]
        self.assertIn("No history to clear", message)

    def test_handle_clear_history_user_confirms(self):
        """Test clear history when user confirms."""
        self.mock_stats_manager.has_history.return_value = True
        self.mock_stats_manager.get_history_count.return_value = 10
        self.mock_ui.review_mode.confirm_clear_history.return_value = True
        self.mock_stats_manager.clear_all_history.return_value = True

        result = self.app._handle_clear_history()

        self.assertTrue(result)
        self.mock_stats_manager.clear_all_history.assert_called_once()
        self.mock_ui.review_mode.display_clear_history_result.assert_called_once_with(
            True, 10
        )

    def test_handle_clear_history_user_cancels(self):
        """Test clear history when user cancels."""
        self.mock_stats_manager.has_history.return_value = True
        self.mock_stats_manager.get_history_count.return_value = 5
        self.mock_ui.review_mode.confirm_clear_history.return_value = False

        result = self.app._handle_clear_history()

        self.assertFalse(result)
        self.mock_stats_manager.clear_all_history.assert_not_called()
        self.mock_ui.console.print.assert_called_once()
        message = self.mock_ui.console.print.call_args[0][0]
        self.assertIn("cancelled", message)

    def test_handle_clear_history_clear_fails(self):
        """Test clear history when clear operation fails."""
        self.mock_stats_manager.has_history.return_value = True
        self.mock_stats_manager.get_history_count.return_value = 8
        self.mock_ui.review_mode.confirm_clear_history.return_value = True
        self.mock_stats_manager.clear_all_history.return_value = False

        result = self.app._handle_clear_history()

        self.assertFalse(result)
        self.mock_ui.review_mode.display_clear_history_result.assert_called_once_with(
            False, 8
        )


if __name__ == "__main__":
    unittest.main()
