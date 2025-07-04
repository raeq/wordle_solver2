"""
Configuration settings for the Wordle solver application.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ..modules.backend.solver.constants import (
    DEFAULT_BACKUP_COUNT,
    DEFAULT_ENCODING,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_SUGGESTIONS_COUNT,
    DEFAULT_WORD_LENGTH,
)

# Environment variable name
WORDLE_ENV_VAR = "WORDLE_ENVIRONMENT"


@dataclass
class GameSettings:
    """Settings for the Wordle game."""

    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    word_length: int = DEFAULT_WORD_LENGTH


@dataclass
class LoggingSettings:
    """Settings for logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_handler: bool = True
    console_handler: bool = True
    backup_count: int = DEFAULT_BACKUP_COUNT


@dataclass
class SolverSettings:
    """Settings for the solver strategies."""

    default_strategy: str = "entropy"
    suggestions_count: int = DEFAULT_SUGGESTIONS_COUNT
    enable_memory_optimization: bool = True
    enable_performance_profiling: bool = False


@dataclass
class AppSettings:
    """Main application settings."""

    game: GameSettings
    logging: LoggingSettings
    solver: SolverSettings

    def __init__(
        self,
        game: Optional[GameSettings] = None,
        logging: Optional[LoggingSettings] = None,
        solver: Optional[SolverSettings] = None,
    ):
        self.game = game or GameSettings()
        self.logging = logging or LoggingSettings()
        self.solver = solver or SolverSettings()

    @classmethod
    def load_from_file(cls, config_path: Path) -> "AppSettings":
        """Load settings from a YAML configuration file."""
        try:
            with open(config_path, encoding=DEFAULT_ENCODING) as f:
                data = yaml.safe_load(f)

            # Create settings instances from loaded data
            game_data = data.get("game", {})
            logging_data = data.get("logging", {})
            solver_data = data.get("solver", {})

            game_settings = GameSettings(**game_data)
            logging_settings = LoggingSettings(**logging_data)
            solver_settings = SolverSettings(**solver_data)

            return cls(
                game=game_settings, logging=logging_settings, solver=solver_settings
            )

        except FileNotFoundError:
            # Return default settings if file doesn't exist
            return cls()
        except (yaml.YAMLError, TypeError) as e:
            # Log error and return default settings
            print(f"Error loading configuration: {e}")
            return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary format."""
        return {
            "game": {
                "max_attempts": self.game.max_attempts,
                "word_length": self.game.word_length,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file_handler": self.logging.file_handler,
                "console_handler": self.logging.console_handler,
                "backup_count": self.logging.backup_count,
            },
            "solver": {
                "default_strategy": self.solver.default_strategy,
                "suggestions_count": self.solver.suggestions_count,
                "enable_memory_optimization": self.solver.enable_memory_optimization,
                "enable_performance_profiling": self.solver.enable_performance_profiling,
            },
        }


def get_environment() -> str:
    """
    Get the current environment setting from the WORDLE_ENVIRONMENT variable.

    If not set or empty, defaults to 'PROD'. Valid values are 'DEV' and 'PROD'.

    Returns:
        str: The current environment ('DEV' or 'PROD')
    """
    env = os.environ.get(WORDLE_ENV_VAR, "")
    if not env or env not in ["DEV", "PROD"]:
        return "PROD"
    return env


# Global settings instance
_app_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get the global application settings instance."""
    global _app_settings
    if _app_settings is None:
        # Try to load from config file in the project root
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        _app_settings = AppSettings.load_from_file(config_path)
    return _app_settings


def initialize_config(config_path: Optional[str] = None) -> AppSettings:
    """Initialize configuration from file or use defaults.

    Args:
        config_path: Optional path to configuration file

    Returns:
        AppSettings instance
    """
    # Check environment variable for configuration
    environment = get_environment()

    # Allow different config paths based on environment
    if not config_path:
        # Use default config path
        default_config_path = Path(__file__).parent.parent.parent / "config.yaml"

        # Check for environment-specific config file
        env_config_path = (
            Path(__file__).parent.parent.parent / f"config.{environment.lower()}.yaml"
        )
        if env_config_path.exists():
            default_config_path = env_config_path

        return AppSettings.load_from_file(default_config_path)
    else:
        return AppSettings.load_from_file(Path(config_path))


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _app_settings
    _app_settings = None
