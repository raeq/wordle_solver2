# src/frontend/cli/__init__.py
"""
Modular CLI interface for the Wordle Solver application.

This module provides a clean, testable, and maintainable CLI interface
by separating concerns into specialized components.
"""

from .interface import CLIInterface

__all__ = ["CLIInterface"]
