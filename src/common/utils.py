"""
Common utilities for error handling and validation across the Wordle Solver.
"""

from functools import wraps
from typing import Callable, TypeVar

from src.modules.backend.exceptions import (
    InvalidGuessError,
    InvalidResultError,
    WordleError,
)
from src.modules.backend.result_color import ResultColor

T = TypeVar("T")


def validate_word_input(word: str, word_length: int = 5) -> str:
    """
    Validate word input ensuring it meets Wordle requirements.

    Args:
        word: The word to validate
        word_length: Expected word length (default: 5)

    Returns:
        The validated and normalized word (uppercase)

    Raises:
        InvalidGuessError: If the word is invalid
    """
    if not word:
        raise InvalidGuessError(word, "cannot be empty")

    # Normalize to uppercase
    word = word.upper().strip()

    if len(word) != word_length:
        raise InvalidGuessError(word, f"must be exactly {word_length} characters")

    if not word.isalpha():
        raise InvalidGuessError(word, "must contain only letters")

    return word


def validate_result_pattern(result: str, expected_length: int = 5) -> str:
    """
    Validate result pattern ensuring it contains only valid color codes.

    Args:
        result: The result pattern to validate
        expected_length: Expected pattern length (default: 5)

    Returns:
        The validated and normalized result pattern (uppercase)

    Raises:
        InvalidResultError: If the result pattern is invalid
    """
    if not result:
        raise InvalidResultError(result, "cannot be empty")

    # Normalize to uppercase
    result = result.upper().strip()

    if len(result) != expected_length:
        raise InvalidResultError(
            result, f"must be exactly {expected_length} characters"
        )

    if not ResultColor.is_valid_result_string(result):
        valid_chars = [color.value for color in ResultColor]
        raise InvalidResultError(result, f"must contain only {', '.join(valid_chars)}")

    return result


def safe_execute(operation_name: str = "operation"):
    """
    Decorator to safely execute operations and handle common exceptions.

    Args:
        operation_name: Name of the operation for error messages
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except WordleError:
                # Re-raise Wordle-specific errors as they're already properly formatted
                raise
            except Exception as e:
                # Wrap unexpected errors with proper exception chaining
                raise WordleError(
                    f"Unexpected error in {operation_name}: {str(e)}"
                ) from e

        return wrapper

    return decorator


def format_guess_history(guesses_history: list) -> str:
    """
    Format guess history for display purposes.

    Args:
        guesses_history: List of [guess, result, strategy] tuples

    Returns:
        Formatted string representation of the guess history
    """
    if not guesses_history:
        return "No guesses made."

    lines = ["Guess History:"]
    for i, guess_data in enumerate(guesses_history, 1):
        if len(guess_data) >= 3:
            guess, result, strategy = guess_data[:3]
            lines.append(f"{i:2d}. {guess} -> {result} (using {strategy})")
        else:
            guess, result = guess_data[:2]
            lines.append(f"{i:2d}. {guess} -> {result}")

    return "\n".join(lines)


def calculate_success_metrics(guesses_history: list, won: bool) -> dict:
    """
    Calculate various success metrics from guess history.

    Args:
        guesses_history: List of guess attempts
        won: Whether the game was won

    Returns:
        Dictionary containing success metrics
    """
    total_attempts = len(guesses_history)

    metrics = {
        "total_attempts": total_attempts,
        "won": won,
        "success_rate": 1.0 if won else 0.0,
        "efficiency_score": 0.0,
    }

    if won and total_attempts > 0:
        # Calculate efficiency (6 attempts is max, 1 is perfect)
        metrics["efficiency_score"] = (7 - total_attempts) / 6.0

    return metrics
