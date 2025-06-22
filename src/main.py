# src/main.py
"""
Main entry point for the Wordle Solver application.
"""
from .modules.app import WordleSolverApp

def main():
    """Main function that starts the application."""
    app = WordleSolverApp()
    app.run()

if __name__ == "__main__":
    main()
