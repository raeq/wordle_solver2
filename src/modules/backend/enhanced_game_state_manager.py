# src/modules/backend/enhanced_game_state_manager.py
"""
Enhanced game state manager that supports both legacy and stateless solver strategies.
"""
from typing import List, Optional, Tuple

from .game_state_manager import GameStateManager

# Import from the centralized __init__.py
from .solver import StatelessSolverStrategy

# Keep the LegacyStrategyAdapter import since it's not in __init__.py
from .solver.stateless_solver_strategy import LegacyStrategyAdapter
from .solver.strategy_migration_factory import strategy_factory
from .stateless_word_manager import StatelessWordManager
from .word_manager import WordManager


class EnhancedGameStateManager(GameStateManager):
    """
    Enhanced game state manager with support for stateless strategies.

    This extends the existing GameStateManager to work with both legacy
    and stateless solver strategies, providing a smooth migration path.
    """

    def __init__(
        self,
        word_manager: WordManager,
        strategy_name: str = "frequency",
        max_guesses: int = 6,
        use_stateless: bool = True,
        stateless_word_manager: Optional[StatelessWordManager] = None,
    ):
        """
        Initialize enhanced game state manager.

        Args:
            word_manager: WordManager instance for legacy compatibility
            strategy_name: Name of the strategy to use
            max_guesses: Maximum number of guesses allowed
            use_stateless: Whether to prefer stateless strategy implementations
            stateless_word_manager: Optional StatelessWordManager for pure stateless operations
        """
        # Initialize parent class with just word_manager
        super().__init__(word_manager)

        # Set max_guesses after initialization
        self.max_guesses = max_guesses

        self.strategy_name = strategy_name
        self.use_stateless = use_stateless
        self.stateless_word_manager = stateless_word_manager

        # Get strategy using the migration factory
        self.strategy = strategy_factory.create_strategy(
            strategy_name=strategy_name,
            use_stateless=use_stateless,
            word_manager=word_manager,
            stateless_word_manager=stateless_word_manager,
        )

        # Override the parent's strategy
        self.set_strategy(self.strategy)

        # Track if we're using a stateless strategy
        self.is_stateless_strategy = isinstance(
            self.strategy, (StatelessSolverStrategy, LegacyStrategyAdapter)
        )

    def get_top_suggestions(self, count: int = 10) -> List[str]:
        """Get top N suggestions using the current strategy (enhanced version)."""
        if self.is_stateless_strategy:
            # Use stateless interface
            return self._get_suggestions_stateless(count)
        else:
            # Use legacy interface (fallback)
            return self._get_suggestions_legacy(count)

    def _get_suggestions_stateless(self, count: int = 10) -> List[str]:
        """Get suggestions using stateless strategy interface."""
        try:
            # Convert current game state to constraints
            constraints = self.guesses.copy()

            # Get suggestions using stateless interface
            if isinstance(self.strategy, StatelessSolverStrategy):
                # Pure stateless strategy
                return self.strategy.get_top_suggestions(
                    constraints=constraints,
                    count=count,
                    word_manager=self.word_manager,
                    stateless_word_manager=self.stateless_word_manager,
                    prefer_common=True,
                )
            elif isinstance(self.strategy, LegacyStrategyAdapter):
                # Legacy strategy with stateless adapter
                return self.strategy.get_top_suggestions(
                    constraints=constraints,
                    count=count,
                    word_manager=self.word_manager,
                    stateless_word_manager=self.stateless_word_manager,
                )
            else:
                # Fallback to legacy
                return self._get_suggestions_legacy(count)

        except Exception as e:
            print(f"Warning: Stateless strategy failed ({e}), falling back to legacy")
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
        if hasattr(self.strategy, "get_top_suggestions"):
            try:
                return self.strategy.get_top_suggestions(
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
            new_strategy = strategy_factory.create_strategy(
                strategy_name=strategy_name,
                use_stateless=use_stateless,
                word_manager=self.word_manager,
                stateless_word_manager=self.stateless_word_manager,
            )

            # Update strategy
            self.strategy = new_strategy
            self.strategy_name = strategy_name
            self.use_stateless = use_stateless
            self.is_stateless_strategy = isinstance(
                new_strategy, (StatelessSolverStrategy, LegacyStrategyAdapter)
            )

            return True

        except Exception as e:
            print(f"Warning: Failed to switch strategy to {strategy_name}: {e}")
            return False

    def get_strategy_info(self) -> dict:
        """Get information about the current strategy."""
        return {
            "strategy_name": self.strategy_name,
            "is_stateless": self.is_stateless_strategy,
            "use_stateless_preference": self.use_stateless,
            "strategy_class": self.strategy.__class__.__name__,
            "migration_status": strategy_factory.migration_manager.get_migration_status().get(
                self.strategy_name, "unknown"
            ),
        }

    def validate_strategy_performance(self) -> dict:
        """Validate current strategy performance against alternatives."""
        if not self.guesses:
            return {"error": "No guesses made yet, cannot validate performance"}

        try:
            # Run validation with current game state
            validation_results = strategy_factory.run_migration_validation(
                word_manager=self.word_manager,
                stateless_word_manager=self.stateless_word_manager,
            )

            current_strategy_result = validation_results.get(self.strategy_name, {})

            return {
                "current_strategy": self.strategy_name,
                "validation_result": current_strategy_result,
                "all_results": validation_results,
            }

        except Exception as e:
            return {"error": f"Validation failed: {e}"}

    def get_available_strategies(self) -> dict:
        """Get information about available strategies."""
        return strategy_factory.migration_manager.get_available_strategies()

    def get_recommendations(self) -> dict:
        """Get strategy recommendations."""
        return strategy_factory.get_recommendations()

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
                "strategy_name": self.strategy_name,
                "is_stateless": self.is_stateless_strategy,
                "iterations": iterations,
                "total_time": duration,
                "avg_time_per_call": duration / iterations,
                "calls_per_second": iterations / duration,
            }

        except Exception as e:
            return {"error": f"Benchmark failed: {e}"}


