# src/modules/backend/solver/strategy_factory.py
"""
Factory for creating solver strategy instances.
"""
from typing import Dict, Type

from .entropy_strategy import EntropyStrategy
from .frequency_strategy import FrequencyStrategy
from .solver_strategy import SolverStrategy


class StrategyFactory:
    """Factory for creating solver strategies."""

    # Map of strategy names to their classes
    _strategies: Dict[str, Type[SolverStrategy]] = {
        "frequency": FrequencyStrategy,
        "entropy": EntropyStrategy,
    }

    @classmethod
    def create_strategy(cls, strategy_name: str) -> SolverStrategy:
        """
        Create a strategy based on name.

        Args:
            strategy_name: Name of the strategy to create

        Returns:
            An instance of the requested strategy

        Raises:
            ValueError: If the strategy name is not recognized
        """
        strategy_name = strategy_name.lower()

        if strategy_name not in cls._strategies:
            raise ValueError(
                f"Unknown strategy '{strategy_name}'. "
                f"Available strategies: {', '.join(cls._strategies.keys())}"
            )

        strategy_class = cls._strategies[strategy_name]
        return strategy_class()

    @classmethod
    def get_available_strategies(cls) -> list[str]:
        """Get a list of available strategy names."""
        return list(cls._strategies.keys())

    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[SolverStrategy]) -> None:
        """
        Register a new strategy type.

        Args:
            name: Name for the strategy
            strategy_class: Class to instantiate for this strategy
        """
        cls._strategies[name.lower()] = strategy_class
