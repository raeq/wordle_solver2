# src/modules/app.py
"""
Main application module that coordinates the backend and frontend components.
"""

from src.common.di_container import get_container
from src.config.settings import get_settings
from src.frontend.cli import CLIInterface

from .backend.exceptions import (
    GameStateError,
    InvalidColorError,
    InvalidGuessError,
    InvalidResultError,
    WordleError,
)
from .backend.game_engine import GameEngine
from .backend.game_history_manager import GameHistoryManager
from .backend.game_state_manager import GameStateManager
from .backend.result_color import ResultColor
from .backend.solver.strategy_factory import StrategyFactory
from .backend.stats_manager import StatsManager
from .backend.word_manager import WordManager
from .logging_utils import log_game_outcome, log_method


class WordleSolverApp:
    """Main application that manages the game loop and component interaction."""

    def __init__(self) -> None:
        # Get configuration and DI container
        self.config = get_settings()
        self.container = get_container()

        # Group related components to reduce instance attribute count
        self._components = self._initialize_components()
        self.current_strategy_name = self.config.solver.default_strategy

    def _initialize_components(self) -> dict:
        """Initialize and return all application components."""
        return {
            "word_manager": self.container.get(WordManager),
            "solver": self.container.get(GameStateManager),
            "game_engine": self.container.get(GameEngine),
            "stats_manager": self.container.get(StatsManager),
            "ui": self.container.get(CLIInterface),
        }

    @property
    def word_manager(self) -> WordManager:
        """Get word manager component."""
        return self._components["word_manager"]  # type: ignore

    @property
    def solver(self) -> GameStateManager:
        """Get solver component."""
        return self._components["solver"]  # type: ignore

    @property
    def game_engine(self) -> GameEngine:
        """Get game engine component."""
        return self._components["game_engine"]  # type: ignore

    @property
    def stats_manager(self) -> StatsManager:
        """Get stats manager component."""
        return self._components["stats_manager"]  # type: ignore

    @property
    def ui(self) -> CLIInterface:
        """Get UI component."""
        return self._components["ui"]  # type: ignore

    def get_current_strategy(self) -> str:
        """Get the current strategy name (public method to satisfy pylint)."""
        return self.current_strategy_name

    @log_method("DEBUG")
    def run(self) -> None:
        """Main application loop."""
        self.ui.display_welcome()

        # Allow user to select initial strategy
        self._select_initial_strategy()

        while True:
            game_mode = self.ui.get_game_mode()

            if game_mode == "solver":
                self._run_solver_mode()
            elif game_mode == "review":
                self._run_review_mode()
            elif game_mode == "clear":
                self._run_clear_history_mode()
            else:
                self._run_game_mode()

            if not self.ui.ask_play_again():
                break

        self.ui.display_game_stats(self.stats_manager.get_stats())
        self.ui.console.print(
            "\n[bold blue]Thanks for using Wordle Solver! Goodbye! 👋[/bold blue]"
        )

    def _select_initial_strategy(self) -> None:
        """Allow user to select the initial strategy."""
        self.ui.console.print("\n[bold]🧠 Let's set up your solver strategy![/bold]")

        new_strategy_name = self.ui.get_strategy_selection(self.current_strategy_name)
        if new_strategy_name:
            self._change_strategy(new_strategy_name)

        self.ui.display_current_strategy(self.current_strategy_name)

    def _change_strategy(self, strategy_name: str) -> None:
        """Change the current solver strategy."""
        try:
            new_strategy = StrategyFactory.create_strategy(strategy_name)
            self.solver.set_strategy(new_strategy)
            self.current_strategy_name = strategy_name
            self.ui.console.print(
                f"[bold green]✓ Strategy changed to: {strategy_name.upper()}[/bold green]"
            )
        except ValueError as e:
            self.ui.console.print(
                f"[bold red]Error changing strategy: {str(e)}[/bold red]"
            )

    def _handle_strategy_command(self) -> None:
        """Handle the strategy change command."""
        new_strategy_name = self.ui.get_strategy_selection(self.current_strategy_name)
        if new_strategy_name:
            self._change_strategy(new_strategy_name)
        else:
            self.ui.console.print("[dim]Strategy unchanged.[/dim]")

    @log_method("DEBUG")
    def _run_solver_mode(self) -> None:
        """Run the solver mode (user plays externally and gets suggestions)."""
        try:
            self.ui.display_solver_mode_start()
            self.solver.reset()
            self._show_suggestions()

            guesses_history: list = []
            attempt = 1
            max_attempts = 6
            won = False

            # Main solver loop
            while attempt <= max_attempts and not won:
                won = self._process_solver_turn(guesses_history, attempt, max_attempts)
                if not won:
                    attempt += 1

            # Record game statistics and display results
            self._finalize_solver_mode(guesses_history, won, attempt, max_attempts)

        except Exception as e:
            self._handle_solver_mode_error(e)

    def _process_solver_turn(
        self, guesses_history: list, attempt: int, max_attempts: int
    ) -> bool:
        """Process a single turn in solver mode. Returns True if game is won."""
        try:
            # Get guess and result from user
            guess, result = self.ui.get_guess_and_result()

            # Handle special commands
            if guess == "HINT":
                self._show_suggestions()
                return False
            if guess == "STRATEGY":
                self._handle_strategy_command()
                return False

            # Update solver state
            self.solver.add_guess(guess, result)
            guesses_history.append([guess, result, self.current_strategy_name])

            # Display colored result
            self.ui.display_guess_result(guess, result, attempt, max_attempts)

            # Check if solved
            if result == ResultColor.GREEN.value * 5:
                self.ui.console.print(
                    "\n[bold green]Congratulations! You've found the solution![/bold green]"
                )
                return True

            # Show suggestions for next turn
            self._show_suggestions()
            return False

        except (
            InvalidGuessError,
            InvalidResultError,
            InvalidColorError,
            WordleError,
        ) as e:
            self.ui.console.print(f"[bold red]{type(e).__name__}: {str(e)}[/bold red]")
            return False

    def _finalize_solver_mode(
        self, guesses_history: list, won: bool, attempt: int, max_attempts: int
    ) -> None:
        """Finalize solver mode by recording stats and displaying results."""
        self.stats_manager.record_game(guesses_history, won, attempt, mode="solver")
        self._display_solver_result(won, attempt, max_attempts, guesses_history)
        self.word_manager.reset()

    def _handle_solver_mode_error(self, error: Exception) -> None:
        """Handle unexpected errors in solver mode."""
        self.ui.console.print(f"[bold red]Unexpected error: {str(error)}[/bold red]")
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
        self.ui.display_suggestions(
            suggestions,
            len(possible_words),
            common_words,
            strategy_name=self.current_strategy_name,
        )

    @log_method("INFO")
    @log_game_outcome
    def _display_solver_result(
        self, won: bool, attempt: int, max_attempts: int, guesses_history=None
    ) -> None:
        """Display the result of the solver mode game."""
        if won:
            self.ui.console.print(
                f"\n[bold green]Congratulations! "
                f"You solved it in {attempt}/{max_attempts} attempts![/bold green]"
            )
        else:
            self.ui.console.print(
                "\n[bold red]Game over! You didn't find the solution.[/bold red]"
            )

        # Display guess history if available
        if guesses_history:
            # Use public method instead of protected access
            self.ui.display_guess_history(guesses_history)

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
            self.ui.display_play_mode_start(
                game_id, f"The word has {len(set(target_word))} unique letters"
            )

            guesses_history = []
            attempt = 1
            max_attempts = 6
            won = False

            # Main game loop
            while attempt <= max_attempts:
                # Get guess from user (already handles input validation)
                guess = self.ui.get_guess_input(
                    "Enter your guess (5-letter word) or type 'hint'/'strategy' for help:",
                    self.word_manager,
                )

                # Handle special commands
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
                        strategy_name=self.current_strategy_name,
                    )
                    continue
                if guess == "STRATEGY":
                    self._handle_strategy_command()
                    continue

                try:
                    # Process guess
                    result, is_solved = self.game_engine.make_guess(guess)
                    # Track strategy used for this guess
                    guesses_history.append([guess, result, self.current_strategy_name])

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
                    self.ui.console.print(
                        f"[bold red]Invalid Guess: {str(e)}[/bold red]"
                    )
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
                mode="manual",
            )

            # Display game result
            self._display_game_result(
                won,
                self.game_engine.target_word,
                attempt if won else max_attempts,
                max_attempts,
            )

            self.word_manager.reset()

        except (
            GameStateError,
            InvalidGuessError,
            InvalidResultError,
            WordleError,
        ) as e:
            # Handle known game-related errors
            self.ui.console.print(f"[bold red]Game Error: {str(e)}[/bold red]")
            self.ui.console.print(
                "[bold yellow]The application will continue, "
                "but the current game has been aborted.[/bold yellow]"
            )
        except KeyboardInterrupt:
            # Handle user interruption gracefully
            self.ui.console.print(
                "\n[bold yellow]Game interrupted by user.[/bold yellow]"
            )
        except Exception as e:
            # Handle any other unexpected errors to prevent app crash
            self.ui.console.print(f"[bold red]Unexpected error: {str(e)}[/bold red]")
            self.ui.console.print(
                "[bold yellow]The application will continue, "
                "but the current game has been aborted.[/bold yellow]"
            )

    @log_method("INFO")
    @log_game_outcome
    def _display_game_result(
        self, won: bool, target_word: str, attempt: int, max_attempts: int
    ) -> None:
        """Display the result of the play mode game."""
        game_state = self.game_engine.get_game_state()
        self.ui.display_game_over(
            won,
            target_word,
            attempt,
            max_attempts,
            str(game_state["game_id"]),
            self.game_engine.guesses,
        )

    @log_method("DEBUG")
    def _run_review_mode(self) -> None:
        """Run the review mode for browsing and reviewing previous games."""
        try:
            self.ui.display_review_mode_start()

            # Use StatsManager instead of GameHistoryManager for consistency
            try:
                games = self.stats_manager.get_history()
                if not games:
                    self.ui.console.print("[yellow]No games found in history.[/yellow]")
                    return

                # Paginate games directly (simple pagination)
                page_size = 10
                pages = []
                for i in range(0, len(games), page_size):
                    pages.append(games[i : i + page_size])

                if not pages:
                    self.ui.console.print("[yellow]No games to display.[/yellow]")
                    return

                current_page = 1
                total_pages = len(pages)

                # Main review loop
                while True:
                    # Display current page using the review mode handler
                    self.ui.display_games_list(
                        pages[current_page - 1], current_page, total_pages
                    )

                    # Get user action
                    action = self.ui.get_game_review_action(current_page, total_pages)

                    if action == "q":
                        break
                    elif action == "clear":
                        # Handle clear history command
                        if self._handle_clear_history():
                            # History was cleared, exit review mode
                            break
                    elif action == "n" and current_page < total_pages:
                        current_page += 1
                    elif action == "p" and current_page > 1:
                        current_page -= 1
                    elif len(action) == 6 and action.isalnum():
                        # User entered a game ID - use StatsManager to find it
                        game = self.stats_manager.get_game_by_id(action)
                        if game:
                            self.ui.simulate_game_display(game)
                        else:
                            self.ui.console.print(
                                f"[red]Game ID '{action}' not found.[/red]"
                            )

            except Exception as e:
                self.ui.console.print(
                    f"[bold red]Error loading game history: {str(e)}[/bold red]"
                )

        except Exception as e:
            self.ui.console.print(
                f"[bold red]Error in review mode: {str(e)}[/bold red]"
            )

    def _handle_clear_history(self) -> bool:
        """
        Handle the clear history command with confirmation.

        Returns:
            bool: True if history was cleared, False if cancelled
        """
        # Check if there's any history to clear
        if not self.stats_manager.has_history():
            self.ui.console.print("[yellow]No history to clear.[/yellow]")
            return False

        # Get current count before clearing
        games_count = self.stats_manager.get_history_count()

        # Get confirmation from user through the UI
        if self.ui.review_mode.confirm_clear_history():
            # User confirmed, clear the history
            success = self.stats_manager.clear_all_history()

            # Display result
            self.ui.review_mode.display_clear_history_result(success, games_count)

            return success
        else:
            # User cancelled
            self.ui.console.print("[dim]Clear history cancelled.[/dim]")
            return False

    @log_method("DEBUG")
    def _run_clear_history_mode(self) -> None:
        """Run the clear history mode (user can clear game history)."""
        try:
            self.ui.display_clear_history_mode_start()

            # Initialize game history manager
            history_manager = GameHistoryManager()

            # Load game history
            try:
                games = history_manager.load_game_history()
                if not games:
                    self.ui.console.print("[yellow]No games found in history.[/yellow]")
                    return

                # Format games for display
                formatted_games = [
                    history_manager.format_game_summary(game) for game in games
                ]

                # Paginate games
                pages = history_manager.paginate_games(formatted_games, page_size=10)
                if not pages:
                    self.ui.console.print("[yellow]No games to display.[/yellow]")
                    return

                current_page = 1
                total_pages = len(pages)

                # Display current page
                self.ui.display_game_list(
                    pages[current_page - 1], current_page, total_pages
                )

                # Get user confirmation to clear history
                if self.ui.review_mode.confirm_clear_history():
                    # User confirmed, clear the history
                    success = self.stats_manager.clear_all_history()

                    # Display result
                    self.ui.review_mode.display_clear_history_result(
                        success, len(games)
                    )

            except Exception as e:
                self.ui.console.print(
                    f"[bold red]Error loading game history: {str(e)}[/bold red]"
                )

        except Exception as e:
            self.ui.console.print(
                f"[bold red]Error in clear history mode: {str(e)}[/bold red]"
            )
