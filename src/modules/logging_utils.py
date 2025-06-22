"""
Structured logging utilities for the Wordle Solver application.
"""

import functools
import inspect
import json
import logging
import logging.config
import os
import time
from datetime import datetime
from typing import Any, Callable, TypeVar, cast

import yaml

# Type variables for better type hinting
F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")


# Configure logging
def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up structured logging configuration from YAML file.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    os_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(os_path, "..", "..")
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure log file path with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(logs_dir, f"wordle_solver_{timestamp}.log")

    # Set numeric log level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    # Load logging configuration from YAML file
    config_file = os.path.join(os_path, "..", "logging_config.yaml")

    if os.path.exists(config_file):
        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Set the dynamic log file path in the config
        if "handlers" in config and "file_handler" in config["handlers"]:
            config["handlers"]["file_handler"]["filename"] = log_file

        # Override the root logger level if specified
        if "root" in config:
            config["root"]["level"] = log_level.upper()

        # Apply configuration
        logging.config.dictConfig(config)
        logging.info(f"Logging configured from {config_file}")
    else:
        # Fallback to basic configuration if YAML file is not found
        logging.basicConfig(
            level=numeric_level,
            format="%(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        logging.warning(f"Logging config file not found at {config_file}, using basic configuration")


# Structured logging decorator
def log_method(level: str = "DEBUG") -> Callable[[F], F]:
    """
    Decorator for structured logging of method calls.

    Args:
        level: The logging level to use (DEBUG, INFO, etc.)

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log_level = getattr(logging, level.upper(), None)
            if not isinstance(log_level, int):
                log_level = logging.DEBUG

            # Extract method information
            module_name = func.__module__
            class_name = args[0].__class__.__name__ if args else None
            func_name = func.__name__

            # Prepare parameter info for logging
            params = {}
            if args and len(args) > 1:  # Skip 'self' parameter
                # Get parameter names from function signature
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())

                # Map positional args to their parameter names (excluding 'self')
                for i, arg in enumerate(args[1:], 1):
                    if i < len(param_names):
                        params[param_names[i]] = repr(arg)
                    else:
                        params[f"arg{i}"] = repr(arg)

            # Add keyword arguments
            params.update({k: repr(v) for k, v in kwargs.items()})

            # Create structured log entry
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "module": module_name,
                "class": class_name,
                "method": func_name,
                "params": params,
            }

            # Log at the specified level
            logging.log(log_level, json.dumps(log_entry))

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # Log exceptions
                error_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "ERROR",
                    "module": module_name,
                    "class": class_name,
                    "method": func_name,
                    "exception": str(e),
                    "exception_type": type(e).__name__,
                }
                logging.error(json.dumps(error_entry))
                raise
            finally:
                # Log execution time for performance monitoring
                execution_time = time.time() - start_time
                if level == "DEBUG":
                    perf_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "level": "DEBUG",
                        "module": module_name,
                        "class": class_name,
                        "method": func_name,
                        "execution_time_ms": round(execution_time * 1000, 2),
                    }
                    logging.debug(json.dumps(perf_entry))

        return cast(F, wrapper)

    return decorator


# Special decorator for logging game outcomes
def log_game_outcome(func: F) -> F:
    """
    Special decorator for logging game outcomes at INFO level.

    Args:
        func: The function to decorate

    Returns:
        Decorated function
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)

        # Extract game result information based on the method name and parameters
        class_name = args[0].__class__.__name__ if args else None
        method_name = func.__name__

        # For specific outcome methods, log more detailed information
        if method_name == "_display_solver_result" or method_name == "display_game_over":
            won = args[1] if len(args) > 1 else kwargs.get("won", None)
            attempt = args[2] if len(args) > 2 else kwargs.get("attempt", None)
            max_attempts = args[3] if len(args) > 3 else kwargs.get("max_attempts", None)

            # Create structured log entry for game outcome
            outcome_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "class": class_name,
                "event": "game_outcome",
                "won": won,
                "attempts": attempt,
                "max_attempts": max_attempts,
            }

            # Add target word for game mode if available (position may vary)
            if method_name == "display_game_over" and len(args) > 2:
                outcome_entry["target_word"] = args[2]

            logging.info(json.dumps(outcome_entry))

        return result

    return cast(F, wrapper)


# Initialize logging when the module is imported
setup_logging()
