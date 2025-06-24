# src/modules/app.py
"""
Main application module that coordinates the backend and frontend components.
"""

from ..frontend.cli_interface import CLIInterface
from .backend.exceptions import (
    GameStateError,
    InvalidColorError,
    InvalidGuessError,
    InvalidResultError,
    WordleError,
)
from .backend.game_engine import GameEngine
from .backend.result_color import ResultColor
from .backend.solver import Solver
from .backend.stats_manager import StatsManager
from .backend.word_manager import WordManager
from .logging_utils import log_game_outcome, log_method


class WordleSolverApp:
    """Main application that manages the game loop and component interaction."""

    def __init__(self) -> None:
        # Initialize components
        self.word_manager = WordManager()
        self.solver = Solver(self.word_manager)
        self.game_engine = GameEngine(self.word_manager)
        self.stats_manager = StatsManager()
        self.ui = CLIInterface()

    @log_method("DEBUG")
    def run(self) -> None:
        """Main application loop."""
        self.ui.display_welcome()

        while True:
            game_mode = self.ui.get_game_mode()

            if game_mode == "solver":
                self._run_solver_mode()
            else:
                self._run_game_mode()

            if not self.ui.ask_play_again():
                break

        self.ui.display_game_stats(self.stats_manager.get_stats())
        self.ui.console.print("\n[bold blue]Thanks for using Wordle Solver! Goodbye! 👋[/bold blue]")

    @log_method("DEBUG")
    def _run_solver_mode(self) -> None:
        """Run the solver mode (user plays externally and gets suggestions)."""
        try:
            self.ui.display_solver_mode_start()
            self.solver.reset()

            # Show initial suggestions
            self._show_suggestions()

            guesses_history = []
            attempt = 1
            max_attempts = 6
            won = False

            # Main solver loop
            while attempt <= max_attempts:
                try:
                    # Get guess and result from user
                    guess, result = self.ui.get_guess_and_result()

                    # Update solver state
                    self.solver.add_guess(guess, result)
                    guesses_history.append([guess, result])

                    # Display colored result
                    self.ui.display_guess_result(guess, result, attempt, max_attempts)

                    # Show top 10 suggestions after every guess
                    self._show_suggestions()

                    # Check if solved
                    if all(color == ResultColor.GREEN.value for color in result):
                        won = True
                        break

                    attempt += 1

                except InvalidGuessError as e:
                    self.ui.console.print(f"[bold red]Invalid Guess: {str(e)}[/bold red]")
                    continue
                except InvalidResultError as e:
                    self.ui.console.print(f"[bold red]Invalid Result: {str(e)}[/bold red]")
                    continue
                except InvalidColorError as e:
                    self.ui.console.print(f"[bold red]Invalid Color: {str(e)}[/bold red]")
                    continue
                except WordleError as e:
                    self.ui.console.print(f"[bold red]Error: {str(e)}[/bold red]")
                    continue

            # Record game statistics
            self.stats_manager.record_game(guesses_history, won, attempt)

            # Display game result
            self._display_solver_result(won, attempt, max_attempts)
            self.word_manager.reset()

        except Exception as e:
            self.ui.console.print(f"[bold red]Unexpected error: {str(e)}[/bold red]")
            self.ui.console.print(
                "[bold yellow]The application will continue, "
                "but the current game has been aborted.[/bold yellow]"
            )

    @log_method("DEBUG")
    def _show_suggestions(self) -> None:
        """Show word suggestions to the user."""
        suggestions = self.solver.get_top_suggestions(10)
        common_words = self.word_manager.get_common_possible_words()
        possible_words = self.word_manager.get_possible_words()
        self.ui.display_suggestions(suggestions, len(possible_words), common_words)

    @log_method("INFO")
    @log_game_outcome
    def _display_solver_result(self, won: bool, attempt: int, max_attempts: int) -> None:
        """Display the result of the solver mode game."""
        if won:
            self.ui.console.print(
                f"\n[bold green]Congratulations! "
                f"You solved it in {attempt}/{max_attempts} attempts![/bold green]"
            )
        else:
            self.ui.console.print("\n[bold red]Game over! You didn't find the solution.[/bold red]")

    @log_method("DEBUG")
    def _run_game_mode(self) -> None:
        """Run the game mode (computer selects a word for the user to guess)."""
        try:
            # Start a new game
            target_word = self.game_engine.start_new_game()
            self.solver.reset()  # Reset the solver to clear previous game state

            # Get the game ID from the game engine
            game_state = self.game_engine.get_game_state()
            game_id = str(game_state["game_id"])

            # Display the start message with the game ID
            self.ui.display_play_mode_start(game_id, f"The word has {len(set(target_word))} unique letters")

            guesses_history = []
            attempt = 1
            max_attempts = 6
            won = False

            # Main game loop
            while attempt <= max_attempts:
                # Get guess from user (already handles input validation)
                guess = self.ui.get_guess_input(
                    "Enter your guess (5-letter word) or type 'hint' for suggestions:",
                    self.word_manager,
                )

                # Handle hint command
                if guess == "HINT":
                    # Get current possible words based on previous guesses
                    suggestions = self.solver.get_top_suggestions(10)
                    common_possible = self.word_manager.get_common_possible_words()
                    possible_words = self.word_manager.get_possible_words()

                    # Show possible words as suggestions
                    self.ui.display_suggestions(
                        suggestions,
                        len(possible_words),
                        common_possible,
                    )
                    continue

                try:
                    # Process guess
                    result, is_solved = self.game_engine.make_guess(guess)
                    guesses_history.append([guess, result])

                    # Add the guess to the solver to filter possible words
                    self.solver.add_guess(guess, result)

                    # Display result
                    self.ui.display_guess_result(guess, result, attempt, max_attempts)

                    if is_solved:
                        won = True
                        break

                    attempt += 1

                except GameStateError as e:
                    self.ui.console.print(f"[bold red]Game Error: {str(e)}[/bold red]")
                except InvalidGuessError as e:
                    self.ui.console.print(f"[bold red]Invalid Guess: {str(e)}[/bold red]")
                except WordleError as e:
                    self.ui.console.print(f"[bold red]Error: {str(e)}[/bold red]")

            # Record game statistics
            game_state = self.game_engine.get_game_state()
            self.stats_manager.record_game(
                guesses_history,
                won,
                attempt,
                game_id=str(game_state["game_id"]),
                target_word=self.game_engine.target_word,
            )

            # Display game result
            self._display_game_result(
                won, self.game_engine.target_word, attempt if won else max_attempts, max_attempts
            )

            self.word_manager.reset()

        except Exception as e:
            self.ui.console.print(f"[bold red]Unexpected error: {str(e)}[/bold red]")
            self.ui.console.print(
                "[bold yellow]The application will continue, "
                "but the current game has been aborted.[/bold yellow]"
            )

    @log_method("INFO")
    @log_game_outcome
    def _display_game_result(self, won: bool, target_word: str, attempt: int, max_attempts: int) -> None:
        """Display the result of the play mode game."""
        game_state = self.game_engine.get_game_state()
        self.ui.display_game_over(
            won, target_word, attempt, max_attempts, str(game_state["game_id"]), self.game_engine.guesses
        )
