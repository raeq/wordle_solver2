"""
Wordle Solver Package

A command-line application that helps solve Wordle puzzles by suggesting
optimal guesses based on previous attempts and their results.
Now includes a play mode where you can play against the computer!
"""

# Import new modular structure instead of old direct imports
from .frontend.cli_interface import CLIInterface
from .modules.app import WordleSolverApp
from .modules.backend.game_engine import GameEngine
from .modules.backend.solver import Solver
from .modules.backend.stats_manager import StatsManager
from .modules.backend.word_manager import WordManager

__version__ = "2.0.0"
__author__ = "AI Assistant"

__all__ = [
    "WordManager",
    "Solver",
    "GameEngine",
    "StatsManager",
    "CLIInterface",
    "WordleSolverApp",
]
