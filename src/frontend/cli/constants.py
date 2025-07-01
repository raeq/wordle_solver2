# src/frontend/cli/constants.py
"""
Constants and message templates for the CLI interface.
"""


# Game mode constants
GAME_MODES = {"SOLVER": "solver", "PLAY": "play", "REVIEW": "review", "CLEAR": "clear"}

# Special commands
SPECIAL_COMMANDS = {"HINT": "HINT", "STRATEGY": "STRATEGY", "QUIT": "QUIT"}

# UI Messages
WELCOME_MESSAGE = """
🎯 Welcome to Wordle Solver! 🎯

Choose your game mode:
1. 🧠 Solver Mode: You play Wordle and get suggestions
2. 🎮 Play Mode: Play against the computer
3. 📚 Review Mode: Review previous games
4. 🗑️  Clear History: Delete all game history

In Solver Mode, you tell the app your guess results and get top 10 suggestions.
In Play Mode, the computer picks a word and you try to guess it!
In Review Mode, you can review your past games and analyze your performance.
"""

SOLVER_MODE_START = """
🧠 Solver Mode Started! 🧠

Play Wordle in your favorite app, and I'll help you!
Enter your guess and the result pattern using:
  {green} = Green (correct position)
  {yellow} = Yellow (right letter, wrong position)
  {black} = Black (not in the word)

Example: "AUDIO {black}{yellow}{black}{green}{black}"
"""

PLAY_MODE_START = """
🎮 Play Mode Started! 🎮

Game ID: {game_id}

I've chosen a 5-letter word for you to guess.
You have 6 attempts to find it!
{difficulty_hint}

Enter your guess (5-letter word):
"""

REVIEW_MODE_START = """
📚 Review Mode Started! 📚

Browse through your previous games and analyze your performance.
You can navigate through pages of games or enter a specific Game ID
to review that game in detail.

Navigate with:
- 'n' for next page
- 'p' for previous page  
- Enter a 6-letter Game ID to review
- 'q' to return to main menu
"""

# Strategy descriptions
STRATEGY_DESCRIPTIONS = {
    "frequency": "Letter frequency analysis - prioritizes common letters",
    "entropy": "Information theory - maximizes information gain per guess",
    "minimax": "Worst-case optimization - minimizes maximum remaining words",
    "two_step": "Two-phase approach - broad elimination then targeted guessing",
    "weighted_gain": "Balanced approach - combines multiple scoring factors",
}

STRATEGY_INFO = {
    "frequency": {
        "name": "Frequency Analysis",
        "description": "Uses letter frequency to suggest common words",
        "best_for": "Early game, maximizing vowel discovery",
    },
    "entropy": {
        "name": "Entropy Maximization",
        "description": "Maximizes information gain using probability theory",
        "best_for": "Consistent performance across all game phases",
    },
    "minimax": {
        "name": "Minimax Optimization",
        "description": "Minimizes worst-case remaining word count",
        "best_for": "Late game when few words remain",
    },
    "two_step": {
        "name": "Two-Step Strategy",
        "description": "Broad elimination first, then targeted guessing",
        "best_for": "Balanced approach for varying difficulty",
    },
    "weighted_gain": {
        "name": "Weighted Gain (Default)",
        "description": "Combines multiple factors for balanced suggestions",
        "best_for": "General purpose, good overall performance",
    },
}

# Strategy hints
STRATEGY_HINTS = {
    "frequency": "💡 Frequency strategy works best early in the game to discover common letters",
    "entropy": "💡 Entropy strategy provides consistent performance throughout the game",
    "minimax": "💡 Minimax strategy is optimal when few words remain (currently {remaining_words})",
    "two_step": "💡 Two-step strategy adapts its approach based on game progress",
    "weighted_gain": "💡 Weighted gain provides balanced suggestions for general play",
}

# Default prompts
DEFAULT_PROMPTS = {
    "game_mode": "\n[bold cyan]Select game mode[/bold cyan]",
    "guess_input": "Enter your guess (5-letter word) or type 'hint' for suggestions:",
    "guess_and_result": "Enter your guess and result (e.g., 'AUDIO {example}') or type 'hint'/'strategy' for help",
    "strategy_selection": "\n[bold cyan]Select a strategy[/bold cyan]",
    "continue": "\n[dim]Press Enter to continue...[/dim]",
}

# Color scheme constants
UI_STYLES = {
    "title": "bold blue",
    "success": "bold green",
    "error": "bold red",
    "info": "bold cyan",
    "warning": "bold yellow",
    "dim": "dim",
    "highlight": "bold white",
}

# Table configurations
TABLE_CONFIGS = {
    "strategies": {
        "columns": [
            {"name": "Strategy", "style": "bold cyan", "width": 15},
            {"name": "Name", "style": "bold", "width": 20},
            {"name": "Description", "width": 35},
            {"name": "Best For", "style": "italic", "width": 25},
        ]
    },
    "suggestions": {
        "columns": [
            {"name": "Word", "style": "bold"},
            {"name": "Common?", "style": "green"},
        ]
    },
}
