# src/frontend/cli/__init__.py
"""
Modular CLI interface for the Wordle Solver application.

This module provides a clean, testable, and maintainable CLI interface
by separating concerns into specialized components.
"""

from .game_state_manager import GameStateManager
from .interface import CLIInterface

__all__ = ["CLIInterface", "GameStateManager"]
