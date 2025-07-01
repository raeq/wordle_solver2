# tests/test_review_app_functionality.py
"""
Tests for the review mode functionality in the main app.
"""
import unittest
from unittest.mock import Mock, patch

from src.modules.app import WordleSolverApp
from src.modules.backend.game_history_manager import GameHistoryError


class TestReviewAppFunctionality(unittest.TestCase):
    """Test cases for review mode in the main application."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock all dependencies to avoid initialization issues
        with patch("src.modules.app.get_container"), patch(
            "src.modules.app.get_settings"
        ):
            self.app = WordleSolverApp()

        # Mock the UI component
        self.app._components["ui"] = Mock()
        self.mock_ui = self.app._components["ui"]

    @patch("src.modules.app.GameHistoryManager")
    def test_run_review_mode_success(self, mock_history_manager_class):
        """Test successful review mode execution."""
        # Setup mock history manager
        mock_history_manager = Mock()
        mock_history_manager_class.return_value = mock_history_manager

        # Mock game data
        sample_games = [
            {"game_id": "CGVWFZ", "target_word": "BEGUN", "won": True, "attempts": 4},
            {"game_id": "Z0T6R0", "target_word": "FLUID", "won": True, "attempts": 2},
        ]

        formatted_games = [
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
        ]

        pages = [formatted_games]  # Single page

        mock_history_manager.load_game_history.return_value = sample_games
        mock_history_manager.format_game_summary.side_effect = formatted_games
        mock_history_manager.paginate_games.return_value = pages

        # Mock UI interactions - user quits immediately
        self.mock_ui.get_game_review_action.return_value = "q"

        # Run review mode
        self.app._run_review_mode()

        # Verify interactions
        self.mock_ui.display_review_mode_start.assert_called_once()
        mock_history_manager.load_game_history.assert_called_once()
        self.mock_ui.display_game_list.assert_called_once_with(formatted_games, 1, 1)
        self.mock_ui.get_game_review_action.assert_called_once_with(1, 1)

    @patch("src.modules.app.GameHistoryManager")
    def test_run_review_mode_no_games(self, mock_history_manager_class):
        """Test review mode when no games exist."""
        # Setup mock history manager with no games
        mock_history_manager = Mock()
        mock_history_manager_class.return_value = mock_history_manager
        mock_history_manager.load_game_history.return_value = []

        # Run review mode
        self.app._run_review_mode()

        # Verify interactions
        self.mock_ui.display_review_mode_start.assert_called_once()
        mock_history_manager.load_game_history.assert_called_once()
        self.mock_ui.console.print.assert_called_with(
            "[yellow]No games found in history.[/yellow]"
        )

    @patch("src.modules.app.GameHistoryManager")
    def test_run_review_mode_navigation(self, mock_history_manager_class):
        """Test navigation through pages in review mode."""
        # Setup mock history manager
        mock_history_manager = Mock()
        mock_history_manager_class.return_value = mock_history_manager

        # Create enough games for multiple pages
        sample_games = [{"game_id": f"GAME{i:02d}"} for i in range(25)]
        formatted_games = [
            {
                "game_id": f"GAME{i:02d}",
                "date": "2025-07-01",
                "target": "TESTS",
                "attempts": "3",
                "result": "Won",
            }
            for i in range(25)
        ]

        # Create 3 pages of 10 games each, with 5 games on the last page
        page1 = formatted_games[:10]
        page2 = formatted_games[10:20]
        page3 = formatted_games[20:25]
        pages = [page1, page2, page3]

        mock_history_manager.load_game_history.return_value = sample_games
        mock_history_manager.format_game_summary.side_effect = formatted_games
        mock_history_manager.paginate_games.return_value = pages

        # Mock UI interactions: next page, then previous page, then quit
        self.mock_ui.get_game_review_action.side_effect = ["n", "p", "q"]

        # Run review mode
        self.app._run_review_mode()

        # Verify the pages were displayed in correct order
        display_calls = self.mock_ui.display_game_list.call_args_list
        self.assertEqual(len(display_calls), 3)

        # Check page navigation
        self.assertEqual(display_calls[0][0], (page1, 1, 3))  # First page
        self.assertEqual(display_calls[1][0], (page2, 2, 3))  # Second page after 'n'
        self.assertEqual(
            display_calls[2][0], (page1, 1, 3)
        )  # Back to first page after 'p'

    @patch("src.modules.app.GameHistoryManager")
    def test_run_review_mode_game_simulation(self, mock_history_manager_class):
        """Test game simulation in review mode."""
        # Setup mock history manager
        mock_history_manager = Mock()
        mock_history_manager_class.return_value = mock_history_manager

        sample_game = {
            "game_id": "CGVWFZ",
            "target_word": "BEGUN",
            "won": True,
            "attempts": 4,
            "guesses": [["AUDIO", "BYBBB", "entropy"]],
        }

        sample_games = [sample_game]
        formatted_games = [
            {
                "game_id": "CGVWFZ",
                "date": "2025-07-01",
                "target": "BEGUN",
                "attempts": "4",
                "result": "Won",
            }
        ]
        pages = [formatted_games]

        mock_history_manager.load_game_history.return_value = sample_games
        mock_history_manager.format_game_summary.return_value = formatted_games[0]
        mock_history_manager.paginate_games.return_value = pages
        mock_history_manager.get_game_by_id.return_value = sample_game

        # Mock UI interactions: enter game ID, then quit
        self.mock_ui.get_game_review_action.side_effect = ["CGVWFZ", "q"]

        # Run review mode
        self.app._run_review_mode()

        # Verify game simulation was called
        mock_history_manager.get_game_by_id.assert_called_with(sample_games, "CGVWFZ")
        self.mock_ui.simulate_game_display.assert_called_once_with(sample_game)

    @patch("src.modules.app.GameHistoryManager")
    def test_run_review_mode_invalid_game_id(self, mock_history_manager_class):
        """Test handling of invalid game ID in review mode."""
        # Setup mock history manager
        mock_history_manager = Mock()
        mock_history_manager_class.return_value = mock_history_manager

        sample_games = [{"game_id": "CGVWFZ"}]
        formatted_games = [
            {
                "game_id": "CGVWFZ",
                "date": "2025-07-01",
                "target": "BEGUN",
                "attempts": "4",
                "result": "Won",
            }
        ]
        pages = [formatted_games]

        mock_history_manager.load_game_history.return_value = sample_games
        mock_history_manager.format_game_summary.return_value = formatted_games[0]
        mock_history_manager.paginate_games.return_value = pages
        mock_history_manager.get_game_by_id.return_value = None  # Game not found

        # Mock UI interactions: enter invalid game ID, then quit
        self.mock_ui.get_game_review_action.side_effect = ["NOTFND", "q"]

        # Run review mode
        self.app._run_review_mode()

        # Verify error message was displayed
        error_calls = [
            call
            for call in self.mock_ui.console.print.call_args_list
            if "not found" in str(call)
        ]
        self.assertTrue(len(error_calls) > 0)

    @patch("src.modules.app.GameHistoryManager")
    def test_run_review_mode_history_load_error(self, mock_history_manager_class):
        """Test handling of history loading errors."""
        # Setup mock history manager that raises an error
        mock_history_manager = Mock()
        mock_history_manager_class.return_value = mock_history_manager
        mock_history_manager.load_game_history.side_effect = GameHistoryError(
            "File not found"
        )

        # Run review mode
        self.app._run_review_mode()

        # Verify error message was displayed
        self.mock_ui.console.print.assert_called_with(
            "[bold red]Error loading game history: File not found[/bold red]"
        )

    @patch("src.modules.app.GameHistoryManager")
    def test_run_review_mode_general_error(self, mock_history_manager_class):
        """Test handling of general errors in review mode."""
        # Setup mock history manager that raises a general error
        mock_history_manager_class.side_effect = Exception("General error")

        # Run review mode
        self.app._run_review_mode()

        # Verify error message was displayed
        self.mock_ui.console.print.assert_called_with(
            "[bold red]Error in review mode: General error[/bold red]"
        )

    def test_run_method_includes_review_mode(self):
        """Test that the main run method handles review mode."""
        # Mock UI to return review mode, then exit
        self.mock_ui.get_game_mode.side_effect = ["review"]
        self.mock_ui.ask_play_again.return_value = False
        self.mock_ui.get_strategy_selection.return_value = None

        # Mock stats manager
        mock_stats = Mock()
        mock_stats.get_stats.return_value = {
            "games_played": 0,
            "games_won": 0,
            "win_rate": 0,
            "avg_attempts": 0,
        }
        self.app._components["stats_manager"] = mock_stats

        # Mock the review mode method
        with patch.object(self.app, "_run_review_mode") as mock_review:
            self.app.run()

            # Verify review mode was called
            mock_review.assert_called_once()

    @patch("src.modules.app.GameHistoryManager")
    def test_run_review_mode_edge_cases(self, mock_history_manager_class):
        """Test edge cases in review mode."""
        # Setup mock history manager
        mock_history_manager = Mock()
        mock_history_manager_class.return_value = mock_history_manager

        # Test with games but no pages (edge case)
        sample_games = [{"game_id": "TEST01"}]
        mock_history_manager.load_game_history.return_value = sample_games
        mock_history_manager.format_game_summary.return_value = {"game_id": "TEST01"}
        mock_history_manager.paginate_games.return_value = []  # No pages

        # Run review mode
        self.app._run_review_mode()

        # Verify appropriate message was displayed
        self.mock_ui.console.print.assert_called_with(
            "[yellow]No games to display.[/yellow]"
        )

    @patch("src.modules.app.GameHistoryManager")
    def test_run_review_mode_boundary_navigation(self, mock_history_manager_class):
        """Test boundary conditions for page navigation."""
        # Setup mock history manager
        mock_history_manager = Mock()
        mock_history_manager_class.return_value = mock_history_manager

        sample_games = [{"game_id": "TEST01"}]
        formatted_games = [
            {
                "game_id": "TEST01",
                "date": "2025-07-01",
                "target": "TESTS",
                "attempts": "3",
                "result": "Won",
            }
        ]
        pages = [formatted_games]

        mock_history_manager.load_game_history.return_value = sample_games
        mock_history_manager.format_game_summary.return_value = formatted_games[0]
        mock_history_manager.paginate_games.return_value = pages

        # Mock UI interactions: try to go to previous page on first page, then next on last page
        self.mock_ui.get_game_review_action.side_effect = ["p", "n", "q"]

        # Run review mode
        self.app._run_review_mode()

        # Should have stayed on the same page (page 1) for all attempts
        display_calls = self.mock_ui.display_game_list.call_args_list
        for call in display_calls:
            page_num = call[0][1]  # Second argument is page number
            self.assertEqual(page_num, 1)


if __name__ == "__main__":
    unittest.main()
