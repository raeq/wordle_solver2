# src/frontend/cli/interface.py
"""
Main CLI interface that coordinates all modular components.
This is the new, refactored CLI interface that replaces the monolithic version.
"""

from typing import List, Optional, Tuple

from rich.console import Console

from src.modules.backend.word_manager import WordManager

from .display import DisplayManager
from .game_modes import PlayModeHandler, ReviewModeHandler, SolverModeHandler
from .input_handler import InputHandler
from .types import DisplayConfig


class CLIInterface:
    """
    Modular CLI interface for the Wordle Solver application.

    This refactored version separates concerns into specialized components:
    - DisplayManager: Handles all output and visual presentation
    - InputHandler: Manages user input and validation
    - Game mode handlers: Provide mode-specific functionality
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize the CLI interface with all components."""
        # Core components
        self.console = console or Console()
        self.display = DisplayManager(self.console)
        self.input_handler = InputHandler()

        # Game mode handlers
        self.solver_mode = SolverModeHandler(self.display, self.input_handler)
        self.play_mode = PlayModeHandler(self.display, self.input_handler)
        self.review_mode = ReviewModeHandler(self.display, self.input_handler)

        # Configuration
        self.config = DisplayConfig()

    # Main interface methods
    def display_welcome(self) -> None:
        """Display the main welcome message."""
        self.display.display_welcome()

    def get_game_mode(self) -> str:
        """Get the game mode selection from user."""
        return self.input_handler.get_game_mode()

    # Solver mode methods
    def display_solver_mode_start(self) -> None:
        """Display solver mode start screen."""
        self.solver_mode.start_mode()

    def get_guess_and_result(self) -> Tuple[str, str]:
        """Get guess and result from user input."""
        return self.solver_mode.get_guess_and_result()

    def display_current_strategy(self, strategy_name: str) -> None:
        """Display information about the current strategy."""
        self.solver_mode.display_strategy_info(strategy_name)

    def display_available_strategies(self) -> None:
        """Display table of all available strategies."""
        self.display.display_available_strategies()

    def get_strategy_selection(
        self, current_strategy: Optional[str] = None
    ) -> Optional[str]:
        """Handle strategy selection workflow."""
        return self.solver_mode.handle_strategy_selection(current_strategy)

    def display_suggestions(
        self,
        suggestions: List[str],
        remaining_words_count: int,
        common_words: Optional[List[str]] = None,
        strategy_name: Optional[str] = None,
    ) -> None:
        """Display word suggestions to the user."""
        self.solver_mode.display_suggestions(
            suggestions, remaining_words_count, common_words, strategy_name
        )

    # Play mode methods
    def display_play_mode_start(self, game_id: str, difficulty_hint: str = "") -> None:
        """Display play mode start screen."""
        self.play_mode.start_mode(game_id, difficulty_hint)

    def get_guess_input(
        self,
        prompt_text: str = "Enter your guess (5-letter word) or type 'hint' for suggestions:",
        word_manager: Optional[WordManager] = None,
    ) -> str:
        """Get a guess from the user."""
        return self.play_mode.get_guess_input(word_manager, prompt_text)

    def display_guess_result(
        self, guess: str, result: str, attempt: int, max_attempts: int
    ) -> None:
        """Display the result of a guess."""
        self.play_mode.display_guess_result(guess, result, attempt, max_attempts)

    def display_game_over(
        self,
        won: bool,
        target_word: str,
        attempt: int,
        max_attempts: int,
        game_id: str,
        guesses: Optional[List[tuple]] = None,
    ) -> None:
        """Display game over information."""
        self.play_mode.display_game_over(won, attempt, target_word, guesses)

    # Review mode methods
    def display_review_mode_start(self) -> None:
        """Display review mode start screen."""
        self.review_mode.start_mode()

    def display_games_list(
        self, games: List[dict], page: int, total_pages: int
    ) -> None:
        """Display a paginated list of games."""
        self.review_mode.display_games_list(games, page, total_pages)

    def display_detailed_game_review(self, game: dict) -> None:
        """Display detailed review of a specific game."""
        self.review_mode.display_detailed_game_review(game)

    def get_navigation_input(self) -> str:
        """Get navigation input from user in review mode."""
        return self.review_mode.get_navigation_input()

    # Additional review mode methods for backward compatibility
    def display_game_list(self, games: List[dict], page: int, total_pages: int) -> None:
        """Display a list of games (backward compatibility alias)."""
        self.display_games_list(games, page, total_pages)

    def get_game_review_action(self, current_page: int, total_pages: int) -> str:
        """Get user action for game review navigation."""
        # Display navigation options based on current page
        options = ["q = Quit"]

        if current_page > 1:
            options.append("p = Previous page")
        if current_page < total_pages:
            options.append("n = Next page")

        options.append("Enter Game ID to review specific game")

        self.display_info("Options: " + ", ".join(options))

        while True:
            action = (
                self.input_handler.get_simple_input(
                    f"Choose action (Page {current_page}/{total_pages}):"
                )
                .lower()
                .strip()
            )

            # Valid single character commands
            if action in ["q", "n", "p"]:
                return action

            # Check if it's a valid game ID (6 alphanumeric characters)
            if len(action) == 6 and action.isalnum():
                return action.upper()

            # Invalid input, show error and retry
            self.display_error(
                "Invalid input. Please enter q, n, p, or a 6-character Game ID."
            )

    def simulate_game_display(self, game: dict) -> None:
        """Simulate the display of a complete game."""
        self.review_mode.display_detailed_game_review(game)
        self.input_handler.get_continue_prompt()

    def ask_play_again(self) -> bool:
        """Ask user if they want to play again."""
        return self.get_confirmation(
            "Would you like to play another game?", default=True
        )

    def display_game_stats(self, stats: dict) -> None:
        """Display game statistics."""
        self.review_mode.display_statistics_summary(stats)

    def display_guess_history(self, guesses: List[tuple]) -> None:
        """Display the history of guesses made in a game."""
        self.display_info("Guess History:")
        for i, guess_data in enumerate(guesses, 1):
            if len(guess_data) >= 3:
                guess, result, method = guess_data[0], guess_data[1], guess_data[2]
                self.display_info(f"  {i}. {guess} -> {result} (using {method})")
            elif len(guess_data) >= 2:
                guess, result = guess_data[0], guess_data[1]
                self.display_info(f"  {i}. {guess} -> {result}")

    # Shared utility methods
    def display_error(self, message: str) -> None:
        """Display an error message."""
        self.display.display_error(message)

    def display_success(self, message: str) -> None:
        """Display a success message."""
        self.display.display_success(message)

    def display_info(self, message: str) -> None:
        """Display an informational message."""
        self.display.display_info(message)

    def get_confirmation(self, prompt_text: str, default: bool = False) -> bool:
        """Get yes/no confirmation from user."""
        return self.input_handler.get_confirmation(prompt_text, default)

    def get_continue_prompt(
        self, prompt_text: str = "\n[dim]Press Enter to continue...[/dim]"
    ) -> str:
        """Get user input to continue."""
        return self.input_handler.get_continue_prompt(prompt_text)

    # Configuration methods
    def update_display_config(self, config: DisplayConfig) -> None:
        """Update display configuration."""
        self.config = config
        self.display.update_config(config)

    def set_show_hints(self, show_hints: bool) -> None:
        """Enable or disable hint display."""
        self.config.show_hints = show_hints
        self.display.update_config(self.config)

    def set_max_suggestions(self, max_suggestions: int) -> None:
        """Set maximum number of suggestions to display."""
        self.config.max_suggestions = max_suggestions
        self.display.update_config(self.config)

    # Backward compatibility methods for gradual migration
    def _validate_input_guess(
        self, guess: str, word_manager: Optional[WordManager] = None
    ) -> None:
        """Backward compatibility method - validation is now handled in InputHandler."""
        # This method exists for compatibility but validation is now centralized
        from .validators import InputValidator

        validation = InputValidator.validate_guess(guess, word_manager)
        if not validation.is_valid:
            from src.modules.backend.exceptions import InvalidGuessError

            raise InvalidGuessError(guess, validation.error_message)

    def _colorize_result(self, guess: str, result: str):
        """Backward compatibility method - formatting is now handled in TextFormatter."""
        from .formatters import TextFormatter

        return TextFormatter.colorize_guess_result(guess, result)

    # Advanced functionality
    def handle_hint_request(
        self,
        mode: str,
        suggestions: List[str],
        remaining_words_count: int,
        common_words: Optional[List[str]] = None,
        strategy_name: Optional[str] = None,
    ) -> None:
        """Handle hint requests based on current mode."""
        if mode == "solver":
            self.solver_mode.handle_hint_request(
                suggestions, remaining_words_count, common_words, strategy_name
            )
        elif mode == "play":
            self.play_mode.handle_hint_request(
                suggestions, remaining_words_count, common_words, strategy_name
            )

    def handle_strategy_request(
        self, current_strategy: Optional[str] = None
    ) -> Optional[str]:
        """Handle strategy change requests."""
        return self.get_strategy_selection(current_strategy)
