# src/frontend/cli/validators.py
"""
Input validation logic for the CLI interface.
"""

from typing import Optional

from src.modules.backend.result_color import ResultColor
from src.modules.backend.word_manager import WordManager

from .constants import GAME_MODES, SPECIAL_COMMANDS
from .types import UserInput, ValidationResult


class InputValidator:
    """Handles validation of user inputs."""

    @staticmethod
    def validate_guess(
        guess: str, word_manager: Optional[WordManager] = None
    ) -> ValidationResult:
        """Validate a guess input."""
        try:
            # Check length
            if len(guess) != 5:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Guess must be exactly 5 letters, got {len(guess)}",
                )

            # Check if alphabetic
            if not guess.isalpha():
                return ValidationResult(
                    is_valid=False, error_message="Guess must contain only letters"
                )

            normalized_guess = guess.upper()

            # Check if valid word (if word manager provided)
            if word_manager and not word_manager.is_valid_word(normalized_guess):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"'{normalized_guess}' is not a valid word",
                )

            return ValidationResult(is_valid=True, normalized_value=normalized_guess)

        except Exception as e:
            return ValidationResult(
                is_valid=False, error_message=f"Validation error: {str(e)}"
            )

    @staticmethod
    def validate_result(result: str) -> ValidationResult:
        """Validate a result string."""
        try:
            # Check length
            if len(result) != 5:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Result must be exactly 5 characters, got {len(result)}",
                )

            # Check if valid result characters
            if not ResultColor.is_valid_result_string(result):
                green = ResultColor.GREEN.value
                yellow = ResultColor.YELLOW.value
                black = ResultColor.BLACK.value
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Result must contain only {green}, {yellow}, or {black} characters",
                )

            return ValidationResult(is_valid=True, normalized_value=result.upper())

        except Exception as e:
            return ValidationResult(
                is_valid=False, error_message=f"Validation error: {str(e)}"
            )

    @staticmethod
    def validate_game_mode(mode: str) -> ValidationResult:
        """Validate game mode selection."""
        normalized_mode = mode.lower().strip()

        # Check direct mode names
        if normalized_mode in GAME_MODES.values():
            return ValidationResult(is_valid=True, normalized_value=normalized_mode)

        # Check numeric choices
        mode_mapping = {
            "1": GAME_MODES["SOLVER"],
            "2": GAME_MODES["PLAY"],
            "3": GAME_MODES["REVIEW"],
            "4": GAME_MODES["CLEAR"],
        }

        if normalized_mode in mode_mapping:
            return ValidationResult(
                is_valid=True, normalized_value=mode_mapping[normalized_mode]
            )

        return ValidationResult(
            is_valid=False,
            error_message=f"Invalid game mode: {mode}. Choose 1-4, solver, play, review, or clear.",
        )

    @staticmethod
    def parse_user_input(raw_input: str) -> UserInput:
        """Parse raw user input and identify special commands."""
        cleaned_input = raw_input.strip().upper()

        # Check for special commands
        if cleaned_input in SPECIAL_COMMANDS.values():
            return UserInput(
                raw_input=raw_input, command=cleaned_input, is_special_command=True
            )

        return UserInput(raw_input=raw_input, command=None, is_special_command=False)

    @staticmethod
    def parse_guess_and_result(user_input: str) -> ValidationResult:
        """Parse and validate guess and result from combined input."""
        try:
            # Handle special case for winning result
            if user_input.strip().upper() == "GGGGG":
                green = ResultColor.GREEN.value
                return ValidationResult(
                    is_valid=True, normalized_value=f"SOLVE {green * 5}"
                )

            # Handle solve format
            if user_input.upper().startswith("SOLVE "):
                parts = user_input.split()
                if len(parts) == 2:
                    result_validation = InputValidator.validate_result(parts[1])
                    if result_validation.is_valid:
                        return ValidationResult(
                            is_valid=True,
                            normalized_value=f"SOLVE {result_validation.normalized_value}",
                        )
                    else:
                        return result_validation

            # Split input into guess and result parts
            parts = user_input.split()
            if len(parts) != 2:
                return ValidationResult(
                    is_valid=False,
                    error_message="Input must follow 'GUESS RESULT' format (e.g., 'AUDIO GYBGG')",
                )

            guess, result = parts

            # Validate guess
            guess_validation = InputValidator.validate_guess(guess)
            if not guess_validation.is_valid:
                return guess_validation

            # Validate result
            result_validation = InputValidator.validate_result(result)
            if not result_validation.is_valid:
                return result_validation

            return ValidationResult(
                is_valid=True,
                normalized_value=f"{guess_validation.normalized_value} {result_validation.normalized_value}",
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False, error_message=f"Parse error: {str(e)}"
            )

    @staticmethod
    def validate_strategy(
        strategy: str, available_strategies: list
    ) -> ValidationResult:
        """Validate strategy selection."""
        normalized_strategy = strategy.lower().strip()

        if not normalized_strategy:
            return ValidationResult(
                is_valid=True, normalized_value=None  # Keep current strategy
            )

        if normalized_strategy in available_strategies:
            return ValidationResult(is_valid=True, normalized_value=normalized_strategy)

        return ValidationResult(
            is_valid=False,
            error_message=f"Invalid strategy: {strategy}. Available: {', '.join(available_strategies)}",
        )
