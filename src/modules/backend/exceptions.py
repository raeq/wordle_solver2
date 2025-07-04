"""
Custom exception classes for the Wordle Solver application.
This module defines specialized exceptions for different error conditions in the game.
"""

import inspect

import structlog

# Configure logger
logger = structlog.get_logger("wordle_solver.exceptions")


# Mixin for logging errors in debug mode
class DebugLogMixin:
    def _log_error(self, message: str) -> None:
        frame = inspect.currentframe()
        if frame is not None:
            try:
                if frame.f_back and frame.f_back.f_back:
                    frame = frame.f_back.f_back
                    calling_module = frame.f_globals.get("__name__", "unknown")
                    calling_function = frame.f_code.co_name
                    calling_lineno = frame.f_lineno
                else:
                    calling_module = "unknown"
                    calling_function = "unknown"
                    calling_lineno = 0
            except AttributeError:
                calling_module = "unknown"
                calling_function = "unknown"
                calling_lineno = 0
        else:
            calling_module = "unknown"
            calling_function = "unknown"
            calling_lineno = 0

        if logger is not None:
            logger.debug(
                "Wordle error occurred",
                error_type=self.__class__.__name__,
                message=message,
                module=calling_module,
                function=calling_function,
                line=calling_lineno,
            )


class WordleError(Exception):
    """Base class for all Wordle-related exceptions."""

    def __init__(self, message: str = ""):
        super().__init__(message)
        self._log_error(message)

    def _log_error(self, message: str) -> None:
        """Log error information using structlog."""
        # Get caller information
        frame = inspect.currentframe()
        if frame is not None:
            # Try to go back two frames to get the actual caller
            try:
                if frame.f_back and frame.f_back.f_back:
                    frame = frame.f_back.f_back
                    calling_module = frame.f_globals.get("__name__", "unknown")
                    calling_function = frame.f_code.co_name
                    calling_lineno = frame.f_lineno
                else:
                    calling_module = "unknown"
                    calling_function = "unknown"
                    calling_lineno = 0
            except AttributeError:
                calling_module = "unknown"
                calling_function = "unknown"
                calling_lineno = 0
        else:
            calling_module = "unknown"
            calling_function = "unknown"
            calling_lineno = 0

        # Log the exception with context if logger exists
        if logger is not None:
            logger.error(
                "Wordle error occurred",
                error_type=self.__class__.__name__,
                message=message,
                module=calling_module,
                function=calling_function,
                line=calling_lineno,
            )


class GameStateError(WordleError):
    """Raised when an operation is attempted in an invalid game state."""


class InvalidGuessError(DebugLogMixin, WordleError):
    """Raised when a guess is invalid."""

    def __init__(self, guess: str, reason: str):
        self.guess = guess
        self.reason = reason
        super().__init__(f"Invalid guess '{guess}': {reason}")


class InvalidWordError(InvalidGuessError):
    """Raised when a word is not in the word list."""

    def __init__(self, word: str):
        super().__init__(word, "not in the word list")


class InvalidResultError(DebugLogMixin, WordleError):
    """Raised when a result pattern is invalid."""

    def __init__(self, result: str, reason: str):
        self.result = result
        self.reason = reason
        super().__init__(f"Invalid result '{result}': {reason}")


class InvalidColorError(DebugLogMixin, WordleError):
    """Raised when an invalid color character is used."""

    def __init__(self, char: str):
        self.char = char
        super().__init__(f"Invalid color character: '{char}'. Use G, Y, or B.")


class InputLengthError(DebugLogMixin, WordleError):
    """Raised when input is not the correct length."""

    def __init__(self, input_type: str, actual_length: int, expected_length: int = 5):
        self.input_type = input_type
        self.actual_length = actual_length
        self.expected_length = expected_length
        super().__init__(
            f"{input_type} must be exactly {expected_length} characters (got {actual_length})"
        )
