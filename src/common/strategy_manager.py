"""
Enhanced strategy management with improved factory pattern and performance optimizations.
"""

import time
from typing import Any, Dict, List, Optional, Type

from src.common.cache import cache_strategy_results
from src.common.types import GuessHistory
from src.modules.backend.solver.constants import (
    DEFAULT_SUGGESTIONS_COUNT,
    FIRST_ARRAY_INDEX,
)

# Import stateless strategy classes directly
from src.modules.backend.solver.stateless_entropy_strategy import (
    StatelessEntropyStrategy,
)
from src.modules.backend.solver.stateless_frequency_strategy import (
    StatelessFrequencyStrategy,
)
from src.modules.backend.solver.stateless_hybrid_strategy import StatelessHybridStrategy
from src.modules.backend.solver.stateless_minimax_strategy import (
    StatelessMinimaxStrategy,
)
from src.modules.backend.solver.stateless_solver_strategy import StatelessSolverStrategy
from src.modules.backend.solver.stateless_two_step_strategy import (
    StatelessTwoStepStrategy,
)
from src.modules.backend.solver.stateless_weighted_gain_strategy import (
    StatelessWeightedGainStrategy,
)

# Type aliases for backward compatibility
EntropyStrategy = StatelessEntropyStrategy
FrequencyStrategy = StatelessFrequencyStrategy
HybridFrequencyEntropyStrategy = StatelessHybridStrategy
MinimaxStrategy = StatelessMinimaxStrategy
SolverStrategy = StatelessSolverStrategy
TwoStepStrategy = StatelessTwoStepStrategy
WeightedGainStrategy = StatelessWeightedGainStrategy


class StrategyManager:
    """Enhanced strategy manager with caching and performance monitoring."""

    def __init__(self):
        self._strategies: Dict[str, Type[StatelessSolverStrategy]] = {}
        self._strategy_instances: Dict[str, StatelessSolverStrategy] = {}
        self._performance_stats: Dict[str, Dict[str, Any]] = {}

    def register_strategy(
        self, name: str, strategy_class: Type[SolverStrategy]
    ) -> None:
        """Register a new strategy class."""
        self._strategies[name] = strategy_class
        self._performance_stats[name] = {
            "total_calls": FIRST_ARRAY_INDEX,
            "total_time": 0.0,
            "average_time": 0.0,
            "last_used": None,
        }

    def get_strategy(self, name: str) -> SolverStrategy:
        """Get a strategy instance (cached for performance)."""
        if name not in self._strategies:
            raise ValueError(f"Unknown strategy: {name}")

        # Use cached instance if available
        if name not in self._strategy_instances:
            self._strategy_instances[name] = self._strategies[name]()

        return self._strategy_instances[name]

    @cache_strategy_results
    def get_suggestions_with_monitoring(
        self,
        strategy_name: str,
        possible_words: List[str],
        common_words: List[str],
        guesses_so_far: GuessHistory,
        count: int = DEFAULT_SUGGESTIONS_COUNT,
        word_manager: Any = None,
    ) -> List[str]:
        """Get suggestions with performance monitoring."""
        start_time = time.time()

        try:
            strategy = self.get_strategy(strategy_name)
            suggestions = strategy.get_top_suggestions(
                possible_words, common_words, guesses_so_far, count, word_manager
            )

            # Update performance stats
            execution_time = time.time() - start_time
            stats = self._performance_stats[strategy_name]
            stats["total_calls"] += 1
            stats["total_time"] += execution_time
            stats["average_time"] = stats["total_time"] / stats["total_calls"]
            stats["last_used"] = time.time()

            return suggestions

        except Exception as e:
            # Still update stats even if there's an error
            execution_time = time.time() - start_time
            stats = self._performance_stats[strategy_name]
            stats["total_calls"] += 1
            stats["total_time"] += execution_time
            stats["average_time"] = stats["total_time"] / stats["total_calls"]
            raise e

    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names."""
        return list(self._strategies.keys())

    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all strategies."""
        return self._performance_stats.copy()

    def get_recommended_strategy(
        self, possible_words_count: int, guesses_made: int
    ) -> str:
        """Recommend the best strategy based on game state."""
        # Early game (first 2 guesses, many words remaining)
        if guesses_made < 2 and possible_words_count > 100:
            return "entropy"  # Best for information gain

        # Mid game (some constraints, moderate word count)
        if guesses_made < 4 and possible_words_count > 10:
            return "weighted_gain"  # Balance of entropy and frequency

        # Late game (few words remaining)
        if possible_words_count <= 10:
            return "frequency"  # Focus on most common words

        # Very constrained (very few words)
        if possible_words_count <= 3:
            return "minimax"  # Minimize worst case

        # Default fallback
        return "hybrid_frequency_entropy"

    def clear_instances(self) -> None:
        """Clear cached strategy instances (useful for testing)."""
        self._strategy_instances.clear()


# Global strategy manager instance
_strategy_manager: Optional[StrategyManager] = None


def get_strategy_manager() -> StrategyManager:
    """Get the global strategy manager instance."""
    global _strategy_manager
    if _strategy_manager is None:
        _strategy_manager = _create_default_strategy_manager()
    return _strategy_manager


def _create_default_strategy_manager() -> StrategyManager:
    """Create and configure the default strategy manager."""
    manager = StrategyManager()

    # Register all available strategies
    manager.register_strategy("frequency", FrequencyStrategy)
    manager.register_strategy("entropy", EntropyStrategy)
    manager.register_strategy("weighted_gain", WeightedGainStrategy)
    manager.register_strategy("minimax", MinimaxStrategy)
    manager.register_strategy("two_step", TwoStepStrategy)
    manager.register_strategy(
        "hybrid_frequency_entropy", HybridFrequencyEntropyStrategy
    )

    return manager


def reset_strategy_manager() -> None:
    """Reset the global strategy manager (useful for testing)."""
    global _strategy_manager
    _strategy_manager = None
