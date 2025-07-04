"""
Wordle Solver Package

A command-line application that helps solve Wordle puzzles by suggesting
optimal guesses based on previous attempts and their results.
Now includes a play mode where you can play against the computer!
"""

# Import new modular structure instead of old direct imports
from .frontend.cli import CLIInterface, GameStateManager
from .modules.backend.game_engine import GameEngine
from .modules.backend.solver.constants import (
    VERSION_MAJOR,
    VERSION_MINOR,
    VERSION_PATCH,
)
from .modules.backend.stateless_word_manager import StatelessWordManager
from .modules.backend.stats_manager import StatsManager
from .modules.enhanced_app import EnhancedWordleSolverApp

# Add backward compatibility alias
WordManager = StatelessWordManager  # Alias for backward compatibility

__version__ = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
__author__ = "Richard Quinn"

__all__ = [
    "StatelessWordManager",
    "WordManager",  # Include alias in exports
    "GameStateManager",
    "GameEngine",
    "EnhancedWordleSolverApp",  # Add to fix F401 error
    "StatsManager",
    "CLIInterface",
]
