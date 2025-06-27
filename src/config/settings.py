"""
Centralized configuration settings for the Wordle Solver application.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class GameConfig:
    """Game-related configuration."""

    max_attempts: int = 6
    word_length: int = 5
    default_strategy: str = "weighted_gain"


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    log_dir: str = "logs"
    log_file: str = "wordle_solver.log"
    backup_count: int = 30
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class UIConfig:
    """User interface configuration."""

    suggestions_count: int = 10
    enable_colors: bool = True
    enable_progress_bar: bool = True


@dataclass
class AppConfig:
    """Main application configuration."""

    game: GameConfig
    logging: LoggingConfig
    ui: UIConfig
    project_root: Path

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "AppConfig":
        """Load configuration from file or use defaults."""
        project_root = Path(__file__).parent.parent.parent

        # Default configuration
        game = GameConfig()
        logging = LoggingConfig()
        ui = UIConfig()

        # Load from file if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            # Update configurations with file data
            if "game" in config_data:
                game = GameConfig(**config_data["game"])
            if "logging" in config_data:
                logging = LoggingConfig(**config_data["logging"])
            if "ui" in config_data:
                ui = UIConfig(**config_data["ui"])

        return cls(game=game, logging=logging, ui=ui, project_root=project_root)

    @property
    def log_file_path(self) -> Path:
        """Get the full path to the log file."""
        return self.project_root / self.logging.log_dir / self.logging.log_file

    @property
    def words_file_path(self) -> Path:
        """Get the full path to the words file."""
        return self.project_root / "src" / "words.txt"


# Global configuration instance
config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global config
    if config is None:
        config = AppConfig.load()
    return config


def initialize_config(config_path: Optional[str] = None) -> AppConfig:
    """Initialize the global configuration."""
    global config
    config = AppConfig.load(config_path)
    return config
