# src/frontend/cli/game_state_manager.py
"""
Game state management for the Wordle solver application.

This module maintains the state of the game including previous guesses,
results, and strategy management, allowing the frontend to work with a stateless backend.
"""
from typing import Dict, List, Optional, Tuple

from src.modules.backend.result_color import ResultColor
from src.modules.backend.solver import HybridFrequencyEntropyStrategy, SolverStrategy
from src.modules.backend.stateless_word_manager import StatelessWordManager
from src.modules.logging_utils import set_game_id


class GameStateManager:
    """
    Manages the state of a Wordle game in the frontend.

    This class keeps track of previous guesses and results, applies them
    to the stateless word manager, and manages strategy-based suggestions.
    """

    def __init__(
        self,
        word_manager: StatelessWordManager,
        strategy: Optional[SolverStrategy] = None,
        max_guesses: int = 6,
    ):
        """Initialize the game state manager.

        Args:
            word_manager: A stateless word manager instance
            strategy: Optional solver strategy (defaults to HybridFrequencyEntropyStrategy)
            max_guesses: Maximum number of guesses allowed (default: 6)
        """
        self.word_manager = word_manager
        self.guesses: List[Tuple[str, str]] = []  # (guess, result) pairs
        self.max_guesses = max_guesses

        # Default to hybrid strategy if none provided
        self.strategy = strategy or HybridFrequencyEntropyStrategy()

    def set_strategy(self, strategy: SolverStrategy) -> None:
        """Change the solver strategy.

        Args:
            strategy: The new strategy to use
        """
        self.strategy = strategy

    def get_strategy_name(self) -> str:
        """Get the name of the current strategy.

        Returns:
            String name of the current strategy
        """
        strategy_class_name = self.strategy.__class__.__name__
        # Convert class name to strategy name (e.g., "EntropyStrategy" -> "entropy")
        name_mapping = {
            "FrequencyStrategy": "frequency",
            "EntropyStrategy": "entropy",
            "MinimaxStrategy": "minimax",
            "TwoStepStrategy": "two_step",
            "WeightedGainStrategy": "weighted_gain",
            "HybridFrequencyEntropyStrategy": "hybrid",
            "StatelessFrequencyStrategy": "frequency",
            "StatelessEntropyStrategy": "entropy",
            "StatelessMinimaxStrategy": "minimax",
            "StatelessTwoStepStrategy": "two_step",
            "StatelessWeightedGainStrategy": "weighted_gain",
            "StatelessHybridStrategy": "hybrid",
        }
        return name_mapping.get(strategy_class_name, strategy_class_name.lower())

    def reset(self) -> None:
        """Reset the game state for a new game."""
        self.guesses = []

        # Clear the game ID from the logging context
        set_game_id(None)

    def add_guess(self, guess: str, result: str) -> None:
        """Add a new guess-result constraint.

        Args:
            guess: The guessed word
            result: The result pattern (G/Y/B for Green/Yellow/Black)
        """
        guess = guess.upper()
        result = result.upper()
        self.guesses.append((guess, result))

    # For backwards compatibility with older code
    def add_constraint(self, guess: str, result: str) -> None:
        """Alias for add_guess to maintain compatibility."""
        self.add_guess(guess, result)

    def get_possible_words(self) -> List[str]:
        """Get all possible words based on current constraints.

        Returns:
            List of words that match all constraints
        """
        # Use the stateless word manager to apply all constraints
        return self.word_manager.apply_multiple_constraints(self.guesses)

    def get_common_possible_words(self) -> List[str]:
        """Get common possible words based on current constraints.

        Returns:
            List of common words that match all constraints
        """
        possible_words = self.get_possible_words()
        return self.word_manager.get_common_words_from_set(set(possible_words))

    def suggest_next_guess(self) -> str:
        """Suggest the next best guess using the current strategy.

        Returns:
            The best word to guess next
        """
        suggestions = self.get_top_suggestions(1)
        return suggestions[0] if suggestions else "No valid words remaining"

    def get_top_suggestions(self, count: int = 10) -> List[str]:
        """Get top N suggestions using the current strategy.

        Args:
            count: Number of suggestions to return

        Returns:
            List of suggested words
        """
        possible_words = self.get_possible_words()
        common_words = self.get_common_possible_words()

        if not possible_words:
            return []

        if len(possible_words) <= count:
            # If we have few words left, prioritize common ones first
            other_possible = [w for w in possible_words if w not in common_words]
            return common_words + other_possible

        # Use the strategy to get suggestions
        # Check if the strategy uses the new stateless interface
        if hasattr(self.strategy, "get_top_words"):
            return self.strategy.get_top_words(
                possible_words=possible_words, limit=count
            )
        else:
            # Use the legacy strategy interface
            return self.strategy.get_top_suggestions(
                possible_words, common_words, self.guesses, count, self.word_manager
            )

    def get_constraints_count(self) -> int:
        """Get the number of constraints (guesses) so far.

        Returns:
            Number of guesses made
        """
        return len(self.guesses)

    def get_remaining_guesses(self) -> int:
        """Get number of remaining guesses.

        Returns:
            Number of guesses remaining
        """
        return self.max_guesses - len(self.guesses)

    def is_game_won(self) -> bool:
        """Check if the game has been won.

        Returns:
            True if the game has been won
        """
        return bool(self.guesses) and self.guesses[-1][1] == ResultColor.GREEN.value * 5

    def is_game_over(self) -> bool:
        """Check if the game is over (won or max guesses reached).

        Returns:
            True if the game is over
        """
        return self.is_game_won() or len(self.guesses) >= self.max_guesses

    def get_game_state(self) -> Dict[str, object]:
        """Get current game state.

        Returns:
            Dictionary with current game state information
        """
        return {
            "guesses_made": len(self.guesses),
            "guesses_remaining": self.get_remaining_guesses(),
            "possible_words_count": len(self.get_possible_words()),
            "common_words_count": len(self.get_common_possible_words()),
            "is_game_won": self.is_game_won(),
            "is_game_over": self.is_game_over(),
            "guesses": self.guesses,
            "strategy": self.get_strategy_name(),
        }
