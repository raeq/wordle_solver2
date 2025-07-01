"""
Dependency injection container for the Wordle Solver application.
"""

from typing import Any, Callable, Dict, Optional, Type, TypeVar

from src.frontend.cli import CLIInterface
from src.modules.backend.game_engine import GameEngine
from src.modules.backend.game_state_manager import GameStateManager
from src.modules.backend.stats_manager import StatsManager
from src.modules.backend.word_manager import WordManager

T = TypeVar("T")


class DIContainer:
    """Simple dependency injection container."""

    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}

    def register_singleton(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a singleton factory."""
        self._factories[interface.__name__] = factory

    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory that creates new instances each time."""
        self._instances[interface.__name__] = factory

    def get(self, interface: Type[T]) -> T:
        """Get an instance of the requested type."""
        name = interface.__name__

        # Check if it's a singleton
        if name in self._singletons:
            return self._singletons[name]  # type: ignore

        # Check if we have a factory for singletons
        if name in self._factories:
            instance = self._factories[name]()
            self._singletons[name] = instance
            return instance  # type: ignore

        # Check if we have a regular factory
        if name in self._instances:
            return self._instances[name]()  # type: ignore

        raise ValueError(f"No factory registered for {name}")

    def reset_singletons(self) -> None:
        """Reset all singleton instances (useful for testing)."""
        self._singletons.clear()


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = _create_default_container()
    return _container


def _create_default_container() -> DIContainer:
    """Create and configure the default dependency injection container."""
    container = DIContainer()

    # Register singletons with direct constructor calls instead of lambdas
    container.register_singleton(WordManager, WordManager)
    container.register_singleton(StatsManager, StatsManager)
    container.register_singleton(CLIInterface, CLIInterface)

    # Register factories that depend on singletons
    def create_game_state_manager():
        return GameStateManager(container.get(WordManager))

    def create_game_engine():
        return GameEngine(container.get(WordManager))

    container.register_factory(GameStateManager, create_game_state_manager)
    container.register_factory(GameEngine, create_game_engine)

    return container


def configure_container_for_testing() -> DIContainer:
    """Configure a container specifically for testing with mocks."""
    container = DIContainer()
    # This will be used in tests to inject mocks
    return container


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    global _container
    _container = None
