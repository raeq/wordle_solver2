"""
Custom exception classes for the Wordle Solver application.
This module defines specialized exceptions for different error conditions in the game.
"""


class WordleError(Exception):
    """Base class for all Wordle-related exceptions."""
    pass


class GameStateError(WordleError):
    """Raised when an operation is attempted in an invalid game state."""
    pass


class InvalidGuessError(WordleError):
    """Raised when a guess is invalid."""
    def __init__(self, guess: str, reason: str):
        self.guess = guess
        self.reason = reason
        super().__init__(f"Invalid guess '{guess}': {reason}")


class InvalidWordError(InvalidGuessError):
    """Raised when a word is not in the word list."""
    def __init__(self, word: str):
        super().__init__(word, "not in the word list")


class InvalidResultError(WordleError):
    """Raised when a result pattern is invalid."""
    def __init__(self, result: str, reason: str):
        self.result = result
        self.reason = reason
        super().__init__(f"Invalid result '{result}': {reason}")


class InvalidColorError(WordleError):
    """Raised when an invalid color character is used."""
    def __init__(self, char: str):
        self.char = char
        super().__init__(f"Invalid color character: '{char}'. Use G, Y, or B.")


class InputLengthError(WordleError):
    """Raised when input is not the correct length."""
    def __init__(self, input_type: str, actual_length: int, expected_length: int = 5):
        self.input_type = input_type
        self.actual_length = actual_length
        self.expected_length = expected_length
        super().__init__(f"{input_type} must be exactly {expected_length} characters (got {actual_length})")
