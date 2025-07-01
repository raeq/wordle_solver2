# src/frontend/cli/formatters.py
"""
Text formatting, colorization, and styling for the CLI interface.
"""

from typing import List, Optional

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.modules.backend.result_color import ResultColor

from .constants import TABLE_CONFIGS, UI_STYLES


class TextFormatter:
    """Handles text formatting and colorization."""

    @staticmethod
    def colorize_guess_result(guess: str, result: str) -> Text:
        """Convert guess and result to colored rich Text."""
        styled_text = Text()

        for letter, code in zip(guess, result):
            if code == ResultColor.GREEN.value:
                styled_text.append(letter, style="black on green")
            elif code == ResultColor.YELLOW.value:
                styled_text.append(letter, style="black on yellow")
            else:  # BLACK
                styled_text.append(letter, style="white on grey23")

        return styled_text

    @staticmethod
    def create_panel(content: str, title: str, style: str = "bold blue") -> Panel:
        """Create a styled panel with content."""
        return Panel(
            content,
            title=title,
            title_align="center",
            style=style,
        )

    @staticmethod
    def format_game_mode_panel(content: str, title: str, mode: str) -> Panel:
        """Create a game mode specific panel."""
        style_mapping = {
            "solver": "bold blue",
            "play": "bold green",
            "review": "bold cyan",
        }
        style = style_mapping.get(mode, "bold blue")
        return TextFormatter.create_panel(content, title, style)

    @staticmethod
    def format_error_message(message: str) -> str:
        """Format an error message with styling."""
        return f"[{UI_STYLES['error']}]Error: {message}[/{UI_STYLES['error']}]"

    @staticmethod
    def format_success_message(message: str) -> str:
        """Format a success message with styling."""
        return f"[{UI_STYLES['success']}]{message}[/{UI_STYLES['success']}]"

    @staticmethod
    def format_info_message(message: str) -> str:
        """Format an info message with styling."""
        return f"[{UI_STYLES['info']}]{message}[/{UI_STYLES['info']}]"

    @staticmethod
    def format_prompt(text: str) -> str:
        """Format a prompt with consistent styling."""
        return f"[{UI_STYLES['info']}]{text}[/{UI_STYLES['info']}]"

    @staticmethod
    def format_guess_display(
        guess: str, result: str, attempt: int, max_attempts: int
    ) -> str:
        """Format a guess result for display."""
        colored_result = TextFormatter.colorize_guess_result(guess, result)
        emoji_result = ResultColor.result_to_emoji(result)
        return f"\n[bold]Guess {attempt}/{max_attempts}:[/bold] {colored_result} {emoji_result}"


class TableFormatter:
    """Handles table creation and formatting."""

    @staticmethod
    def create_strategies_table(
        strategies_data: dict, available_strategies: List[str]
    ) -> Table:
        """Create a formatted table of available strategies."""
        config = TABLE_CONFIGS["strategies"]
        table = Table(title="🧠 Available Solver Strategies")

        # Add columns
        for col_config in config["columns"]:
            table.add_column(
                col_config["name"],
                style=col_config.get("style"),
                width=col_config.get("width"),
            )

        # Add rows
        for strategy_key in available_strategies:
            info = strategies_data.get(
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

        return table

    @staticmethod
    def create_suggestions_table(
        suggestions: List[str],
        remaining_words_count: int,
        common_words: Optional[List[str]] = None,
        strategy_name: Optional[str] = None,
    ) -> Table:
        """Create a formatted table of word suggestions."""
        # Create title with strategy information
        title = f"Suggestions (from {remaining_words_count} possible words)"
        if strategy_name:
            title += f" • Strategy: {strategy_name.upper()}"

        config = TABLE_CONFIGS["suggestions"]
        table = Table(title=title)

        # Add columns
        for col_config in config["columns"]:
            table.add_column(col_config["name"], style=col_config.get("style"))

        # Add rows
        for word in suggestions:
            is_common = "✓" if common_words and word in common_words else ""
            table.add_row(word, is_common)

        return table

    @staticmethod
    def create_game_review_table(guesses: List[tuple], target_word: str) -> List[str]:
        """Create formatted lines for game review display."""
        lines = []
        lines.append(f"[dim]Target Word: [bold]{target_word}[/bold][/dim]")
        lines.append("[dim]" + "=" * 50 + "[/dim]")

        # Show each guess
        for i, guess_data in enumerate(guesses, 1):
            if len(guess_data) >= 3:
                guess, result, method = guess_data[0], guess_data[1], guess_data[2]
            else:
                guess, result = guess_data[0], guess_data[1]
                method = "unknown"

            colored_result = TextFormatter.colorize_guess_result(guess, result)
            emoji_result = ResultColor.result_to_emoji(result)

            lines.append(f"\n[bold]Turn {i}:[/bold]")
            lines.append(f"  Word: [bold white]{guess}[/bold white]")
            lines.append(f"  Result: {colored_result} {emoji_result}")
            lines.append(f"  Method: [cyan]{method}[/cyan]")

        return lines


class MessageFormatter:
    """Handles message templating and formatting."""

    @staticmethod
    def format_strategy_hint(strategy_name: str, remaining_words: int) -> str:
        """Format a strategy hint message."""
        from .constants import STRATEGY_HINTS

        hint_template = STRATEGY_HINTS.get(strategy_name)
        if not hint_template:
            return ""

        hint = hint_template.format(remaining_words=remaining_words)
        return f"\n[{UI_STYLES['dim']}]{hint}[/{UI_STYLES['dim']}]"

    @staticmethod
    def format_current_strategy_display(strategy_name: str, description: str) -> Panel:
        """Format current strategy display panel."""
        content = f"[bold]{strategy_name.upper()}[/bold]\n{description}"
        return Panel(
            content,
            title="Current Strategy",
            border_style="blue",
            width=60,
        )

    @staticmethod
    def format_game_over_message(won: bool, attempts: int) -> str:
        """Format game over message."""
        if won:
            return f"[{UI_STYLES['success']}]🎉 Won in {attempts} attempts![/{UI_STYLES['success']}]"
        else:
            return f"[{UI_STYLES['error']}]😢 Lost after {attempts} attempts[/{UI_STYLES['error']}]"

    @staticmethod
    def format_no_suggestions_message() -> str:
        """Format message when no suggestions are available."""
        return f"\n[{UI_STYLES['error']}]No valid words remain that match your constraints.[/{UI_STYLES['error']}]"

    @staticmethod
    def format_example_input() -> str:
        """Format example input with proper colors."""
        green = ResultColor.GREEN.value
        yellow = ResultColor.YELLOW.value
        black = ResultColor.BLACK.value
        return f"AUDIO {black}{yellow}{black}{green}{black}"
