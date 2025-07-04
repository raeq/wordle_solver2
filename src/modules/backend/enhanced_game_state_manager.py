# src/modules/backend/enhanced_game_state_manager.py
"""
Enhanced game state manager that supports both legacy and stateless solver strategies.
"""
from typing import List, Optional, Tuple, Union

# Import from the centralized __init__.py
from .solver import StatelessSolverStrategy

# Keep the LegacyStrategyAdapter import since it's not in __init__.py
from .solver.stateless_solver_strategy import LegacyStrategyAdapter

# Import strategy_factory for the StatelessGameStateManager class
from .solver.strategy_migration_factory import (
    StrategyMigrationManager,
    strategy_factory,
)
from .stateless_word_manager import StatelessWordManager


class EnhancedGameStateManager:
    """Enhanced game state manager with support for stateless strategies."""

    def __init__(
        self,
        word_manager: StatelessWordManager,
        strategy_name: str = "hybrid",
        use_stateless: bool = True,
        stateless_word_manager: Optional[StatelessWordManager] = None,
    ):
        """Initialize the enhanced game state manager.

        Args:
            word_manager: Word manager instance.
            strategy_name: Name of the strategy to use.
            use_stateless: Whether to use stateless strategy.
            stateless_word_manager: Optional stateless word manager.
        """
        self.word_manager = word_manager
        self.stateless_word_manager = stateless_word_manager or word_manager
        self.use_stateless = use_stateless
        self.guesses: List[Tuple[str, str]] = []
        self.max_guesses = 6

        # Initialize strategy migration manager
        self._strategy_manager = StrategyMigrationManager()
        self._strategy_name = strategy_name
        self._current_strategy = self._create_strategy(strategy_name, use_stateless)

    def _create_strategy(
        self, strategy_name: str, use_stateless: bool
    ) -> Union[StatelessSolverStrategy, LegacyStrategyAdapter]:
        """Create and return the appropriate strategy instance."""
        return self._strategy_manager.get_strategy(
            strategy_name=strategy_name,
            use_stateless=use_stateless,
            fallback_to_legacy=True,
        )

    def get_top_suggestions(self, count: int = 10) -> List[str]:
        """Get top N suggestions using the current strategy (enhanced version)."""
        if isinstance(self._current_strategy, StatelessSolverStrategy):
            # Pure stateless strategy
            return self._current_strategy.get_top_suggestions(
                constraints=self.guesses.copy(),
                count=count,
                word_manager=self.word_manager,
                stateless_word_manager=self.stateless_word_manager,
                prefer_common=True,
            )
        elif isinstance(self._current_strategy, LegacyStrategyAdapter):
            # Legacy strategy with stateless adapter
            return self._current_strategy.get_top_suggestions(
                constraints=self.guesses.copy(),
                count=count,
                word_manager=self.word_manager,
                stateless_word_manager=self.stateless_word_manager,
            )
        else:
            # Fallback to legacy
            return self._get_suggestions_legacy(count)

    def _get_suggestions_legacy(self, count: int = 10) -> List[str]:
        """Get suggestions using legacy strategy interface."""
        possible_words = self.word_manager.get_possible_words()
        common_words = self.word_manager.get_common_possible_words()

        if not possible_words:
            return []

        if len(possible_words) <= count:
            # If we have few words left, prioritize common ones first
            other_possible = [w for w in possible_words if w not in common_words]
            return common_words + other_possible

        # Use the legacy strategy interface
        if hasattr(self._current_strategy, "get_top_suggestions"):
            try:
                return self._current_strategy.get_top_suggestions(
                    possible_words, common_words, self.guesses, count, self.word_manager
                )
            except Exception as e:
                print(
                    f"Warning: Legacy strategy failed ({e}), returning possible words"
                )
                return possible_words[:count]
        else:
            # Ultimate fallback
            return possible_words[:count]

    def switch_strategy(self, strategy_name: str, use_stateless: bool = None) -> bool:
        """
        Switch to a different strategy during the game.

        Args:
            strategy_name: Name of the new strategy
            use_stateless: Whether to use stateless version (None = keep current preference)

        Returns:
            True if strategy was switched successfully
        """
        try:
            if use_stateless is None:
                use_stateless = self.use_stateless

            # Get new strategy
            new_strategy = self._create_strategy(strategy_name, use_stateless)

            # Update strategy
            self._current_strategy = new_strategy
            self._strategy_name = strategy_name
            self.use_stateless = use_stateless

            return True

        except Exception as e:
            print(f"Warning: Failed to switch strategy to {strategy_name}: {e}")
            return False

    def get_strategy_info(self) -> dict:
        """Get information about the current strategy."""
        return {
            "strategy_name": self._strategy_name,
            "is_stateless": isinstance(
                self._current_strategy, (StatelessSolverStrategy, LegacyStrategyAdapter)
            ),
            "use_stateless_preference": self.use_stateless,
            "strategy_class": self._current_strategy.__class__.__name__,
            "migration_status": self._strategy_manager.get_migration_status().get(
                self._strategy_name, "unknown"
            ),
        }

    def make_guess(self, guess: str, result: str) -> None:
        """Add a guess and its result to the game state.

        Args:
            guess: The word that was guessed
            result: The result pattern (G/Y/B for Green/Yellow/Black)
        """
        # Add the guess-result pair to the list of guesses
        self.guesses.append((guess, result))

        # Update the word manager if it has a method to apply constraints
        if hasattr(self.word_manager, "apply_single_constraint"):
            self.word_manager.apply_single_constraint(guess, result)

    def add_guess(self, guess: str, result: str) -> None:
        """Alias for make_guess to maintain backward compatibility with tests.

        Args:
            guess: The word that was guessed
            result: The result pattern (G/Y/B for Green/Yellow/Black)
        """
        self.make_guess(guess, result)

    def validate_strategy_performance(self) -> dict:
        """Validate current strategy performance against alternatives."""
        if not self.guesses:
            return {"error": "No guesses made yet, cannot validate performance"}

        try:
            # Run validation with current game state
            validation_results = self._strategy_manager.run_migration_validation(
                word_manager=self.word_manager,
                stateless_word_manager=self.stateless_word_manager,
            )

            current_strategy_result = validation_results.get(self._strategy_name, {})

            return {
                "current_strategy": self._strategy_name,
                "validation_result": current_strategy_result,
                "all_results": validation_results,
            }

        except Exception as e:
            return {"error": f"Validation failed: {e}"}

    def get_available_strategies(self) -> dict:
        """Get information about available strategies."""
        return self._strategy_manager.get_available_strategies()

    def get_recommendations(self) -> dict:
        """Get strategy recommendations."""
        return self._strategy_manager.get_recommendations()

    def benchmark_current_strategy(self, iterations: int = 10) -> dict:
        """Benchmark the current strategy performance."""
        import time

        if not self.guesses:
            return {"error": "No guesses made yet, cannot benchmark"}

        try:
            # Benchmark current suggestions
            start_time = time.time()

            for _ in range(iterations):
                self.get_top_suggestions(5)

            end_time = time.time()
            duration = end_time - start_time

            return {
                "strategy_name": self._strategy_name,
                "is_stateless": isinstance(
                    self._current_strategy,
                    (StatelessSolverStrategy, LegacyStrategyAdapter),
                ),
                "iterations": iterations,
                "total_time": duration,
                "avg_time_per_call": duration / iterations,
                "calls_per_second": iterations / duration,
            }

        except Exception as e:
            return {"error": f"Benchmark failed: {e}"}

    def reset(self) -> None:
        """Reset the game state manager for a new game."""
        self.guesses = []
        # Reset the word manager if it's not stateless
        self.word_manager.reset()
        # No need to reset the strategy as it should be stateless


