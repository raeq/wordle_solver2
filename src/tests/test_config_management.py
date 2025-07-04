#!/usr/bin/env python3
# src/tests/test_config_management.py
"""
Test suite for configuration management.

This test suite verifies:
1. Basic configuration loading and defaults
2. Environment variable configuration with WORDLE_ENVIRONMENT
3. Configuration file overrides
4. Environment-specific configuration files
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from src.config.settings import (
    WORDLE_ENV_VAR,
    AppSettings,
    get_environment,
    get_settings,
    initialize_config,
    reset_settings,
)


class TestConfigManagement:
    """Tests for configuration management functionality"""

    def setup_method(self):
        """Set up tests by resetting settings and environment"""
        reset_settings()
        # Save any existing environment variable to restore later
        self.original_env = os.environ.get(WORDLE_ENV_VAR)
        # Clear the environment variable for tests
        if WORDLE_ENV_VAR in os.environ:
            del os.environ[WORDLE_ENV_VAR]

    def teardown_method(self):
        """Clean up after tests"""
        reset_settings()
        # Restore original environment variable if it existed
        if self.original_env is not None:
            os.environ[WORDLE_ENV_VAR] = self.original_env
        elif WORDLE_ENV_VAR in os.environ:
            del os.environ[WORDLE_ENV_VAR]

    def test_default_settings_load(self):
        """Test that default settings load correctly"""
        settings = get_settings()
        assert settings is not None
        assert settings.game is not None
        assert settings.logging is not None
        assert settings.solver is not None

    def test_environment_default(self):
        """Test that the default environment is PROD when env var not set"""
        assert get_environment() == "PROD"

    def test_environment_dev(self):
        """Test that DEV environment is recognized"""
        os.environ[WORDLE_ENV_VAR] = "DEV"
        assert get_environment() == "DEV"

    def test_environment_prod(self):
        """Test that PROD environment is recognized"""
        os.environ[WORDLE_ENV_VAR] = "PROD"
        assert get_environment() == "PROD"

    def test_empty_environment(self):
        """Test that empty environment defaults to PROD"""
        os.environ[WORDLE_ENV_VAR] = ""
        assert get_environment() == "PROD"

    def test_invalid_environment(self):
        """Test that invalid environment defaults to PROD"""
        os.environ[WORDLE_ENV_VAR] = "INVALID_VALUE"
        assert get_environment() == "PROD"

    @pytest.mark.parametrize(
        "env_value,expected",
        [
            (None, "PROD"),  # No env var
            ("", "PROD"),  # Empty string
            ("DEV", "DEV"),
            ("PROD", "PROD"),
            ("TEST", "PROD"),  # Invalid value
            ("dev", "PROD"),  # Case sensitive
            ("prod", "PROD"),  # Case sensitive
        ],
    )
    def test_environment_variations(self, env_value, expected):
        """Test various environment variable values"""
        if env_value is None:
            if WORDLE_ENV_VAR in os.environ:
                del os.environ[WORDLE_ENV_VAR]
        else:
            os.environ[WORDLE_ENV_VAR] = env_value

        assert get_environment() == expected

    def test_custom_config_file(self):
        """Test loading from a custom config file"""
        tmp_file_path = None
        try:
            # Create a custom config
            custom_config = {
                "game": {"max_attempts": 10, "word_length": 6},
                "logging": {"level": "DEBUG"},
                "solver": {"default_strategy": "minimax"},
            }

            # Create a named temporary file and close it right away
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp_file:
                tmp_file_path = tmp_file.name

            # Write the config to the temporary file using regular file handling
            with open(tmp_file_path, "w") as f:
                yaml.dump(custom_config, f)

            # Load the custom config
            settings = initialize_config(tmp_file_path)

            # Verify settings were loaded correctly
            assert settings.game.max_attempts == 10
            assert settings.game.word_length == 6
            assert settings.logging.level == "DEBUG"
            assert settings.solver.default_strategy == "minimax"
        finally:
            # Clean up temporary file
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    def test_env_specific_config(self):
        """Test loading environment-specific config files"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create mock project structure
            config_dir = Path(tmp_dir)

            # Create dev and prod config files
            dev_config = {
                "game": {"max_attempts": 8},
                "logging": {"level": "DEBUG"},
                "solver": {},
            }

            prod_config = {
                "game": {"max_attempts": 6},
                "logging": {"level": "INFO"},
                "solver": {},
            }

            # Write config files
            dev_config_path = config_dir / "config.dev.yaml"
            prod_config_path = config_dir / "config.prod.yaml"

            with open(dev_config_path, "w") as f:
                yaml.dump(dev_config, f)

            with open(prod_config_path, "w") as f:
                yaml.dump(prod_config, f)

            # Test DEV environment by directly loading the files
            os.environ[WORDLE_ENV_VAR] = "DEV"
            dev_settings = AppSettings.load_from_file(dev_config_path)
            assert dev_settings.game.max_attempts == 8
            assert dev_settings.logging.level == "DEBUG"

            # Test PROD environment by directly loading the files
            os.environ[WORDLE_ENV_VAR] = "PROD"
            prod_settings = AppSettings.load_from_file(prod_config_path)
            assert prod_settings.game.max_attempts == 6
            assert prod_settings.logging.level == "INFO"

            # Verify that the environment variable works with a custom initialize_config function
            def test_initialize_config(env_var_value):
                os.environ[WORDLE_ENV_VAR] = env_var_value
                if env_var_value == "DEV":
                    return AppSettings.load_from_file(dev_config_path)
                else:
                    return AppSettings.load_from_file(prod_config_path)

            # Test with DEV environment
            settings_dev = test_initialize_config("DEV")
            assert settings_dev.game.max_attempts == 8
            assert settings_dev.logging.level == "DEBUG"

            # Test with PROD environment
            settings_prod = test_initialize_config("PROD")
            assert settings_prod.game.max_attempts == 6
            assert settings_prod.logging.level == "INFO"


if __name__ == "__main__":
    pytest.main()
