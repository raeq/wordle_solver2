# src/modules/backend/solver/solver_strategy.py
"""
Strategy pattern implementation for Wordle solver algorithms.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from src.modules.backend.word_manager import WordManager


class SolverStrategy(ABC):
    """Abstract base class for Wordle solver strategies."""

    @abstractmethod
    def get_top_suggestions(
        self,
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: List[Tuple[str, str]],
        count: int = 10,
        word_manager: Optional["WordManager"] = None,
    ) -> List[str]:
        """
        Get top N suggestions based on the strategy's algorithm.

        Args:
            possible_words: List of possible valid words that match constraints
            common_words: List of common words from the possible words
            guesses_so_far: List of (guess, result) tuples representing game history
            count: Number of suggestions to return
            word_manager: WordManager instance for accessing word data

        Returns:
            List of suggested words, ordered by preference
        """
        raise NotImplementedError("Subclasses must implement get_top_suggestions")
