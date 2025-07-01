# src/frontend/cli/game_modes/solver_mode.py
"""
Solver mode specific UI components and interactions.
"""

from typing import List, Optional, Tuple

from ..display import DisplayManager
from ..input_handler import InputHandler


class SolverModeHandler:
    """Handles UI interactions specific to solver mode."""

    def __init__(self, display: DisplayManager, input_handler: InputHandler):
        """Initialize solver mode handler."""
        self.display = display
        self.input_handler = input_handler

    def start_mode(self) -> None:
        """Display solver mode start screen."""
        self.display.display_mode_start("solver")

    def get_guess_and_result(self) -> Tuple[str, str]:
        """Get guess and result input from user for solver mode."""
        return self.input_handler.get_guess_and_result()

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

    def display_constraints_summary(self, constraints: dict) -> None:
        """Display current constraints summary."""
        if not constraints:
            return

        summary_lines = ["Current constraints:"]

        if "known_positions" in constraints and constraints["known_positions"]:
            positions = constraints["known_positions"]
            pos_str = "".join(positions.get(i, "_") for i in range(5))
            summary_lines.append(f"  Known positions: {pos_str}")

        if "required_letters" in constraints and constraints["required_letters"]:
            letters = ", ".join(sorted(constraints["required_letters"]))
            summary_lines.append(f"  Required letters: {letters}")

        if "excluded_letters" in constraints and constraints["excluded_letters"]:
            letters = ", ".join(sorted(constraints["excluded_letters"]))
            summary_lines.append(f"  Excluded letters: {letters}")

        summary = "\n".join(summary_lines)
        self.display.display_info(summary)
