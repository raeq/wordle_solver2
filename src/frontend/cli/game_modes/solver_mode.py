# src/frontend/cli/game_modes/solver_mode.py
"""
Solver mode specific UI components and interactions.
"""

from typing import List, Optional, Tuple

# Import StrategyFactory and SolverStrategy from the centralized __init__.py
from src.modules.backend.solver import StrategyFactory
from src.modules.backend.stateless_word_manager import StatelessWordManager

from ..display import DisplayManager
from ..game_state_manager import GameStateManager
from ..input_handler import InputHandler


class SolverModeHandler:
    """Handles UI interactions specific to solver mode."""

    def __init__(
        self,
        display: DisplayManager,
        input_handler: InputHandler,
        word_manager: Optional[StatelessWordManager] = None,
    ):
        """Initialize solver mode handler.

        Args:
            display: Display manager for UI output
            input_handler: Input handler for user input
            word_manager: Optional stateless word manager instance
        """
        self.display = display
        self.input_handler = input_handler

        # Initialize with a stateless word manager if not provided
        if word_manager is None:
            word_manager = StatelessWordManager()

        # Create game state manager to maintain game state and strategy
        self.game_state = GameStateManager(word_manager)
        self.strategy_factory = StrategyFactory()

    def reset(self) -> None:
        """Reset the solver mode state."""
        self.game_state.reset()

    def start_mode(self) -> None:
        """Display solver mode start screen."""
        self.display.display_mode_start("solver")

        # Reset game state when starting a new solver session
        self.reset()

    def get_guess_and_result(self) -> Tuple[str, str]:
        """Get guess and result input from user for solver mode."""
        return self.input_handler.get_guess_and_result()

    def add_constraint(self, guess: str, result: str) -> None:
        """Add a new guess-result constraint.

        Args:
            guess: The guessed word
            result: The result pattern (G/Y/B for Green/Yellow/Black)
        """
        self.game_state.add_guess(guess, result)

    def get_suggestions(
        self, strategy_name: str, limit: int = 10
    ) -> Tuple[List[str], int, List[str]]:
        """Get word suggestions based on current constraints.

        Args:
            strategy_name: Name of the strategy to use
            limit: Maximum number of suggestions to return

        Returns:
            Tuple of (suggestions, total possible words count, common possible words)
        """
        # Get all possible words based on current constraints
        possible_words = self.game_state.get_possible_words()
        possible_words_count = len(possible_words)

        # Get common possible words
        common_possible_words = self.game_state.get_common_possible_words()

        # Get strategy-based suggestions
        if strategy_name and possible_words:
            # Create or update strategy with current constraints
            if (
                self.current_strategy is None
                or self.current_strategy.name != strategy_name
            ):
                self.current_strategy = self.strategy_factory.create_strategy(
                    strategy_name, self.game_state.word_manager
                )

            # Get top suggestions based on the strategy
            suggestions = self.current_strategy.get_top_words(
                possible_words=possible_words, limit=limit
            )
        else:
            # Fall back to possible words if no strategy or no words
            suggestions = possible_words[:limit] if possible_words else []

        return suggestions, possible_words_count, common_possible_words

    def display_strategy_info(self, strategy_name: str) -> None:
        """Display current strategy information."""
        self.display.display_current_strategy(strategy_name)

    def handle_strategy_selection(
        self, current_strategy: Optional[str] = None
    ) -> Optional[str]:
        """Handle strategy selection workflow."""
        if current_strategy:
            self.display.display_strategy_selection_current(current_strategy)

        self.display.display_available_strategies()
        return self.input_handler.get_strategy_selection(current_strategy)

    def display_suggestions(
        self,
        suggestions: List[str],
        remaining_words_count: int,
        common_words: Optional[List[str]] = None,
        strategy_name: Optional[str] = None,
    ) -> None:
        """Display word suggestions for solver mode."""
        self.display.display_suggestions(
            suggestions, remaining_words_count, common_words, strategy_name
        )

    def handle_hint_request(
        self,
        suggestions: List[str],
        remaining_words_count: int,
        common_words: Optional[List[str]] = None,
        strategy_name: Optional[str] = None,
    ) -> None:
        """Handle hint request in solver mode."""
        if suggestions:
            self.display_suggestions(
                suggestions, remaining_words_count, common_words, strategy_name
            )
        else:
            self.display.display_info(
                "No suggestions available with current constraints."
            )

    def display_solver_progress(self, attempt: int, max_attempts: int = 6) -> None:
        """Display progress in solver mode."""
        progress_msg = f"Attempt {attempt}/{max_attempts}"
        self.display.display_info(progress_msg)

    def display_constraints_summary(self) -> None:
        """Display current constraints summary."""
        constraints_count = self.game_state.get_constraints_count()
        if constraints_count == 0:
            return

        summary_lines = [f"Current constraints: {constraints_count} guesses"]

        # Display previous guesses and results
        for i, (guess, result) in enumerate(self.game_state.guesses):
            summary_lines.append(f"  Guess {i+1}: {guess} - {result}")

        summary = "\n".join(summary_lines)
        self.display.display_info(summary)
