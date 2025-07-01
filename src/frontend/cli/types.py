# src/frontend/cli/types.py
"""
Type definitions for the CLI module.
"""

from dataclasses import dataclass
from typing import Optional, Protocol

# Basic type aliases
GameMode = str
Strategy = str
Guess = str
Result = str
Command = str


# Input validation result
@dataclass
class ValidationResult:
    """Result of input validation."""

    is_valid: bool
    error_message: Optional[str] = None
    normalized_value: Optional[str] = None


# User input types
@dataclass
class UserInput:
    """Represents user input with metadata."""

    raw_input: str
    command: Optional[str] = None
    is_special_command: bool = False


@dataclass
class GuessResult:
    """Represents a guess and its result."""

    guess: str
    result: str
    attempt: int
    method: Optional[str] = None


# Display configuration
@dataclass
class DisplayConfig:
    """Configuration for display components."""

    show_hints: bool = True
    show_strategy_info: bool = True
    show_common_words: bool = True
    max_suggestions: int = 10


# Game state for display
@dataclass
class GameDisplayState:
    """Current game state for display purposes."""

    mode: GameMode
    attempt: int
    max_attempts: int
    remaining_words: int
    current_strategy: Optional[str] = None
    game_id: Optional[str] = None


# Strategy selection result
@dataclass
class StrategySelection:
    """Result of strategy selection."""

    strategy: Optional[str]
    keep_current: bool = False


# Protocol for console-like objects (for testing)
class ConsoleProtocol(Protocol):
    """Protocol for console objects."""

    def print(self, *args, **kwargs) -> None: ...


class PromptProtocol(Protocol):
    """Protocol for prompt objects."""

    @staticmethod
    def ask(prompt: str, **kwargs) -> str: ...


class ConfirmProtocol(Protocol):
    """Protocol for confirm objects."""

    @staticmethod
    def ask(prompt: str, **kwargs) -> bool: ...
