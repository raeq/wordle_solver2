# src/frontend/cli/game_state.py
"""
Game state management for the frontend CLI application.

This module is kept for backward compatibility.
The functionality has been moved to game_state_manager.py.
"""

from typing import List, Tuple

from src.modules.backend.stateless_word_manager import StatelessWordManager

from .game_state_manager import GameStateManager as _GameStateManager


class GameState(_GameStateManager):
    """
    Maintains the state of a Wordle game in the frontend.

    This class is an alias to GameStateManager for backward compatibility.
    All the functionality has been consolidated in the GameStateManager class.
    """

    def __init__(self, word_manager: StatelessWordManager):
        """Initialize the game state.

        Args:
            word_manager: A stateless word manager instance
        """
        super().__init__(word_manager)

    # For backward compatibility, constraints is an alias to guesses
    @property
    def constraints(self) -> List[Tuple[str, str]]:
        """Get the list of constraints (alias for guesses)."""
        return self.guesses
