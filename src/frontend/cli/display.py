# src/frontend/cli/display.py
"""
Display components for the CLI interface.
Handles all output operations and visual presentation.
"""

from typing import List, Optional

from rich.console import Console

# Import StrategyFactory from the centralized __init__.py
from src.modules.backend.solver import StrategyFactory

from .constants import (
    PLAY_MODE_START,
    REVIEW_MODE_START,
    SOLVER_MODE_START,
    STRATEGY_DESCRIPTIONS,
    STRATEGY_INFO,
    WELCOME_MESSAGE,
)
from .formatters import MessageFormatter, TableFormatter, TextFormatter
from .types import ConsoleProtocol, DisplayConfig


class DisplayManager:
    """Manages all display operations for the CLI."""

    def __init__(self, console: Optional[ConsoleProtocol] = None):
        """Initialize display manager with optional console injection."""
        self.console = console or Console()
        self.config = DisplayConfig()

    def display_welcome(self) -> None:
        """Display the main welcome message."""
        panel = TextFormatter.create_panel(
            WELCOME_MESSAGE, "Wordle Solver", "bold blue"
        )
        self.console.print(panel)

    def display_mode_start(self, mode: str, **kwargs) -> None:
        """Display mode-specific start message."""
        if mode == "solver":
            self._display_solver_mode_start()
        elif mode == "play":
            self._display_play_mode_start(**kwargs)
        elif mode == "review":
            self._display_review_mode_start()

    def _display_solver_mode_start(self) -> None:
        """Display solver mode start message."""
        content = SOLVER_MODE_START.format(green="🟩", yellow="🟨", black="⬛")
        panel = TextFormatter.format_game_mode_panel(content, "Wordle Solver", "solver")
        self.console.print(panel)

    def _display_play_mode_start(self, game_id: str, difficulty_hint: str = "") -> None:
        """Display play mode start message."""
        content = PLAY_MODE_START.format(
            game_id=game_id, difficulty_hint=difficulty_hint
        )
        panel = TextFormatter.format_game_mode_panel(content, "Play Wordle", "play")
        self.console.print(panel)

    def _display_review_mode_start(self) -> None:
        """Display review mode start message."""
        panel = TextFormatter.format_game_mode_panel(
            REVIEW_MODE_START, "Review Games", "review"
        )
        self.console.print(panel)

    def display_current_strategy(self, strategy_name: str) -> None:
        """Display information about the current strategy."""
        description = STRATEGY_DESCRIPTIONS.get(strategy_name, "Unknown strategy")
        panel = MessageFormatter.format_current_strategy_display(
            strategy_name, description
        )
        self.console.print(panel)

    def display_available_strategies(self) -> None:
        """Display table of all available strategies."""
        available_strategies = StrategyFactory.get_available_strategies()
        table = TableFormatter.create_strategies_table(
            STRATEGY_INFO, available_strategies
        )
        self.console.print(table)

    def display_suggestions(
        self,
        suggestions: List[str],
        remaining_words_count: int,
        common_words: Optional[List[str]] = None,
        strategy_name: Optional[str] = None,
    ) -> None:
        """Display word suggestions to the user."""
        if not suggestions:
            self.console.print(MessageFormatter.format_no_suggestions_message())
            return

        # Display suggestions table
        table = TableFormatter.create_suggestions_table(
            suggestions, remaining_words_count, common_words, strategy_name
        )
        self.console.print(table)

        # Add strategy hint if enabled and provided
        if self.config.show_hints and strategy_name:
            hint = MessageFormatter.format_strategy_hint(
                strategy_name, remaining_words_count
            )
            if hint:
                self.console.print(hint)

    def display_guess_result(
        self, guess: str, result: str, attempt: int, max_attempts: int
    ) -> None:
        """Display the result of a guess."""
        formatted_result = TextFormatter.format_guess_display(
            guess, result, attempt, max_attempts
        )
        self.console.print(formatted_result)

    def display_game_over(
        self,
        won: bool,
        attempts: int,
        target_word: Optional[str] = None,
        guesses: Optional[List[tuple]] = None,
    ) -> None:
        """Display game over information."""
        # Show game review if data is available
        if target_word and guesses:
            review_lines = TableFormatter.create_game_review_table(guesses, target_word)
            for line in review_lines:
                self.console.print(line)

        # Show final result
        self.console.print("\n[dim]" + "=" * 50 + "[/dim]")
        game_over_msg = MessageFormatter.format_game_over_message(won, attempts)
        self.console.print(game_over_msg)

    def display_error(self, message: str) -> None:
        """Display an error message."""
        formatted_msg = TextFormatter.format_error_message(message)
        self.console.print(formatted_msg)

    def display_success(self, message: str) -> None:
        """Display a success message."""
        formatted_msg = TextFormatter.format_success_message(message)
        self.console.print(formatted_msg)

    def display_info(self, message: str) -> None:
        """Display an info message."""
        formatted_msg = TextFormatter.format_info_message(message)
        self.console.print(formatted_msg)

    def display_strategy_selection_current(self, current_strategy: str) -> None:
        """Display current strategy before selection."""
        message = f"\n[bold]Current strategy:[/bold] [cyan]{current_strategy}[/cyan]"
        self.console.print(message)

    def update_config(self, config: DisplayConfig) -> None:
        """Update display configuration."""
        self.config = config
