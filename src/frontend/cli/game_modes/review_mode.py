# src/frontend/cli/game_modes/review_mode.py
"""
Review mode specific UI components and interactions.
"""

from typing import Any, Dict, List

from ..display import DisplayManager
from ..formatters import TextFormatter
from ..input_handler import InputHandler


class ReviewModeHandler:
    """Handles UI interactions specific to review mode."""

    def __init__(self, display: DisplayManager, input_handler: InputHandler):
        """Initialize review mode handler."""
        self.display = display
        self.input_handler = input_handler

    def start_mode(self) -> None:
        """Display review mode start screen."""
        self.display.display_mode_start("review")

    def get_navigation_input(self) -> str:
        """Get navigation input from user in review mode."""
        return self.input_handler.get_simple_input(
            "Enter command (n/p for navigation, Game ID to review, 'clear' to clear all history, q to quit):"
        )

    def confirm_clear_history(self) -> bool:
        """Get confirmation from user before clearing all history."""
        self.display.console.print(
            "\n[bold red]⚠️  WARNING: This will permanently delete ALL game history![/bold red]"
        )
        self.display.console.print(
            "[yellow]This action cannot be undone. All your game records and statistics will be lost.[/yellow]"
        )

        confirmation = self.input_handler.get_simple_input(
            "\nType 'DELETE ALL' (in caps) to confirm, or anything else to cancel:"
        )

        return confirmation == "DELETE ALL"

    def display_clear_history_result(self, success: bool, games_count: int) -> None:
        """Display the result of clearing history operation."""
        if success:
            self.display.console.print(
                f"\n[bold green]✅ Successfully cleared all history! "
                f"Deleted {games_count} game records.[/bold green]"
            )
        else:
            self.display.console.print(
                "\n[bold red]❌ Failed to clear history. Please try again.[/bold red]"
            )

    def display_games_list(
        self, games: List[Dict[str, Any]], page: int, total_pages: int
    ) -> None:
        """Display a paginated list of games."""
        if not games:
            # Use console.print directly to match test expectations
            self.display.console.print("[yellow]No games found in history.[/yellow]")
            return

        # Create header
        header = f"📚 Game History - Page {page}/{total_pages}"
        self.display.display_info(header)

        # Display games
        for game in games:
            self._display_game_summary(game)

    def _display_game_summary(self, game: Dict[str, Any]) -> None:
        """Display a summary of a single game."""
        game_id = game.get("game_id", "Unknown")
        mode = game.get("mode", "Unknown")
        won = game.get("won", False)
        attempts = game.get("attempts", 0)
        target_word = game.get("target_word", "Unknown")
        timestamp = game.get("timestamp", "Unknown")

        # Format timestamp for display
        formatted_date = self._format_timestamp(timestamp)

        # Format status
        status = "🎉 Won" if won else "😢 Lost"
        status_style = "green" if won else "red"

        # Create game summary
        summary = f"""
[bold]Game ID:[/bold] {game_id}
[bold]Mode:[/bold] {mode.title()}
[bold]Target:[/bold] {target_word}
[bold]Result:[/bold] [{status_style}]{status}[/{status_style}] in {attempts} attempts
[bold]Date:[/bold] {formatted_date}
[dim]{'=' * 50}[/dim]
        """

        self.display.console.print(summary.strip())

    def _format_timestamp(self, timestamp: str) -> str:
        """Format ISO timestamp to readable date format."""
        if timestamp == "Unknown" or not timestamp:
            return "Unknown"

        try:
            from datetime import datetime

            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except (ValueError, AttributeError):
            return timestamp  # Return original if parsing fails

    def display_detailed_game_review(self, game: Dict[str, Any]) -> None:
        """Display detailed review of a specific game."""
        game_id = game.get("game_id", "Unknown")
        target_word = game.get("target_word", "Unknown")
        guesses = game.get("guesses", [])
        won = game.get("won", False)
        attempts = game.get("attempts", 0)
        mode = game.get("mode", "Unknown")
        timestamp = game.get("timestamp", "Unknown")

        # Format timestamp for display
        formatted_date = self._format_timestamp(timestamp)

        # Display game header
        header = f"""
🎯 Detailed Game Review: {game_id}

[bold]Mode:[/bold] {mode.title()}
[bold]Date:[/bold] {formatted_date}
[bold]Target Word:[/bold] {target_word}
[bold]Result:[/bold] {"🎉 Won" if won else "😢 Lost"} in {attempts} attempts

[dim]{'=' * 60}[/dim]
        """

        self.display.console.print(header.strip())

        # Display each guess
        for i, guess_data in enumerate(guesses, 1):
            self._display_guess_detail(i, guess_data)

        # Display final summary
        self._display_game_analysis(game)

    def _display_guess_detail(self, turn: int, guess_data: tuple) -> None:
        """Display detailed information about a single guess."""
        if len(guess_data) >= 3:
            guess, result, method = guess_data[0], guess_data[1], guess_data[2]
        else:
            guess, result = guess_data[0], guess_data[1]
            method = "unknown"

        colored_result = TextFormatter.colorize_guess_result(guess, result)

        from src.modules.backend.result_color import ResultColor

        emoji_result = ResultColor.result_to_emoji(result)

        self.display.console.print(f"\n[bold]Turn {turn}:[/bold]")
        self.display.console.print(f"  Word: [bold white]{guess}[/bold white]")
        self.display.console.print(f"  Result: {colored_result} {emoji_result}")
        self.display.console.print(f"  Method: [cyan]{method}[/cyan]")

    def _display_game_analysis(self, game: Dict[str, Any]) -> None:
        """Display analysis and statistics for the game."""
        guesses = game.get("guesses", [])
        won = game.get("won", False)
        attempts = game.get("attempts", 0)

        self.display.console.print(f"\n[dim]{'=' * 60}[/dim]")

        # Basic stats
        if won:
            self.display.console.print(
                f"[bold green]🎉 Solved in {attempts} attempts![/bold green]"
            )
        else:
            self.display.console.print(
                f"[bold red]😢 Not solved in {attempts} attempts[/bold red]"
            )

        # Letter analysis
        if guesses:
            self._display_letter_analysis(guesses)

    def _display_letter_analysis(self, guesses: List[tuple]) -> None:
        """Display analysis of letters used in the game."""
        all_letters = set()
        green_letters = set()
        yellow_letters = set()

        from src.modules.backend.result_color import ResultColor

        for guess_data in guesses:
            if len(guess_data) >= 2:
                guess, result = guess_data[0], guess_data[1]
                for letter, color in zip(guess, result):
                    all_letters.add(letter)
                    if color == ResultColor.GREEN.value:
                        green_letters.add(letter)
                    elif color == ResultColor.YELLOW.value:
                        yellow_letters.add(letter)

        self.display.console.print("\n[bold]Letter Analysis:[/bold]")
        self.display.console.print(f"  Total unique letters tried: {len(all_letters)}")
        self.display.console.print(f"  Correct positions found: {len(green_letters)}")
        self.display.console.print(
            f"  Correct letters (wrong pos): {len(yellow_letters)}"
        )

    def display_pagination_info(
        self, current_page: int, total_pages: int, total_games: int
    ) -> None:
        """Display pagination information."""
        info = f"Page {current_page} of {total_pages} ({total_games} total games)"
        self.display.display_info(info)

    def display_no_games_message(self) -> None:
        """Display message when no games are found."""
        self.display.display_info("No games found in history.")

    def display_invalid_game_id_message(self, game_id: str) -> None:
        """Display message for invalid game ID."""
        self.display.display_error(f"Game with ID '{game_id}' not found.")

    def get_continue_after_review(self) -> None:
        """Get continue input after displaying game review."""
        self.input_handler.get_continue_prompt()

    def display_statistics_summary(self, stats: Dict[str, Any]) -> None:
        """Display overall statistics summary."""
        if not stats:
            self.display.display_info("No statistics available.")
            return

        total_games = stats.get("total_games", 0)
        wins = stats.get("wins", 0)
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        avg_attempts = stats.get("average_attempts", 0)

        summary = f"""
📊 Overall Statistics

[bold]Total Games:[/bold] {total_games}
[bold]Wins:[/bold] {wins}
[bold]Win Rate:[/bold] {win_rate:.1f}%
[bold]Average Attempts:[/bold] {avg_attempts:.1f}
        """

        self.display.console.print(summary.strip())
