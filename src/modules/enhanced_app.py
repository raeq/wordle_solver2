# src/modules/enhanced_app.py
"""
Enhanced application module that uses stateless solver strategies and improved game state management.
"""


from src.common.di_container import get_container
from src.config.settings import get_environment, get_settings
from src.frontend.cli import CLIInterface

from .backend.enhanced_game_state_manager import (
    EnhancedGameStateManager,
    StatelessGameStateManager,
)
from .backend.exceptions import (
    InvalidColorError,
    InvalidGuessError,
    InvalidResultError,
    WordleError,
)
from .backend.game_engine import GameEngine
from .backend.result_color import ResultColor
from .backend.solver.strategy_migration_factory import strategy_factory
from .backend.stateless_word_manager import StatelessWordManager
from .backend.stats_manager import StatsManager
from .logging_utils import log_method


class EnhancedWordleSolverApp:
    """Enhanced application that uses stateless solver strategies and improved performance."""

    def __init__(self, use_stateless: bool = True) -> None:
        # Get configuration and DI container
        self.config = get_settings()
        self.container = get_container()
        self.use_stateless = use_stateless

        # Initialize current strategy from SolverSettings instead of GameSettings
        self.current_strategy_name = self.config.solver.default_strategy

        # Initialize components with enhanced capabilities
        self._components = self._initialize_enhanced_components()

    def _should_catch_exceptions(self) -> bool:
        """
        Determine whether exceptions should be caught based on the environment.

        In PROD environment, exceptions are caught to prevent app crashes.
        In DEV environment, exceptions are allowed to propagate for easier debugging.

        Returns:
            bool: True if exceptions should be caught, False otherwise
        """
        environment = get_environment()
        return environment == "PROD"

    def _initialize_enhanced_components(self) -> dict:
        """Initialize enhanced application components with stateless capabilities."""
        # Initialize stateless word manager
        stateless_word_manager = StatelessWordManager()

        # Initialize enhanced game state manager
        enhanced_solver = EnhancedGameStateManager(
            word_manager=stateless_word_manager,
            strategy_name=self.current_strategy_name,
            use_stateless=self.use_stateless,
            stateless_word_manager=stateless_word_manager,
        )

        # Initialize stateless game state manager
        stateless_game_manager = StatelessGameStateManager(
            stateless_word_manager=stateless_word_manager,
            default_strategy=self.current_strategy_name,
        )

        return {
            "word_manager": stateless_word_manager,
            "solver": enhanced_solver,
            "stateless_game_manager": stateless_game_manager,
            "game_engine": self.container.get(GameEngine),
            "stats_manager": self.container.get(StatsManager),
            "ui": self.container.get(CLIInterface),
        }

    @property
    def word_manager(self) -> StatelessWordManager:
        """Get word manager component."""
        return self._components["word_manager"]  # type: ignore

    @property
    def solver(self) -> EnhancedGameStateManager:
        """Get enhanced solver component."""
        return self._components["solver"]

    @property
    def stateless_game_manager(self) -> StatelessGameStateManager:
        """Get stateless game manager component."""
        return self._components["stateless_game_manager"]

    @property
    def game_engine(self) -> GameEngine:
        """Get game engine component."""
        return self._components["game_engine"]

    @property
    def stats_manager(self) -> StatsManager:
        """Get stats manager component."""
        return self._components["stats_manager"]

    @property
    def ui(self) -> CLIInterface:
        """Get UI component."""
        return self._components["ui"]

    @log_method("DEBUG")
    def run(self) -> None:
        """Main enhanced application loop."""
        self.ui.display_welcome()
        self._display_enhancement_info()

        # Allow user to select initial strategy
        self._select_initial_strategy()

        while True:
            game_mode = self.ui.get_game_mode()

            if game_mode == "solver":
                self._run_enhanced_solver_mode()
            elif game_mode == "review":
                self._run_review_mode()
            elif game_mode == "clear":
                self._run_clear_history_mode()
            elif game_mode == "analysis":
                self._run_analysis_mode()
            elif game_mode == "benchmark":
                self._run_benchmark_mode()
            else:
                self._run_enhanced_game_mode()

            if not self.ui.ask_play_again():
                break

        self._display_final_stats()

    def _display_enhancement_info(self) -> None:
        """Display information about the enhanced features."""
        self.ui.console.print("\n[bold cyan]🚀 Enhanced Wordle Solver[/bold cyan]")
        self.ui.console.print(
            f"[dim]Stateless Mode: {'Enabled' if self.use_stateless else 'Disabled'}[/dim]"
        )

        if self.use_stateless:
            # Show migration status
            status = strategy_factory.migration_manager.get_migration_status()
            completed_count = sum(1 for s in status.values() if s == "completed")
            total_count = len(status)
            self.ui.console.print(
                f"[dim]Migrated Strategies: {completed_count}/{total_count}[/dim]"
            )

    def _select_initial_strategy(self) -> None:
        """Allow user to select the initial strategy with migration info."""
        self.ui.console.print("\n[bold]🧠 Strategy Selection[/bold]")

        # Display available strategies and their status
        if self.use_stateless:
            available_strategies = (
                strategy_factory.migration_manager.get_available_strategies()
            )
            self.ui.console.print("\n[bold]Available Strategies:[/bold]")
            for name, info in available_strategies.items():
                status_icon = "✅" if info["stateless_available"] else "🔄"
                status_text = (
                    "Stateless Ready" if info["stateless_available"] else "Legacy Only"
                )
                self.ui.console.print(f"  {status_icon} {name.upper()}: {status_text}")

        new_strategy_name = self.ui.get_strategy_selection(self.current_strategy_name)
        if new_strategy_name:
            self._change_strategy(new_strategy_name)

        self.ui.display_current_strategy(self.current_strategy_name)

    def _change_strategy(self, strategy_name: str) -> None:
        """Change the current solver strategy using the enhanced system."""
        if self._should_catch_exceptions():
            try:
                self._change_strategy_impl(strategy_name)
            except Exception as e:
                self.ui.console.print(
                    f"[bold red]Error changing strategy: {str(e)}[/bold red]"
                )
        else:
            # In development mode, let exceptions propagate
            self._change_strategy_impl(strategy_name)

    def _change_strategy_impl(self, strategy_name: str) -> None:
        """Implementation of changing the solver strategy."""
        # Use the enhanced game state manager's strategy switching
        success = self.solver.switch_strategy(
            strategy_name, use_stateless=self.use_stateless
        )

        if success:
            self.current_strategy_name = strategy_name
            strategy_info = self.solver.get_strategy_info()

            self.ui.console.print(
                f"[bold green]✓ Strategy changed to: {strategy_name.upper()}[/bold green]"
            )
            if self.use_stateless:
                status = "Stateless" if strategy_info["is_stateless"] else "Legacy"
                self.ui.console.print(f"[dim]Mode: {status}[/dim]")
        else:
            self.ui.console.print(
                f"[bold red]Failed to change strategy to: {strategy_name}[/bold red]"
            )

    @log_method("DEBUG")
    def _run_enhanced_solver_mode(self) -> None:
        """Run enhanced solver mode with performance monitoring."""
        # Only catch exceptions in production mode
        if self._should_catch_exceptions():
            try:
                self._run_enhanced_solver_mode_impl()
            except Exception as e:
                self._handle_solver_mode_error(e)
        else:
            # In development mode, let exceptions propagate
            self._run_enhanced_solver_mode_impl()

    def _run_enhanced_solver_mode_impl(self) -> None:
        """Implementation of enhanced solver mode."""
        # Reset everything first to ensure a clean state
        # Reset the backend solver
        self.solver.reset()

        # Reset the UI's solver mode to clear any frontend state
        self.ui.solver_mode.reset()

        # Clear any guesses in the game state
        self.ui.solver_mode.game_state.reset()

        # Display start screen after resetting
        self.ui.display_solver_mode_start()

        # Show initial suggestions with performance info
        self._show_enhanced_suggestions()

        guesses_history = []
        attempt = 1
        max_attempts = 6
        won = False

        # Track performance metrics
        total_suggestion_time = 0.0

        # Main solver loop
        while attempt <= max_attempts and not won:
            import time

            start_time = time.time()

            won = self._process_enhanced_solver_turn(
                guesses_history, attempt, max_attempts
            )

            end_time = time.time()
            total_suggestion_time += end_time - start_time

            if not won:
                attempt += 1

        # Record enhanced game statistics
        self._finalize_enhanced_solver_mode(
            guesses_history, won, attempt, max_attempts, total_suggestion_time
        )

    def _process_enhanced_solver_turn(
        self, guesses_history: list, attempt: int, max_attempts: int
    ) -> bool:
        """Process a single turn in enhanced solver mode."""
        # Only catch specific exceptions in production mode
        if self._should_catch_exceptions():
            try:
                return self._process_enhanced_solver_turn_impl(
                    guesses_history, attempt, max_attempts
                )
            except (
                InvalidGuessError,
                InvalidResultError,
                InvalidColorError,
                WordleError,
            ) as e:
                self.ui.console.print(
                    f"[bold red]{type(e).__name__}: {str(e)}[/bold red]"
                )
                return False
        else:
            # In development mode, let exceptions propagate
            return self._process_enhanced_solver_turn_impl(
                guesses_history, attempt, max_attempts
            )

    def _process_enhanced_solver_turn_impl(
        self, guesses_history: list, attempt: int, max_attempts: int
    ) -> bool:
        """Implementation of processing a single turn in enhanced solver mode."""
        # Get guess and result from user
        guess, result = self.ui.get_guess_and_result()

        # Handle special commands
        if guess == "HINT":
            self._show_enhanced_suggestions()
            return False
        if guess == "STRATEGY":
            self._handle_enhanced_strategy_command()
            return False
        if guess == "ANALYSIS":
            self._show_game_analysis()
            return False

        # Update solver state
        self.solver.make_guess(guess, result)
        guesses_history.append([guess, result, self.current_strategy_name])

        # Display colored result
        self.ui.display_guess_result(guess, result, attempt, max_attempts)

        # Check if solved
        if result == ResultColor.GREEN.value * 5:
            self.ui.console.print(
                "\n[bold green]Congratulations! You've found the solution![/bold green]"
            )
            return True

        # Show enhanced suggestions for next turn
        self._show_enhanced_suggestions()
        return False

    def _show_enhanced_suggestions(self) -> None:
        """Show enhanced word suggestions with performance metrics."""
        import time

        start_time = time.time()
        suggestions = self.solver.get_top_suggestions(10)
        suggestion_time = time.time() - start_time

        # Get additional info
        strategy_info = self.solver.get_strategy_info()
        possible_words = self.word_manager.get_possible_words()
        common_words = self.word_manager.get_common_possible_words()

        # Display suggestions with enhanced info
        self.ui.display_suggestions(
            suggestions,
            len(possible_words),
            common_words,
            strategy_name=self.current_strategy_name,
        )

        # Show performance and strategy info
        self.ui.console.print(
            f"[dim]Strategy: {strategy_info['strategy_class']} "
            f"({'Stateless' if strategy_info['is_stateless'] else 'Legacy'}) "
            f"| Time: {suggestion_time:.3f}s[/dim]"
        )

    def _handle_enhanced_strategy_command(self) -> None:
        """Handle enhanced strategy change command with migration info."""
        if self.use_stateless:
            # Show current strategy performance
            benchmark = self.solver.benchmark_current_strategy(iterations=5)
            if "error" not in benchmark:
                self.ui.console.print(
                    f"[dim]Current Strategy Performance: {benchmark['avg_time_per_call']:.4f}s per call[/dim]"
                )

        new_strategy_name = self.ui.get_strategy_selection(self.current_strategy_name)
        if new_strategy_name:
            self._change_strategy(new_strategy_name)
        else:
            self.ui.console.print("[dim]Strategy unchanged.[/dim]")

    def _show_game_analysis(self) -> None:
        """Show analysis of current game state."""
        if self.use_stateless and self.stateless_game_manager:
            # Get current constraints
            constraints = self.solver.guesses

            # Analyze game state
            analysis = self.stateless_game_manager.analyze_game_state(constraints)

            self.ui.console.print("\n[bold]📊 Game State Analysis[/bold]")
            self.ui.console.print(
                f"Total possible words: {analysis['total_possible_words']}"
            )
            self.ui.console.print(
                f"Common possible words: {analysis['common_possible_words']}"
            )
            self.ui.console.print(f"Game phase: {analysis['game_phase'].upper()}")
            self.ui.console.print(f"Guesses made: {analysis['guesses_made']}")

            if analysis["sample_possible_words"]:
                self.ui.console.print(
                    f"Sample words: {', '.join(analysis['sample_possible_words'][:5])}"
                )

    def _run_analysis_mode(self) -> None:
        """Run analysis mode for detailed game insights."""
        if not self.use_stateless:
            self.ui.console.print(
                "[yellow]Analysis mode requires stateless features to be enabled.[/yellow]"
            )
            return

        self.ui.console.print("\n[bold]📊 Game Analysis Mode[/bold]")
        self.ui.console.print("Enter a sequence of guesses and results to analyze...")

        constraints = []

        while True:
            if self._should_catch_exceptions():
                try:
                    result = self._process_analysis_input(constraints)
                    if result is False:  # Signal to break the loop
                        break
                except (InvalidGuessError, InvalidResultError) as e:
                    self.ui.console.print(f"[red]Error: {e}[/red]")
                except KeyboardInterrupt:
                    break
            else:
                # In development mode, let exceptions propagate
                result = self._process_analysis_input(constraints)
                if result is False:  # Signal to break the loop
                    break

        if constraints:
            # Final analysis
            final_analysis = self.stateless_game_manager.analyze_game_state(constraints)
            self.ui.console.print("\n[bold]Final Analysis:[/bold]")
            for key, value in final_analysis.items():
                self.ui.console.print(f"  {key.replace('_', ' ').title()}: {value}")

    def _process_analysis_input(self, constraints: list) -> bool:
        """Process a single input in analysis mode.

        Returns:
            bool: False if user wants to exit, True otherwise
        """
        guess, result = self.ui.get_guess_and_result()

        if guess.upper() == "DONE":
            return False

        constraints.append((guess, result))

        # Analyze current state
        analysis = self.stateless_game_manager.analyze_game_state(constraints)

        self.ui.console.print(f"\n[dim]After guess {len(constraints)}:[/dim]")
        self.ui.console.print(f"  Possible words: {analysis['total_possible_words']}")
        self.ui.console.print(f"  Game phase: {analysis['game_phase']}")

        # Get suggestions for next guess
        suggestions = self.stateless_game_manager.get_suggestions(constraints, count=5)
        if suggestions:
            self.ui.console.print(f"  Top suggestions: {', '.join(suggestions[:3])}")

        return True

    def _run_benchmark_mode(self) -> None:
        """Run benchmark mode to compare strategy performance."""
        if not self.use_stateless:
            self.ui.console.print(
                "[yellow]Benchmark mode requires stateless features to be enabled.[/yellow]"
            )
            return

        self.ui.console.print("\n[bold]⚡ Strategy Benchmark Mode[/bold]")

        # Run validation for all strategies
        validation_results = strategy_factory.run_migration_validation(
            self.word_manager, self.stateless_word_manager
        )

        self.ui.console.print("\n[bold]Strategy Comparison Results:[/bold]")

        for strategy_name, result in validation_results.items():
            if result["status"] == "tested":
                equiv_status = (
                    "✅ Equivalent" if result["equivalent"] else "⚠️  Different"
                )
                self.ui.console.print(
                    f"  {strategy_name.upper()}: {result['overlap_percentage']:.1f}% overlap - {equiv_status}"
                )
            elif result["status"] == "error":
                self.ui.console.print(
                    f"  {strategy_name.upper()}: ❌ Error - {result['error']}"
                )
            else:
                self.ui.console.print(f"  {strategy_name.upper()}: ⏳ Not migrated")

    def _run_enhanced_game_mode(self) -> None:
        """Run enhanced game mode with better performance monitoring."""
        # This would be similar to the original game mode but with enhanced features
        # For brevity, I'll delegate to the original implementation
        self._run_game_mode()

    def _run_game_mode(self) -> None:
        """Run the standard game mode where the app selects a word and user guesses."""
        # Reset game state and get the game ID
        self.game_engine.start_new_game()
        game_state = self.game_engine.get_game_state()
        game_id = game_state.get("game_id", "unknown")

        # Get game config
        max_attempts = 6
        guesses_history = []
        attempt = 1
        won = False

        # Display instructions with game ID
        self.ui.display_play_mode_start(game_id)

        # Main game loop
        while attempt <= max_attempts and not won:
            # Get user guess
            guess = self.ui.get_guess_input()

            # Handle special commands
            if guess.upper() == "HINT":
                # Generate suggestions using previous guesses to filter words
                if not guesses_history:
                    # No guesses yet, show common words
                    suggestions = self.word_manager.get_common_words()[:10]
                else:
                    # Apply constraints from previous guesses
                    constraints = [(g, r) for g, r in guesses_history]
                    # Get words matching all constraints so far, prioritizing common words
                    filtered_words = self.word_manager.apply_multiple_constraints(
                        constraints
                    )
                    # First try to get common words that match the constraints
                    common_filtered = [
                        w for w in filtered_words if w in self.word_manager.common_words
                    ]

                    if common_filtered:
                        suggestions = common_filtered[:10]
                    else:
                        # If no common words match, use any valid words
                        suggestions = filtered_words[:10]

                self.ui.console.print("\n[bold]Suggested words:[/bold]")
                self.ui.console.print(", ".join(suggestions[:5]))
                continue
            elif guess.upper() == "STRATEGY":
                # Allow user to change strategy for hints
                self._handle_enhanced_strategy_command()
                continue

            # Process the guess
            try:
                result, won = self.game_engine.make_guess(guess, mode="manual")

                # Record the guess locally for display purposes only
                guesses_history.append([guess, result])

                # Display result
                self.ui.display_guess_result(guess, result, attempt, max_attempts)

                # Increment attempt counter
                if not won:
                    attempt += 1
            except Exception as e:
                # Display error message but allow user to try again
                self.ui.console.print(f"[bold red]Error: {str(e)}[/bold red]")
                self.ui.console.print(
                    "[italic]Please try again with a valid 5-letter word.[/italic]"
                )

        # Game over - display result
        if won:
            self.ui.console.print(
                f"\n[bold green]Congratulations! You solved it in {attempt}/{max_attempts} attempts![/bold green]"
            )
        else:
            self.ui.console.print(
                f"\n[bold red]Game over! The word was: {self.game_engine.target_word}[/bold red]"
            )

        # Note: Game saving is now handled automatically by the GameEngine when the game ends

        # Display game history
        self.ui.display_guess_history(guesses_history)

    def _run_review_mode(self) -> None:
        """Run review mode to display game history."""
        import logging

        logger = logging.getLogger("wordle_solver")
        logger.debug("Running ENHANCED review mode from enhanced_app.py")

        from .backend.game_history_manager import GameHistoryManager

        # Initialize history manager
        history_manager = GameHistoryManager()

        # Display review mode start
        self.ui.display_review_mode_start()

        # Load game history
        all_games = history_manager.load_game_history()
        if not all_games:
            self.ui.console.print("\n[yellow]No game history found.[/yellow]")
            return

        # Paginate games for display
        game_pages = history_manager.paginate_games(all_games)

        page_index = 0
        while page_index < len(game_pages):
            # Display current page
            self.ui.display_game_list(
                game_pages[page_index], page_index + 1, len(game_pages)
            )

            # Get user action - pass the current page and total pages
            action = self.ui.get_game_review_action(page_index + 1, len(game_pages))

            if action == "q":
                # Quit review mode
                break
            elif action == "n" and page_index < len(game_pages) - 1:
                # Next page
                page_index += 1
            elif action == "p" and page_index > 0:
                # Previous page
                page_index -= 1
            elif action == "clear":
                # Handle clear history command
                if self._handle_clear_history():
                    # Reload game history if cleared successfully
                    all_games = history_manager.load_game_history()
                    if not all_games:
                        self.ui.console.print(
                            "\n[yellow]No game history remaining.[/yellow]"
                        )
                        break
                    game_pages = history_manager.paginate_games(all_games)
                    page_index = 0
            elif action.isalnum() and len(action) >= 3:
                # Try to find game by ID
                game = history_manager.get_game_by_id(action)
                if game:
                    self.ui.display_detailed_game_review(game)
                else:
                    self.ui.console.print(
                        f"[yellow]Game with ID '{action}' not found.[/yellow]"
                    )
            else:
                # Invalid action
                self.ui.console.print("[yellow]Invalid action. Try again.[/yellow]")

    def _handle_clear_history(self) -> bool:
        """
        Handle the clear history functionality.

        Returns:
            bool: True if history was cleared successfully, False otherwise.
        """
        # Check if there's any history to clear
        if not self.stats_manager.has_history():
            self.ui.console.print("[yellow]No history to clear.[/yellow]")
            return False

        # Get number of games to be deleted
        history_count = self.stats_manager.get_history_count()

        # Ask for confirmation
        if not self.ui.review_mode.confirm_clear_history():
            self.ui.console.print("[yellow]Clear history operation cancelled.[/yellow]")
            return False

        # Try to clear history
        success = self.stats_manager.clear_all_history()

        # Display result
        self.ui.review_mode.display_clear_history_result(success, history_count)

        return success

    def _run_clear_history_mode(self) -> None:
        """Clear all game history and statistics."""
        self.ui.console.print("\n[bold yellow]🧹 Clear History Mode[/bold yellow]")

        if self.ui.get_confirmation(
            "Are you sure you want to clear all game history and statistics?"
        ):
            # Clear statistics and history
            self.stats_manager.clear_all_history()
            self.ui.console.print(
                "[green]✓ Game history and statistics have been cleared.[/green]"
            )
        else:
            self.ui.console.print("[dim]Operation cancelled.[/dim]")

    def _finalize_enhanced_solver_mode(
        self,
        guesses_history: list,
        won: bool,
        attempt: int,
        max_attempts: int,
        total_time: float,
    ) -> None:
        """Finalize enhanced solver mode with performance metrics."""
        # For backward compatibility, check if game_engine has stats_manager
        if (
            hasattr(self.game_engine, "stats_manager")
            and self.game_engine.stats_manager
        ):
            # Game engine will handle recording
            if not self.game_engine.is_game_over():
                # If game engine doesn't have an active game, we need to record directly
                self.stats_manager.record_game(
                    guesses_history, won, attempt, mode="enhanced_solver"
                )
        else:
            # Fall back to direct recording if game_engine doesn't have stats_manager
            self.stats_manager.record_game(
                guesses_history, won, attempt, mode="enhanced_solver"
            )

        # Display results with performance info
        self._display_enhanced_solver_result(
            won, attempt, max_attempts, guesses_history, total_time
        )
        self.word_manager.reset()

    def _finalize_solver_mode(self, guesses_history, won, attempt, max_attempts=6):
        """
        Finalize solver mode and record game statistics.

        Args:
            guesses_history: List of guesses made during the game
            won: Whether the game was won
            attempt: The final attempt number
            max_attempts: Maximum number of attempts allowed
        """
        # Record the game with solver mode
        self.stats_manager.record_game(guesses_history, won, attempt, mode="solver")

    def _display_enhanced_solver_result(
        self,
        won: bool,
        attempt: int,
        max_attempts: int,
        guesses_history: list,
        total_time: float,
    ) -> None:
        """Display enhanced solver results with performance metrics."""
        if won:
            self.ui.console.print(
                f"\n[bold green]Congratulations! You solved it in {attempt}/{max_attempts} attempts![/bold green]"
            )
        else:
            self.ui.console.print(
                "\n[bold red]Game over! You didn't find the solution.[/bold red]"
            )

        # Display performance metrics
        if total_time > 0:
            avg_time_per_turn = (
                total_time / len(guesses_history) if guesses_history else 0
            )
            self.ui.console.print(
                f"[dim]Average time per suggestion: {avg_time_per_turn:.3f}s[/dim]"
            )

        # Display guess history
        if guesses_history:
            self.ui.display_guess_history(guesses_history)

    def _display_final_stats(self) -> None:
        """Display final statistics with enhanced insights."""
        stats = self.stats_manager.get_stats()
        self.ui.display_game_stats(stats)

        if self.use_stateless:
            # Show migration status summary
            status = strategy_factory.migration_manager.get_migration_status()
            completed_strategies = [
                name for name, stat in status.items() if stat == "completed"
            ]

            self.ui.console.print(
                f"\n[dim]Stateless strategies used: {', '.join(completed_strategies)}[/dim]"
            )

        self.ui.console.print(
            "\n[bold blue]Thanks for using Enhanced Wordle Solver! 🚀[/bold blue]"
        )

    def _handle_solver_mode_error(self, error: Exception) -> None:
        """Handle errors in solver mode."""
        self.ui.console.print(f"[bold red]Unexpected error: {str(error)}[/bold red]")
        self.ui.console.print(
            "[bold yellow]The application will continue, but the current game has been aborted.[/bold yellow]"
        )