class StatelessGameStateManager:
    """
    Pure stateless game state manager that doesn't maintain mutable state.

    This is a completely stateless approach where game state is passed
    as parameters rather than maintained as instance state.
    """

    def __init__(
        self,
        stateless_word_manager: Optional[StatelessWordManager] = None,
        default_strategy: str = "frequency",
    ):
        """
        Initialize stateless game state manager.

        Args:
            stateless_word_manager: Optional StatelessWordManager for pure stateless operations
            default_strategy: Default strategy to use
        """
        self.stateless_word_manager = stateless_word_manager
        self.default_strategy = default_strategy

    def get_suggestions(
        self,
        constraints: List[Tuple[str, str]],
        strategy_name: str = None,
        count: int = 10,
        prefer_common: bool = True,
        word_set: Optional[set] = None,
    ) -> List[str]:
        """
        Get suggestions for a given game state (completely stateless).

        Args:
            constraints: List of (guess, result) tuples representing game state
            strategy_name: Strategy to use (None = use default)
            count: Number of suggestions to return
            prefer_common: Whether to prefer common words
            word_set: Optional specific word set to consider

        Returns:
            List of suggested words
        """
        if strategy_name is None:
            strategy_name = self.default_strategy

        # Get strategy
        strategy = strategy_factory.create_strategy(
            strategy_name=strategy_name,
            use_stateless=True,
            stateless_word_manager=self.stateless_word_manager,
        )

        # Get suggestions
        if isinstance(strategy, (StatelessSolverStrategy, LegacyStrategyAdapter)):
            return strategy.get_top_suggestions(
                constraints=constraints,
                count=count,
                stateless_word_manager=self.stateless_word_manager,
                prefer_common=prefer_common,
                word_set=word_set,
            )
        else:
            # This should not happen since we're requesting stateless=True
            raise ValueError("Expected stateless strategy but got legacy strategy")

    def analyze_game_state(
        self, constraints: List[Tuple[str, str]], word_set: Optional[set] = None
    ) -> dict:
        """
        Analyze a game state and provide insights (stateless).

        Args:
            constraints: List of (guess, result) tuples
            word_set: Optional specific word set to analyze

        Returns:
            Dictionary with game state analysis
        """
        if self.stateless_word_manager:
            possible_words = self.stateless_word_manager.apply_multiple_constraints(
                constraints, word_set
            )
            common_words = self.stateless_word_manager.get_common_words_from_set(
                set(possible_words)
            )
        else:
            raise ValueError("StatelessWordManager is required")

        return {
            "total_possible_words": len(possible_words),
            "common_possible_words": len(common_words),
            "guesses_made": len(constraints),
            "sample_possible_words": possible_words[:10],
            "sample_common_words": common_words[:5],
            "game_phase": self._determine_game_phase(
                len(possible_words), len(constraints)
            ),
        }

    def _determine_game_phase(
        self, possible_words_count: int, guesses_made: int
    ) -> str:
        """Determine what phase of the game we're in."""
        if guesses_made == 0:
            return "opening"
        elif possible_words_count > 100:
            return "early"
        elif possible_words_count > 20:
            return "middle"
        elif possible_words_count > 5:
            return "late"
        else:
            return "endgame"
