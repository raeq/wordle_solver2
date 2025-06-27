# src/modules/backend/solver/enhanced_strategy_factory.py
"""
Enhanced strategy factory with dynamic registration, validation, and composition support.
"""
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from .solver_strategy import SolverStrategy


class StrategyValidator:
    """Validates strategy implementations."""

    @staticmethod
    def validate_strategy_class(strategy_class: Type[SolverStrategy]) -> List[str]:
        """
        Validate that a strategy class meets requirements.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check if it's a subclass of SolverStrategy
        if not issubclass(strategy_class, SolverStrategy):
            errors.append(f"{strategy_class.__name__} must inherit from SolverStrategy")

        # Check if it implements required methods
        required_methods = ["get_top_suggestions"]
        for method_name in required_methods:
            if not hasattr(strategy_class, method_name):
                errors.append(
                    f"{strategy_class.__name__} missing required method: {method_name}"
                )
            else:
                method = getattr(strategy_class, method_name)
                if not callable(method):
                    errors.append(
                        f"{strategy_class.__name__}.{method_name} is not callable"
                    )

        # Check method signature
        if hasattr(strategy_class, "get_top_suggestions"):
            try:
                sig = inspect.signature(strategy_class.get_top_suggestions)
                expected_params = [
                    "self",
                    "possible_words",
                    "common_words",
                    "guesses_so_far",
                ]
                actual_params = list(sig.parameters.keys())

                for param in expected_params:
                    if param not in actual_params:
                        errors.append(
                            f"{strategy_class.__name__}.get_top_suggestions missing parameter: {param}"
                        )
            except (TypeError, ValueError) as e:
                errors.append(
                    f"Could not inspect {strategy_class.__name__}.get_top_suggestions signature: {e}"
                )

        return errors

    @staticmethod
    def validate_strategy_instance(strategy: SolverStrategy) -> List[str]:
        """
        Validate that a strategy instance works correctly.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            # Test with minimal valid inputs
            result = strategy.get_top_suggestions(
                possible_words=["HELLO", "WORLD"],
                common_words=["HELLO"],
                guesses_so_far=[],
                count=1,
            )

            if not isinstance(result, list):
                errors.append(
                    f"get_top_suggestions must return a list, got {type(result)}"
                )

            if len(result) > 2:  # Should not return more than possible words
                errors.append(
                    f"get_top_suggestions returned too many results: {len(result)}"
                )

        except (TypeError, AttributeError, ValueError) as e:
            errors.append(f"Strategy failed basic functionality test: {e}")

        return errors


class StrategyComposer:
    """Supports composition and chaining of strategies."""

    @staticmethod
    def create_fallback_strategy(
        primary: SolverStrategy,
        fallback: SolverStrategy,
        fallback_condition: Optional[
            Callable[[List[str], List[str], List], bool]
        ] = None,
    ) -> "FallbackStrategy":
        """
        Create a strategy that falls back to another strategy under certain conditions.

        Args:
            primary: Primary strategy to use
            fallback: Fallback strategy to use when condition is met
            fallback_condition: Function that takes (possible_words, common_words, guesses_so_far)
                               and returns True if fallback should be used
        """
        if fallback_condition is None:
            # Default: use fallback when few words remain
            def default_fallback_condition(
                possible_words, common_words, guesses_so_far
            ):
                # Only use possible_words count for the default condition
                # Other parameters are accepted for API consistency but not used
                _ = common_words  # Mark as intentionally unused
                _ = guesses_so_far  # Mark as intentionally unused
                return len(possible_words) <= 3

            fallback_condition = default_fallback_condition

        return FallbackStrategy(primary, fallback, fallback_condition)

    @staticmethod
    def create_weighted_ensemble(
        strategies: List[Tuple[SolverStrategy, float]],
    ) -> "WeightedEnsembleStrategy":
        """
        Create a strategy that combines multiple strategies with weights.

        Args:
            strategies: List of (strategy, weight) tuples
        """
        return WeightedEnsembleStrategy(strategies)

    @staticmethod
    def create_sequential_strategy(
        strategies: List[SolverStrategy],
        switch_conditions: Optional[List[Callable]] = None,
    ) -> "SequentialStrategy":
        """
        Create a strategy that switches between strategies based on game state.

        Args:
            strategies: List of strategies to use
            switch_conditions: List of condition functions for when to switch
        """
        return SequentialStrategy(strategies, switch_conditions)


