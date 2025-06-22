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
        else:
            return "play"

    def display_play_mode_start(self, difficulty_hint: str = "") -> None:
        """Display start message for play mode."""
        start_text = f"""
🎮 Play Mode Started! 🎮

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

    def get_guess_input(
        self,
        prompt_text: str = "Enter your guess (5-letter word) or type 'hint' for suggestions:",
        word_manager: Optional[WordManager] = None,
    ) -> str:
        """Get a guess from the user."""
        while True:
            try:
                guess = Prompt.ask(f"[bold cyan]{prompt_text}[/bold cyan]").upper()

                # Check for hint command
                if guess.strip() == "HINT":
                    return "HINT"

                self._validate_input_guess(guess, word_manager)
                return guess

            except (InputLengthError, InvalidGuessError) as e:
                self.console.print(f"[bold red]Error: {str(e)}[/bold red]")

    def _validate_input_guess(self, guess: str, word_manager: Optional[WordManager] = None) -> None:
        """Validate a user's guess input."""
        if len(guess) != 5:
            raise InputLengthError("Guess", len(guess))

        if not guess.isalpha():
            raise InvalidGuessError(guess, "must contain only letters")

        if word_manager and not word_manager.is_valid_word(guess):
            raise InvalidWordError(guess)

    def get_guess_and_result(self) -> Tuple[str, str]:
        """Get guess and result from user input, or recognize 'hint' command."""
        while True:
            try:
                user_input = self._get_user_input_for_guess_result()

                # Check for hint command
                if user_input.strip().upper() == "HINT":
                    return "HINT", ""

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
            f"or type 'hint' for a hint[/bold cyan]"
        )
        return Prompt.ask(prompt_text).upper()

    def _parse_and_validate_guess_result(self, user_input: str) -> Tuple[str, str]:
        """Parse and validate the guess and result from user input."""
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

    def display_guess_result(self, guess: str, result: str, attempt: int, max_attempts: int) -> None:
        """Display colored result of a guess."""
        colored_result = self._colorize_result(guess, result)
        emoji_result = ResultColor.result_to_emoji(result)

        self.console.print(f"\n[bold]Guess {attempt}/{max_attempts}:[/bold] {colored_result} {emoji_result}")

    def _colorize_result(self, guess: str, result: str) -> Text:
        """Convert result to colored text."""
        styled_text = Text()

        for _, (letter, code) in enumerate(zip(guess, result)):
            if code == ResultColor.GREEN.value:
                styled_text.append(letter, style="black on green")
            elif code == ResultColor.YELLOW.value:
                styled_text.append(letter, style="black on yellow")
            else:  # BLACK
                styled_text.append(letter, style="white on grey23")

        return styled_text

    def display_suggestions(
        self,
        suggestions: List[str],
        remaining_words_count: int,
        common_words: Optional[List[str]] = None,
    ) -> None:
        """Display suggestions to the user."""
        if not suggestions:
            self.console.print("\n[bold red]No valid words remain that match your constraints.[/bold red]")
            return

        # Create results table
        table = Table(title=f"Suggestions (from {remaining_words_count} possible words)")

        table.add_column("Word", style="bold")
        table.add_column("Common?", style="green")

        for word in suggestions:
            is_common = "✓" if common_words and word in common_words else ""
            table.add_row(word, is_common)

        self.console.print(table)

    def display_game_over(self, won: bool, target_word: str, attempts: int, max_attempts: int) -> None:
        """Display game over message."""
        if won:
            message = f"""
🎉 Congratulations! 🎉

You correctly guessed the word: [bold green]{target_word}[/bold green]
in {attempts}/{max_attempts} attempts!
            """
            title = "You Win!"
            style = "bold green"
        else:
            message = f"""
😢 Game Over 😢

The word was: [bold red]{target_word}[/bold red]
Better luck next time!
            """
            title = "You Lost"
            style = "bold red"

        self.console.print(Panel(message, title=title, style=style))

    def display_game_stats(self, stats: Dict) -> None:
        """Display game statistics."""
        panel_content = f"""
📊 Game Statistics ��

🎮 Games Played: {stats['games_played']}
🏆 Games Won: {stats['games_won']}
📈 Win Rate: {stats['win_rate']:.1f}%
��� Average Attempts: {stats['avg_attempts']:.1f}
        """

        self.console.print(Panel(panel_content, title="Statistics", border_style="blue"))

    def display_hint(self, hint: str) -> None:
        """Display a hint to the user."""
        self.console.print(Panel(hint, title="💡 Hint", border_style="yellow"))

    def ask_play_again(self) -> bool:
        """Ask if the user wants to play again."""
        return Confirm.ask("\n[bold cyan]Would you like to play again?[/bold cyan]")

    def ask_for_hint(self) -> bool:
        """Ask if the user wants a hint."""
        return Confirm.ask("[bold yellow]Would you like a hint? (costs you one guess)[/bold yellow]")
