# src/modules/backend/game_state_manager.py
"""
Module containing the game state management for Wordle solver.
"""
from typing import Dict, List, Optional, Tuple

from ..logging_utils import set_game_id
from .result_color import ResultColor
from .solver.hybrid_frequency_entropy_strategy import HybridFrequencyEntropyStrategy
from .solver.solver_strategy import SolverStrategy
from .word_manager import WordManager


class GameStateManager:
    """Manages the game state and delegates word suggestions to strategies."""

    def __init__(
        self, word_manager: WordManager, strategy: Optional[SolverStrategy] = None
    ):
        self.word_manager = word_manager
        self.guesses: List[Tuple[str, str]] = []  # (guess, result) pairs
        self.max_guesses = 6
        # Default to hybrid strategy if none provided
        self.strategy = strategy or HybridFrequencyEntropyStrategy()

    def set_strategy(self, strategy: SolverStrategy) -> None:
        """Change the solver strategy."""
        self.strategy = strategy

    def get_strategy_name(self) -> str:
        """Get the name of the current strategy."""
        strategy_class_name = self.strategy.__class__.__name__
        # Convert class name to strategy name (e.g., "EntropyStrategy" -> "entropy")
        name_mapping = {
            "FrequencyStrategy": "frequency",
            "EntropyStrategy": "entropy",
            "MinimaxStrategy": "minimax",
            "TwoStepStrategy": "two_step",
            "WeightedGainStrategy": "weighted_gain",
            "HybridFrequencyEntropyStrategy": "hybrid",
        }
        return name_mapping.get(strategy_class_name, strategy_class_name.lower())

    def add_guess(self, guess: str, result: str) -> None:
        """Add a guess and its result to the history and filter words."""
        guess = guess.upper()
        result = result.upper()
        self.guesses.append((guess, result))
        self.word_manager.filter_words(guess, result)

    def suggest_next_guess(self) -> str:
        """Suggest the next best guess using the current strategy."""
        suggestions = self.get_top_suggestions(1)
        return suggestions[0] if suggestions else "No valid words remaining"

    def get_top_suggestions(self, count: int = 10) -> List[str]:
        """Get top N suggestions using the current strategy."""
        possible_words = self.word_manager.get_possible_words()
        common_words = self.word_manager.get_common_possible_words()

        if not possible_words:
            return []

        if len(possible_words) <= count:
            # If we have few words left, prioritize common ones first
            other_possible = [w for w in possible_words if w not in common_words]
            return common_words + other_possible

        # Use the strategy to get suggestions, passing the word_manager for frequency/entropy data
        return self.strategy.get_top_suggestions(
            possible_words, common_words, self.guesses, count, self.word_manager
        )

    def get_remaining_guesses(self) -> int:
        """Get number of remaining guesses."""
        return self.max_guesses - len(self.guesses)

    def is_game_won(self) -> bool:
        """Check if the game has been won."""
        return bool(self.guesses) and self.guesses[-1][1] == ResultColor.GREEN.value * 5

    def is_game_over(self) -> bool:
        """Check if the game is over (won or max guesses reached)."""
        return self.is_game_won() or len(self.guesses) >= self.max_guesses

    def reset(self) -> None:
        """Reset the solver for a new game."""
        self.guesses = []
        self.word_manager.reset()  # Reset the word manager's possible_words list

        # Clear the game ID from the logging context
        set_game_id(None)  # Reset the game ID to None

    def get_game_state(self) -> Dict[str, object]:
        """Get current game state."""
        return {
            "guesses_made": len(self.guesses),
            "guesses_remaining": self.get_remaining_guesses(),
            "possible_words_count": len(self.word_manager.get_possible_words()),
            "is_game_won": self.is_game_won(),
            "is_game_over": self.is_game_over(),
            "guesses_history": self.guesses.copy(),
        }
