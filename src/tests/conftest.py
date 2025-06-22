# src/modules/tests/conftest.py
"""
Pytest configuration file for the Wordle Solver tests.
"""
import sys
from pathlib import Path

# Add the project root to the Python path so that imports work correctly
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
