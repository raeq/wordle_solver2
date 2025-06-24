#!/usr/bin/env python3
"""
Main entry point for the Wordle Solver application.
"""
import os
import sys

import click

from src.modules.app import WordleSolverApp
from src.modules.logging_utils import setup_logging

# Add the src directory to the path if running as script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@click.command()
@click.option("--log-level", default="INFO", help="Set the logging level (DEBUG, INFO, WARNING, ERROR)")
def main(log_level):
    """Run the Wordle Solver application."""
    # Setup logging with the specified level
    setup_logging(log_level=log_level)

    # Create and run the application
    app = WordleSolverApp()
    app.run()


if __name__ == "__main__":
    main()


def main():
    """Main function that starts the application."""
    app = WordleSolverApp()
    app.run()


if __name__ == "__main__":
    main()
