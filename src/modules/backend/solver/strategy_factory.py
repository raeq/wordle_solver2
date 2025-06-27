# src/modules/backend/solver/strategy_factory.py
"""
Factory for creating solver strategy instances with enhanced features.
"""
from typing import Dict, Type

from .enhanced_strategy_factory import enhanced_factory

# Import all strategy classes at module level
from .entropy_strategy import EntropyStrategy
from .frequency_strategy import FrequencyStrategy
from .hybrid_frequency_entropy_strategy import HybridFrequencyEntropyStrategy
from .minimax_strategy import MinimaxStrategy
from .solver_strategy import SolverStrategy
from .two_step_strategy import TwoStepStrategy
from .weighted_gain_strategy import WeightedGainStrategy


class StrategyFactory:
    """Factory for creating solver strategies with backward compatibility."""

    # Map of strategy names to their classes
    _strategies: Dict[str, Type[SolverStrategy]] = {}

    @classmethod
    def _initialize_strategies(cls):
        """Initialize strategies using the enhanced factory."""
        if not cls._strategies:
            # Register strategies with enhanced factory
            enhanced_factory.register_strategy(
                "entropy",
                EntropyStrategy,
                metadata={
                    "description": "Information theory based strategy using Shannon entropy"
                },
            )
            enhanced_factory.register_strategy(
                "frequency",
                FrequencyStrategy,
                metadata={"description": "Corpus frequency based strategy"},
            )
            enhanced_factory.register_strategy(
                "hybrid",
                HybridFrequencyEntropyStrategy,
                metadata={
                    "description": "Hybrid strategy combining frequency and entropy"
                },
            )
            enhanced_factory.register_strategy(
                "minimax",
                MinimaxStrategy,
                metadata={
                    "description": "Minimax strategy for worst-case optimization"
                },
            )
            enhanced_factory.register_strategy(
                "two_step",
                TwoStepStrategy,
                metadata={"description": "Two-step lookahead strategy"},
            )
            enhanced_factory.register_strategy(
                "weighted_gain",
                WeightedGainStrategy,
                metadata={
                    "description": "Weighted combination of multiple information metrics"
                },
            )

            # Update local registry for backward compatibility
            cls._strategies = {
                name: enhanced_factory._strategies[name]
                for name in enhanced_factory.get_available_strategies()
            }

    @classmethod
    def create_strategy(cls, strategy_name: str) -> SolverStrategy:
        """
        Create a strategy based on name using enhanced factory.

        Args:
            strategy_name: Name of the strategy to create

        Returns:
            An instance of the requested strategy

        Raises:
            ValueError: If the strategy name is not recognized
        """
        cls._initialize_strategies()
        return enhanced_factory.create_strategy(strategy_name, validate_instance=True)

    @classmethod
    def get_available_strategies(cls) -> list[str]:
        """Get a list of available strategy names."""
        cls._initialize_strategies()
        return enhanced_factory.get_available_strategies()

    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[SolverStrategy]) -> None:
        """
        Register a new strategy type using enhanced factory.

        Args:
            name: Name for the strategy
            strategy_class: Class to instantiate for this strategy
        """
        enhanced_factory.register_strategy(name, strategy_class, validate=True)
        cls._strategies[name.lower()] = strategy_class

    @classmethod
    def create_fallback_strategy(
        cls, primary_name: str, fallback_name: str, fallback_condition=None
    ) -> SolverStrategy:
        """Create a fallback strategy composition."""
        cls._initialize_strategies()
        return enhanced_factory.create_fallback_strategy(
            primary_name, fallback_name, fallback_condition
        )

    @classmethod
    def create_weighted_ensemble(cls, strategy_weights: list) -> SolverStrategy:
        """Create a weighted ensemble of strategies."""
        cls._initialize_strategies()
        return enhanced_factory.create_weighted_ensemble(strategy_weights)

    @classmethod
    def create_sequential_strategy(
        cls, strategy_names: list, switch_conditions=None
    ) -> SolverStrategy:
        """Create a sequential strategy that switches based on conditions."""
        cls._initialize_strategies()
        return enhanced_factory.create_sequential_strategy(
            strategy_names, switch_conditions
        )
