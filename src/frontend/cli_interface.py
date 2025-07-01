# src/frontend/cli_interface.py
"""
Command line interface for the Wordle Solver application.
"""
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from src.modules.backend.exceptions import (
    InputLengthError,
    InvalidGuessError,
    InvalidResultError,
    InvalidWordError,
)
from src.modules.backend.result_color import ResultColor
from src.modules.backend.solver.strategy_factory import StrategyFactory
from src.modules.backend.word_manager import WordManager


class CLIInterface:
    """Rich-based command line interface for the Wordle Solver."""

    def __init__(self) -> None:
        self.console = Console()

    def display_welcome(self) -> None:
        """Display a welcome message."""
        welcome_text = """
🎯 Welcome to Wordle Solver! 🎯

Choose your game mode:
1. 🧠 Solver Mode: You play Wordle and get suggestions
2. 🎮 Play Mode: Play against the computer

In Solver Mode, you tell the app your guess results and get top 10 suggestions.
In Play Mode, the computer picks a word and you try to guess it!
        """

        self.console.print(
            Panel(
                welcome_text,
                title="Wordle Solver",
                title_align="center",
                style="bold blue",
            )
        )

    def get_game_mode(self) -> str:
        """Get the game mode from user."""
        choice = Prompt.ask(
            "\n[bold cyan]Select game mode[/bold cyan]",
            choices=["1", "2", "solver", "play"],
            default="1",
        )

        if choice in ["1", "solver"]:
            return "solver"
        return "play"

    def display_play_mode_start(self, game_id: str, difficulty_hint: str = "") -> None:
        """Display start message for play mode."""
        start_text = f"""
🎮 Play Mode Started! 🎮

Game ID: {game_id}

I've chosen a 5-letter word for you to guess.
You have 6 attempts to find it!
{difficulty_hint}

Enter your guess (5-letter word):
        """

        self.console.print(
            Panel(
                start_text,
                title="Play Wordle",
                title_align="center",
                style="bold green",
            )
        )

    def display_solver_mode_start(self) -> None:
        """Display start message for solver mode."""
        green = ResultColor.GREEN.value
        yellow = ResultColor.YELLOW.value
        black = ResultColor.BLACK.value

        start_text = f"""
🧠 Solver Mode Started! 🧠

Play Wordle in your favorite app, and I'll help you!
Enter your guess and the result pattern using:
  {green} = Green (correct position)
  {yellow} = Yellow (right letter, wrong position)
  {black} = Black (not in the word)

Example: "AUDIO {black}{yellow}{black}{green}{black}"
        """

        self.console.print(
            Panel(
                start_text,
                title="Wordle Solver",
                title_align="center",
                style="bold blue",
            )
        )

    def display_current_strategy(self, strategy_name: str) -> None:
        """Display the currently active strategy."""
        strategy_descriptions = {
            "frequency": "Letter frequency analysis - prioritizes common letters",
            "entropy": "Information theory - maximizes information gain per guess",
            "minimax": "Worst-case optimization - minimizes maximum remaining words",
            "two_step": "Two-phase approach - broad elimination then targeted guessing",
            "weighted_gain": "Balanced approach - combines multiple scoring factors",
        }

        description = strategy_descriptions.get(strategy_name, "Unknown strategy")

        self.console.print(
            Panel(
                f"[bold]{strategy_name.upper()}[/bold]\n{description}",
                title="Current Strategy",
                border_style="blue",
                width=60,
            )
        )

    def display_available_strategies(self) -> None:
        """Display all available strategies with descriptions."""
        strategies_info = {
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

        table = Table(title="🧠 Available Solver Strategies")
        table.add_column("Strategy", style="bold cyan", width=15)
        table.add_column("Name", style="bold", width=20)
        table.add_column("Description", width=35)
        table.add_column("Best For", style="italic", width=25)

        available_strategies = StrategyFactory.get_available_strategies()

        for strategy_key in available_strategies:
            info = strategies_info.get(
                strategy_key,
                {
                    "name": strategy_key.title(),
                    "description": "Custom strategy",
                    "best_for": "Specialized use cases",
                },
            )

            table.add_row(
                strategy_key, info["name"], info["description"], info["best_for"]
            )

        self.console.print(table)

    def get_strategy_selection(
        self, current_strategy: Optional[str] = None
    ) -> Optional[str]:
        """Prompt user to select a strategy."""
        available_strategies = StrategyFactory.get_available_strategies()

        if current_strategy:
            self.console.print(
                f"\n[bold]Current strategy:[/bold] [cyan]{current_strategy}[/cyan]"
            )

        self.display_available_strategies()

        prompt_text = f"\n[bold cyan]Select a strategy[/bold cyan] ({''.join(available_strategies)})"

        if current_strategy:
            prompt_text += f" or press Enter to keep [cyan]{current_strategy}[/cyan]"

        while True:
            choice = (
                Prompt.ask(
                    prompt_text, default=current_strategy if current_strategy else ""
                )
                .lower()
                .strip()
            )

            if not choice and current_strategy:
                return None  # Keep current strategy

            if choice in available_strategies:
                return choice

            self.console.print(f"[bold red]Invalid choice: {choice}[/bold red]")
            self.console.print(
                f"Available strategies: {', '.join(available_strategies)}"
            )

    def get_guess_input(
        self,
        prompt_text: str = "Enter your guess (5-letter word) or type 'hint' for suggestions:",
        word_manager: Optional[WordManager] = None,
    ) -> str:
        """Get a guess from the user."""
        while True:
            try:
                guess = Prompt.ask(f"[bold cyan]{prompt_text}[/bold cyan]").upper()

                # Check for special commands
                if guess.strip() == "HINT":
                    return "HINT"
                if guess.strip() == "STRATEGY":
                    return "STRATEGY"

                self._validate_input_guess(guess, word_manager)
                return guess

            except (InputLengthError, InvalidGuessError) as e:
                self.console.print(f"[bold red]Error: {str(e)}[/bold red]")

    def _validate_input_guess(
        self, guess: str, word_manager: Optional[WordManager] = None
    ) -> None:
        """Validate a user's guess input."""
        if len(guess) != 5:
            raise InputLengthError("Guess", len(guess))

        if not guess.isalpha():
            raise InvalidGuessError(guess, "must contain only letters")

        if word_manager and not word_manager.is_valid_word(guess):
            raise InvalidWordError(guess)

    def get_guess_and_result(self) -> Tuple[str, str]:
        """Get guess and result from user input, or recognize special commands."""
        while True:
            try:
                user_input = self._get_user_input_for_guess_result()

                # Check for special commands
                if user_input.strip().upper() == "HINT":
                    return "HINT", ""
                if user_input.strip().upper() == "STRATEGY":
                    return "STRATEGY", ""

                # Split and validate the input
                guess, result = self._parse_and_validate_guess_result(user_input)
                return guess, result

            except (InputLengthError, InvalidGuessError, InvalidResultError) as e:
                self.console.print(f"[bold red]Error: {str(e)}[/bold red]")

    def _get_user_input_for_guess_result(self) -> str:
        """Get user input for guess and result."""
        green = ResultColor.GREEN.value
        yellow = ResultColor.YELLOW.value
        black = ResultColor.BLACK.value

        example = f"AUDIO {black}{yellow}{black}{green}{black}"
        prompt_text = (
            f"[bold cyan]Enter your guess and result (e.g., '{example}') "
            f"or type 'hint'/'strategy' for help[/bold cyan]"
        )
        user_input = Prompt.ask(prompt_text).upper()

        # Special case for the winning result pattern
        if user_input.strip() == "GGGGG":
            return f"SOLVE {green}{green}{green}{green}{green}"

        return user_input

    def _parse_and_validate_guess_result(self, user_input: str) -> Tuple[str, str]:
        """Parse and validate the guess and result from user input."""
        # Special case for winning result
        if user_input.startswith("SOLVE "):
            return "SOLVE", user_input.split()[1]

        # Split input into guess and result parts
        parts = user_input.split()
        if len(parts) != 2:
            raise InvalidGuessError(user_input, "must follow 'GUESS RESULT' format")

        guess, result = parts

        # Validate guess
        self._validate_guess(guess)

        # Validate result
        self._validate_result(result)

        return guess, result

    def _validate_guess(self, guess: str) -> None:
        """Validate the guess string."""
        if len(guess) != 5:
            raise InputLengthError("Guess", len(guess))

        if not guess.isalpha():
            raise InvalidGuessError(guess, "must contain only letters")

    def _validate_result(self, result: str) -> None:
        """Validate the result string."""
        if len(result) != 5:
            raise InputLengthError("Result", len(result))

        if not ResultColor.is_valid_result_string(result):
            raise InvalidResultError(
                result,
                f"must contain only {ResultColor.GREEN.value}, "
                f"{ResultColor.YELLOW.value}, or {ResultColor.BLACK.value} characters",
            )

    def display_guess_result(
        self, guess: str, result: str, attempt: int, max_attempts: int
    ) -> None:
        """Display colored result of a guess."""
        colored_result = self._colorize_result(guess, result)
        emoji_result = ResultColor.result_to_emoji(result)

        self.console.print(
            f"\n[bold]Guess {attempt}/{max_attempts}:[/bold] {colored_result} {emoji_result}"
        )

    def _colorize_result(self, guess: str, result: str) -> Text:
        """Convert result to colored text."""
        styled_text = Text()

        for _, (letter, code) in enumerate(zip(guess, result)):
            if code == ResultColor.GREEN.value:
                styled_text.append("", style="black on green")
            elif code == ResultColor.YELLOW.value:
                styled_text.append("", style="black on yellow")
            else:  # BLACK
                styled_text.append("", style="white on grey23")

        return styled_text

    def display_suggestions(
        self,
        suggestions: List[str],
        remaining_words_count: int,
        common_words: Optional[List[str]] = None,
        strategy_name: Optional[str] = None,
    ) -> None:
        """Display suggestions to the user."""
        if not suggestions:
            self.console.print(
                "\n[bold red]No valid words remain that match your constraints.[/bold red]"
            )
            return

        # Create title with strategy information
        title = f"Suggestions (from {remaining_words_count} possible words)"
        if strategy_name:
            title += f" • Strategy: {strategy_name.upper()}"

        # Create results table
        table = Table(title=title)

        table.add_column("Word", style="bold")
        table.add_column("Common?", style="green")

        for word in suggestions:
            is_common = "✓" if common_words and word in common_words else ""
            table.add_row(word, is_common)

        self.console.print(table)

        # Add strategy hint if provided
        if strategy_name:
            self._display_strategy_hint(strategy_name, remaining_words_count)

    def _display_strategy_hint(self, strategy_name: str, remaining_words: int) -> None:
        """Display a helpful hint about the current strategy."""
        hints = {
            "frequency": "💡 Frequency strategy works best early in the game to discover common letters",
            "entropy": "💡 Entropy strategy provides consistent performance throughout the game",
            "minimax": f"💡 Minimax strategy is optimal when few words remain (currently {remaining_words})",
            "two_step": "💡 Two-step strategy adapts its approach based on game progress",
            "weighted_gain": "💡 Weighted gain provides balanced suggestions for general play",
        }

        hint = hints.get(strategy_name)
        if hint:
            self.console.print(f"\n[dim]{hint}[/dim]")

    def display_game_over(
        self,
        won: bool,
        target_word: str,
        attempts: int,
        max_attempts: int,
        game_id: str,
        guesses_history=None,
    ) -> None:
        """Display game over message."""
        if won:
            message = f"""
🎉 Congratulations! 🎉

Game ID: {game_id}

You correctly guessed the word: [bold green]{target_word}[/bold green]
in {attempts}/{max_attempts} attempts!
            """
            title = "You Win!"
            style = "bold green"
        else:
            message = f"""
😢 Game Over 😢

Game ID: {game_id}

The word was: [bold red]{target_word}[/bold red]
Better luck next time!
            """
            title = "You Lost"
            style = "bold red"

        self.console.print(Panel(message, title=title, style=style))

        # Display guess history if available
        if guesses_history:
            self._display_guess_history(guesses_history)

    def _display_guess_history(self, guesses_history) -> None:
        """Display the history of guesses made during the game."""
        self.console.print("\n[bold]Your Guesses:[/bold]")

        for attempt, guess_data in enumerate(guesses_history, start=1):
            # Handle both old format (guess, result) and new format (guess, result, strategy)
            if len(guess_data) == 3:
                guess, result, strategy = guess_data
                strategy_display = f" ([cyan]{strategy}[/cyan])"
            else:
                # Fallback for old format without strategy tracking
                guess, result = guess_data
                strategy_display = ""

            colored_result = self._colorize_result(guess, result)
            emoji_result = ResultColor.result_to_emoji(result)
            self.console.print(
                f"Guess {attempt}: {colored_result} {emoji_result}{strategy_display}"
            )

    def display_guess_history(self, guesses_history) -> None:
        """Display the history of guesses made during the game (public method)."""
        return self._display_guess_history(guesses_history)

    def display_game_stats(self, stats: Dict) -> None:
        """Display game statistics."""
        panel_content = f"""
📊 Game Statistics ��

🎮 Games Played: {stats['games_played']}
🏆 Games Won: {stats['games_won']}
📈 Win Rate: {stats['win_rate']:.1f}%
��� Average Attempts: {stats['avg_attempts']:.1f}
        """

        self.console.print(
            Panel(panel_content, title="Statistics", border_style="blue")
        )

    def display_hint(self, hint: str) -> None:
        """Display a hint to the user."""
        self.console.print(Panel(hint, title="💡 Hint", border_style="yellow"))

    def ask_play_again(self) -> bool:
        """Ask if the user wants to play again."""
        return Confirm.ask("\n[bold cyan]Would you like to play again?[/bold cyan]")

    def ask_for_hint(self) -> bool:
        """Ask if the user wants a hint."""
        return Confirm.ask(
            "[bold yellow]Would you like a hint? (costs you one guess)[/bold yellow]"
        )
