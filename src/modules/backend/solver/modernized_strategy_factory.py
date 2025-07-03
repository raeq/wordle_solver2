# src/modules/backend/solver/modernized_strategy_factory.py
"""
Modernized strategy factory for the fully stateless Wordle solver system.
This replaces all legacy strategy factories and provides a clean, stateless interface.
"""
from typing import Dict

from .stateless_entropy_strategy import StatelessEntropyStrategy
from .stateless_frequency_strategy import StatelessFrequencyStrategy
from .stateless_hybrid_strategy import StatelessHybridStrategy
from .stateless_minimax_strategy import StatelessMinimaxStrategy
from .stateless_solver_strategy import StatelessSolverStrategy
from .stateless_two_step_strategy import StatelessTwoStepStrategy
from .stateless_weighted_gain_strategy import StatelessWeightedGainStrategy


class ModernizedStrategyFactory:
    """Modernized factory for creating stateless solver strategies only."""

    # Map of strategy names to their stateless classes
    _strategies: Dict[str, type] = {
        "frequency": StatelessFrequencyStrategy,
        "entropy": StatelessEntropyStrategy,
        "hybrid": StatelessHybridStrategy,
        "two_step": StatelessTwoStepStrategy,
        "weighted_gain": StatelessWeightedGainStrategy,
        "minimax": StatelessMinimaxStrategy,
    }

    @classmethod
    def create_strategy(cls, strategy_name: str, **kwargs) -> StatelessSolverStrategy:
        """
        Create a stateless strategy instance.

        Args:
            strategy_name: Name of the strategy to create
            **kwargs: Additional arguments for strategy initialization

        Returns:
            StatelessSolverStrategy instance

        Raises:
            ValueError: If strategy name is not found
        """
        strategy_name = strategy_name.lower()

        if strategy_name not in cls._strategies:
            available = list(cls._strategies.keys())
            raise ValueError(
                f"Strategy '{strategy_name}' not found. Available: {available}"
            )

        strategy_class = cls._strategies[strategy_name]
        return strategy_class(**kwargs)

    @classmethod
    def get_available_strategies(cls) -> Dict[str, str]:
        """Get information about available strategies."""
        return {
            name: strategy_class.__name__
            for name, strategy_class in cls._strategies.items()
        }

    @classmethod
    def register_strategy(cls, name: str, strategy_class: type) -> None:
        """Register a new strategy class."""
        if not issubclass(strategy_class, StatelessSolverStrategy):
            raise ValueError("Strategy must be a subclass of StatelessSolverStrategy")
        cls._strategies[name.lower()] = strategy_class


# Global instance for easy access
modernized_strategy_factory = ModernizedStrategyFactory()
