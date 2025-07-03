# src/modules/backend/solver/__init__.py
"""
Solver strategies subpackage.
This package contains the solver strategy implementations for the Wordle solver.
"""

from .modernized_strategy_factory import ModernizedStrategyFactory

# Import stateless strategy implementations directly
from .stateless_entropy_strategy import StatelessEntropyStrategy
from .stateless_frequency_strategy import StatelessFrequencyStrategy
from .stateless_hybrid_strategy import StatelessHybridStrategy
from .stateless_minimax_strategy import StatelessMinimaxStrategy
from .stateless_solver_strategy import StatelessSolverStrategy
from .stateless_two_step_strategy import StatelessTwoStepStrategy
from .stateless_weighted_gain_strategy import StatelessWeightedGainStrategy

# Re-export with simplified names for backward compatibility
EntropyStrategy = StatelessEntropyStrategy
FrequencyStrategy = StatelessFrequencyStrategy
HybridFrequencyEntropyStrategy = StatelessHybridStrategy
MinimaxStrategy = StatelessMinimaxStrategy
SolverStrategy = StatelessSolverStrategy
TwoStepStrategy = StatelessTwoStepStrategy
WeightedGainStrategy = StatelessWeightedGainStrategy
StrategyFactory = ModernizedStrategyFactory

__all__ = [
    # Stateless implementations
    "StatelessSolverStrategy",
    "StatelessFrequencyStrategy",
    "StatelessEntropyStrategy",
    "StatelessHybridStrategy",
    "StatelessMinimaxStrategy",
    "StatelessTwoStepStrategy",
    "StatelessWeightedGainStrategy",
    "ModernizedStrategyFactory",
    # Legacy aliases
    "SolverStrategy",
    "FrequencyStrategy",
    "EntropyStrategy",
    "HybridFrequencyEntropyStrategy",
    "MinimaxStrategy",
    "TwoStepStrategy",
    "WeightedGainStrategy",
    "StrategyFactory",
]