class FallbackStrategy(SolverStrategy):
    """Strategy that falls back to another strategy under certain conditions."""

    def __init__(
        self,
        primary: SolverStrategy,
        fallback: SolverStrategy,
        condition: Callable[[List[str], List[str], List], bool],
    ):
        self.primary = primary
        self.fallback = fallback
        self.condition = condition

    def get_top_suggestions(
        self, possible_words, common_words, guesses_so_far, count=10, word_manager=None
    ):
        if self.condition(possible_words, common_words, guesses_so_far):
            return self.fallback.get_top_suggestions(
                possible_words, common_words, guesses_so_far, count, word_manager
            )
        return self.primary.get_top_suggestions(
            possible_words, common_words, guesses_so_far, count, word_manager
        )


class WeightedEnsembleStrategy(SolverStrategy):
    """Strategy that combines multiple strategies with weights."""

    def __init__(self, strategies: List[Tuple[SolverStrategy, float]]):
        self.strategies = strategies
        # Normalize weights
        total_weight = sum(weight for _, weight in strategies)
        self.strategies = [
            (strategy, weight / total_weight) for strategy, weight in strategies
        ]

    def get_top_suggestions(
        self, possible_words, common_words, guesses_so_far, count=10, word_manager=None
    ):
        if not self.strategies:
            return []

        # Get suggestions from all strategies
        all_suggestions: Dict[str, float] = {}
        for strategy, weight in self.strategies:
            suggestions = strategy.get_top_suggestions(
                possible_words, common_words, guesses_so_far, count * 2, word_manager
            )

            # Weight the suggestions
            for i, word in enumerate(suggestions):
                # Score decreases with position, weighted by strategy weight
                score = weight * (len(suggestions) - i) / len(suggestions)
                all_suggestions[word] = all_suggestions.get(word, 0) + score

        # Sort by combined score and return top count
        sorted_words = sorted(all_suggestions.items(), key=lambda x: x[1], reverse=True)
        return [word for word, score in sorted_words[:count]]


class SequentialStrategy(SolverStrategy):
    """Strategy that switches between strategies based on game state."""

    def __init__(
        self,
        strategies: List[SolverStrategy],
        switch_conditions: Optional[List[Callable]] = None,
    ):
        self.strategies = strategies

        if switch_conditions is None:
            # Default conditions based on number of possible words
            switch_conditions = [
                lambda pw, cw, gs: len(pw) > 100,  # Use first strategy when many words
                lambda pw, cw, gs: 10
                < len(pw)
                <= 100,  # Use second strategy for medium
                lambda pw, cw, gs: len(pw) <= 10,  # Use last strategy for few words
            ]

        self.switch_conditions = switch_conditions

    def get_top_suggestions(
        self, possible_words, common_words, guesses_so_far, count=10, word_manager=None
    ):
        # Find the first strategy whose condition is met
        for i, condition in enumerate(self.switch_conditions):
            if i < len(self.strategies) and condition(
                possible_words, common_words, guesses_so_far
            ):
                return self.strategies[i].get_top_suggestions(
                    possible_words, common_words, guesses_so_far, count, word_manager
                )

        # Fallback to last strategy if no condition is met
        if self.strategies:
            return self.strategies[-1].get_top_suggestions(
                possible_words, common_words, guesses_so_far, count, word_manager
            )

        return []