class StatelessGameStateManager:
    """
    Pure stateless game state manager that doesn't maintain mutable state.

    This is a completely stateless approach where game state is passed
    as parameters rather than maintained as instance state.
    """

    def __init__(
        self,
        word_manager: Optional[WordManager] = None,
        stateless_word_manager: Optional[StatelessWordManager] = None,
        default_strategy: str = "frequency",
    ):
        """
        Initialize stateless game state manager.

        Args:
            word_manager: Optional WordManager for legacy compatibility
            stateless_word_manager: Optional StatelessWordManager for pure stateless operations
            default_strategy: Default strategy to use
        """
        self.word_manager = word_manager
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
            word_manager=self.word_manager,
            stateless_word_manager=self.stateless_word_manager,
        )

        # Get suggestions
        if isinstance(strategy, (StatelessSolverStrategy, LegacyStrategyAdapter)):
            return strategy.get_top_suggestions(
                constraints=constraints,
                count=count,
                word_manager=self.word_manager,
                stateless_word_manager=self.stateless_word_manager,
                prefer_common=prefer_common,
                word_set=word_set,
            )
        else:
            # Fallback for legacy strategies
            if self.word_manager:
                possible_words = self.word_manager.apply_multiple_constraints(
                    constraints, word_set
                )
                common_words = [
                    w for w in possible_words if w in self.word_manager.common_words
                ]

                return strategy.get_top_suggestions(
                    possible_words, common_words, constraints, count, self.word_manager
                )
            else:
                raise ValueError("Legacy strategy requires WordManager")

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
        elif self.word_manager:
            possible_words = self.word_manager.apply_multiple_constraints(
                constraints, word_set
            )
            common_words = [
                w for w in possible_words if w in self.word_manager.common_words
            ]
        else:
            raise ValueError("Either word_manager or stateless_word_manager required")

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
