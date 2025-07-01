# src/frontend/cli/game_modes/play_mode.py
"""
Play mode specific UI components and interactions.
"""

from typing import List, Optional

from src.modules.backend.word_manager import WordManager

from ..display import DisplayManager
from ..input_handler import InputHandler


class PlayModeHandler:
    """Handles UI interactions specific to play mode."""

    def __init__(self, display: DisplayManager, input_handler: InputHandler):
        """Initialize play mode handler."""
        self.display = display
        self.input_handler = input_handler

    def start_mode(self, game_id: str, difficulty_hint: str = "") -> None:
        """Display play mode start screen."""
        self.display.display_mode_start(
            "play", game_id=game_id, difficulty_hint=difficulty_hint
        )

    def get_guess_input(
        self,
        word_manager: Optional[WordManager] = None,
        custom_prompt: Optional[str] = None,
    ) -> str:
        """Get guess input from user for play mode."""
        prompt = (
            custom_prompt
            or "Enter your guess (5-letter word) or type 'hint' for suggestions:"
        )
        return self.input_handler.get_guess_input(prompt, word_manager)

    def display_guess_result(
        self, guess: str, result: str, attempt: int, max_attempts: int = 6
    ) -> None:
        """Display the result of a guess in play mode."""
        self.display.display_guess_result(guess, result, attempt, max_attempts)

    def display_game_over(
        self,
        won: bool,
        attempts: int,
        target_word: str,
        guesses: Optional[List[tuple]] = None,
    ) -> None:
        """Display game over screen for play mode."""
        self.display.display_game_over(won, attempts, target_word, guesses)

    def handle_hint_request(
        self,
        suggestions: List[str],
        remaining_words_count: int,
        common_words: Optional[List[str]] = None,
        strategy_name: Optional[str] = None,
    ) -> None:
        """Handle hint request in play mode."""
        if suggestions:
            self.display.display_info("Here are some suggestions to help you:")
            self.display.display_suggestions(
                suggestions[:5],  # Limit hints in play mode
                remaining_words_count,
                common_words,
                strategy_name,
            )
        else:
            self.display.display_info(
                "No suggestions available with current constraints."
            )

    def display_attempt_info(self, attempt: int, max_attempts: int = 6) -> None:
        """Display current attempt information."""
        remaining = max_attempts - attempt + 1
        if remaining > 1:
            self.display.display_info(
                f"Attempt {attempt}/{max_attempts} - {remaining} attempts remaining"
            )
        else:
            self.display.display_info(
                f"Attempt {attempt}/{max_attempts} - Last chance!"
            )

    def get_play_again_confirmation(self) -> bool:
        """Ask user if they want to play again."""
        return self.input_handler.get_confirmation(
            "Would you like to play another game?", default=True
        )

    def display_difficulty_info(self, difficulty: str) -> None:
        """Display difficulty information."""
        difficulty_messages = {
            "easy": "🟢 Easy mode: Common 5-letter words",
            "medium": "🟡 Medium mode: Mix of common and uncommon words",
            "hard": "🔴 Hard mode: Challenging and obscure words",
        }

        message = difficulty_messages.get(
            difficulty.lower(), f"Difficulty: {difficulty}"
        )
        self.display.display_info(message)

    def continue_prompt(self) -> None:
        """Show continue prompt after game over."""
        self.input_handler.get_continue_prompt()