class EnhancedStrategyFactory:
    """Enhanced factory with dynamic registration, validation, and composition."""

    def __init__(self):
        self._strategies: Dict[str, Type[SolverStrategy]] = {}
        self._strategy_metadata: Dict[str, Dict[str, Any]] = {}
        self._validators = [StrategyValidator.validate_strategy_class]
        self._instance_validators = [StrategyValidator.validate_strategy_instance]

    def register_strategy(
        self,
        name: str,
        strategy_class: Type[SolverStrategy],
        metadata: Optional[Dict[str, Any]] = None,
        validate: bool = True,
    ) -> None:
        """
        Register a new strategy type with optional validation.

        Args:
            name: Name for the strategy
            strategy_class: Class to instantiate for this strategy
            metadata: Optional metadata about the strategy
            validate: Whether to validate the strategy before registration
        """
        name = name.lower()

        if validate:
            errors = []
            for validator in self._validators:
                errors.extend(validator(strategy_class))

            if errors:
                raise ValueError(
                    f"Strategy validation failed for {name}: {'; '.join(errors)}"
                )

        self._strategies[name] = strategy_class
        self._strategy_metadata[name] = metadata or {}

    def unregister_strategy(self, name: str) -> None:
        """Remove a strategy from the registry."""
        name = name.lower()
        self._strategies.pop(name, None)
        self._strategy_metadata.pop(name, None)

    def create_strategy(
        self, strategy_name: str, validate_instance: bool = False, **kwargs
    ) -> SolverStrategy:
        """
        Create a strategy instance with optional validation.

        Args:
            strategy_name: Name of the strategy to create
            validate_instance: Whether to validate the created instance
            **kwargs: Additional arguments to pass to strategy constructor

        Returns:
            An instance of the requested strategy
        """
        strategy_name = strategy_name.lower()

        if strategy_name not in self._strategies:
            available = ", ".join(self._strategies.keys())
            raise ValueError(
                f"Unknown strategy '{strategy_name}'. Available: {available}"
            )

        strategy_class = self._strategies[strategy_name]

        try:
            # Try to create instance with provided kwargs
            strategy = strategy_class(**kwargs)
        except TypeError as e:
            # If kwargs don't match, try without them
            try:
                strategy = strategy_class()
            except Exception as creation_error:
                raise ValueError(
                    f"Failed to create strategy {strategy_name}: {creation_error}"
                ) from e

        if validate_instance:
            errors = []
            for validator in self._instance_validators:
                errors.extend(validator(strategy))

            if errors:
                raise ValueError(
                    f"Strategy instance validation failed: {'; '.join(errors)}"
                )

        return strategy

    def get_available_strategies(self) -> List[str]:
        """Get a list of available strategy names."""
        return list(self._strategies.keys())

    def get_strategy_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a strategy."""
        return self._strategy_metadata.get(name.lower(), {})

    def create_fallback_strategy(
        self,
        primary_name: str,
        fallback_name: str,
        fallback_condition: Optional[Callable] = None,
        **kwargs,
    ) -> SolverStrategy:
        """Create a fallback strategy composition."""
        primary = self.create_strategy(primary_name, **kwargs)
        fallback = self.create_strategy(fallback_name, **kwargs)
        return StrategyComposer.create_fallback_strategy(
            primary, fallback, fallback_condition
        )

    def create_weighted_ensemble(
        self, strategy_weights: List[Tuple[str, float]], **kwargs
    ) -> SolverStrategy:
        """Create a weighted ensemble of strategies."""
        strategies = [
            (self.create_strategy(name, **kwargs), weight)
            for name, weight in strategy_weights
        ]
        return StrategyComposer.create_weighted_ensemble(strategies)

    def create_sequential_strategy(
        self,
        strategy_names: List[str],
        switch_conditions: Optional[List[Callable]] = None,
        **kwargs,
    ) -> SolverStrategy:
        """Create a sequential strategy that switches based on conditions."""
        strategies = [self.create_strategy(name, **kwargs) for name in strategy_names]
        return StrategyComposer.create_sequential_strategy(
            strategies, switch_conditions
        )

    def add_validator(self, validator: Callable[..., List[str]]) -> None:
        """Add a custom strategy class validator."""
        self._validators.append(validator)

    def add_instance_validator(self, validator: Callable[..., List[str]]) -> None:
        """Add a custom strategy instance validator."""
        self._instance_validators.append(validator)


# Create global enhanced factory instance
enhanced_factory = EnhancedStrategyFactory()
