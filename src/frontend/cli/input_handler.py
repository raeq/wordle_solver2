# src/frontend/cli/input_handler.py
"""
Input handling and user interaction for the CLI interface.
Centralizes all user input operations and validation.
"""

from typing import Optional, Tuple

from rich.prompt import Confirm, Prompt

# Import StrategyFactory from the centralized __init__.py
from src.modules.backend.solver import StrategyFactory
from src.modules.backend.word_manager import WordManager

from .constants import DEFAULT_PROMPTS, SPECIAL_COMMANDS
from .formatters import MessageFormatter, TextFormatter
from .types import ConfirmProtocol, PromptProtocol
from .validators import InputValidator


class InputHandler:
    """Handles all user input operations with validation."""

    def __init__(
        self,
        prompt_handler: Optional[PromptProtocol] = None,
        confirm_handler: Optional[ConfirmProtocol] = None,
    ):
        """Initialize input handler with optional prompt injection for testing."""
        self.prompt = prompt_handler or Prompt
        self.confirm = confirm_handler or Confirm

    def get_game_mode(self) -> str:
        """Get game mode selection from user."""
        while True:
            choice = self.prompt.ask(
                DEFAULT_PROMPTS["game_mode"],
                choices=["1", "2", "3", "4", "solver", "play", "review", "clear"],
                default="1",
            )

            validation = InputValidator.validate_game_mode(choice)
            if validation.is_valid:
                return validation.normalized_value

            # This shouldn't happen with choices, but just in case
            print(TextFormatter.format_error_message(validation.error_message))

    def get_guess_input(
        self,
        prompt_text: str = DEFAULT_PROMPTS["guess_input"],
        word_manager: Optional[WordManager] = None,
    ) -> str:
        """Get a guess from the user with validation."""
        formatted_prompt = TextFormatter.format_prompt(prompt_text)

        while True:
            raw_input = self.prompt.ask(formatted_prompt).upper()
            user_input = InputValidator.parse_user_input(raw_input)

            # Handle special commands
            if user_input.is_special_command:
                return user_input.command

            # Validate guess
            validation = InputValidator.validate_guess(raw_input, word_manager)
            if validation.is_valid:
                return validation.normalized_value

            print(TextFormatter.format_error_message(validation.error_message))

    def get_guess_and_result(self) -> Tuple[str, str]:
        """Get guess and result from user input with validation."""
        example = MessageFormatter.format_example_input()
        prompt_text = DEFAULT_PROMPTS["guess_and_result"].format(example=example)
        formatted_prompt = TextFormatter.format_prompt(prompt_text)

        while True:
            raw_input = self.prompt.ask(formatted_prompt).upper()
            user_input = InputValidator.parse_user_input(raw_input)

            # Handle special commands
            if user_input.is_special_command:
                return user_input.command, ""

            # Special case for just result colors (winning pattern)
            if raw_input.strip() == "GGGGG":
                from src.modules.backend.result_color import ResultColor

                green = ResultColor.GREEN.value
                return "SOLVE", green * 5

            # Parse and validate combined input
            validation = InputValidator.parse_guess_and_result(raw_input)
            if validation.is_valid:
                parts = validation.normalized_value.split()
                if len(parts) == 2:
                    return parts[0], parts[1]
                elif validation.normalized_value.startswith("SOLVE "):
                    return "SOLVE", validation.normalized_value.split()[1]

            print(TextFormatter.format_error_message(validation.error_message))

    def get_strategy_selection(
        self, current_strategy: Optional[str] = None
    ) -> Optional[str]:
        """Get strategy selection from user."""
        available_strategies = StrategyFactory.get_available_strategies()

        prompt_text = DEFAULT_PROMPTS["strategy_selection"]
        prompt_text += f" ({', '.join(available_strategies)})"

        if current_strategy:
            prompt_text += f" or press Enter to keep [cyan]{current_strategy}[/cyan]"

        while True:
            choice = self.prompt.ask(
                prompt_text, default=current_strategy if current_strategy else ""
            )

            validation = InputValidator.validate_strategy(choice, available_strategies)
            if validation.is_valid:
                return validation.normalized_value

            print(TextFormatter.format_error_message(validation.error_message))

    def get_confirmation(self, prompt_text: str, default: bool = False) -> bool:
        """Get yes/no confirmation from user."""
        formatted_prompt = TextFormatter.format_prompt(prompt_text)
        return self.confirm.ask(formatted_prompt, default=default)

    def get_continue_prompt(
        self, prompt_text: str = DEFAULT_PROMPTS["continue"]
    ) -> str:
        """Get user input to continue (typically just Enter)."""
        return self.prompt.ask(prompt_text, default="")

    def get_simple_input(self, prompt_text: str, default: str = "") -> str:
        """Get simple string input from user."""
        formatted_prompt = TextFormatter.format_prompt(prompt_text)
        return self.prompt.ask(formatted_prompt, default=default)

    def get_choice_input(
        self, prompt_text: str, choices: list, default: Optional[str] = None
    ) -> str:
        """Get input from a list of choices."""
        formatted_prompt = TextFormatter.format_prompt(prompt_text)
        return self.prompt.ask(formatted_prompt, choices=choices, default=default)

    def handle_special_command(self, command: str) -> str:
        """Process special commands and return the command type."""
        if command in SPECIAL_COMMANDS.values():
            return command
        return ""

    def validate_and_get_input(
        self, prompt_text: str, validator_func, error_handler=None, max_retries: int = 3
    ) -> Optional[str]:
        """Generic method for validated input with retry logic."""
        formatted_prompt = TextFormatter.format_prompt(prompt_text)

        for attempt in range(max_retries):
            try:
                raw_input = self.prompt.ask(formatted_prompt)
                validation = validator_func(raw_input)

                if validation.is_valid:
                    return validation.normalized_value

                error_msg = validation.error_message
                if error_handler:
                    error_handler(error_msg)
                else:
                    print(TextFormatter.format_error_message(error_msg))

            except KeyboardInterrupt:
                return None
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                if error_handler:
                    error_handler(error_msg)
                else:
                    print(TextFormatter.format_error_message(error_msg))

        print(
            TextFormatter.format_error_message(f"Max retries ({max_retries}) exceeded")
        )
        return None
