"""
Centralized imports and type definitions for the Wordle Solver.
This module helps eliminate circular imports and provides a single point for common types.
"""

from enum import Enum
from typing import List, Optional, Protocol, Tuple, runtime_checkable

# Import the canonical ResultColor from backend module

# Core game types
GuessResult = Tuple[str, str]  # (guess, result_pattern)
GuessHistory = List[GuessResult]


# Strategy protocol for better type safety
@runtime_checkable
class SolverStrategyProtocol(Protocol):
    """Protocol defining the interface for solver strategies."""

    def get_top_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: GuessHistory,
        count: int = 10,
        word_manager: Optional["WordManagerProtocol"] = None,
    ) -> List[str]:
        """Get top N suggestions based on the strategy's algorithm."""
        ...


@runtime_checkable
class WordManagerProtocol(Protocol):
    """Protocol defining the interface for word management."""

    def get_all_words(self) -> List[str]:
        """Get all valid words."""
        ...

    def get_common_words(self) -> List[str]:
        """Get common words subset."""
        ...

    def is_valid_word(self, word: str) -> bool:
        """Check if word is valid."""
        ...


# Game state types
class GameMode(Enum):
    """Available game modes."""

    SOLVER = "solver"
    PLAYER = "player"


class GameOutcome(Enum):
    """Possible game outcomes."""

    WON = "won"
    LOST = "lost"
    IN_PROGRESS = "in_progress"
