#!/usr/bin/env python3
"""
Entry point script for the Wordle Solver application.

The application now uses the enhanced implementation with stateless architecture,
providing better performance and additional features like analysis mode and benchmarking.
"""

import os
import sys

# Add src directory to Python path before importing from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Now we can import from src - this needs to be here after path modification
# ruff: noqa: E402
from src.main import main

if __name__ == "__main__":
    main()
