#!/usr/bin/env python3
"""
Main entry point for the Wordle Solver application.
"""
import os
import sys

import click

from src.config.settings import initialize_config
from src.modules.enhanced_app import EnhancedWordleSolverApp
from src.modules.logging_utils import setup_logging

# Add the src directory to the path if running as script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@click.command()
@click.option(
    "--log-level",
    default=None,
    help="Set the logging level (DEBUG, INFO, WARNING, ERROR)",
)
@click.option("--config", default=None, help="Path to configuration file")
@click.option(
    "--stateless/--no-stateless",
    default=True,
    help="Use stateless implementation (default: enabled)",
)
def main(log_level=None, config=None, stateless=True):
    """Run the Wordle Solver application with enhanced features."""
    # Initialize configuration
    app_config = initialize_config(config)

    # Use log level from command line or config
    effective_log_level = log_level or app_config.logging.level

    # Setup logging with the specified level
    setup_logging(log_level=effective_log_level)

    # Create and run the enhanced application with stateless parameter
    app = EnhancedWordleSolverApp(use_stateless=stateless)
    app.run()


if __name__ == "__main__":
    main()
