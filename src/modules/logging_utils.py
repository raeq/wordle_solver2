"""
Structured logging utilities for the Wordle Solver application using structlog.
"""

import functools
import inspect
import logging
import logging.config
import os
import time
from datetime import datetime
from typing import Any, Callable, TypeVar, cast

import structlog
import yaml

# Type variables for better type hinting
F = TypeVar("F", bound=Callable[..., Any])

# Global logger instance, will be configured in setup_logging()
logger = None


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up structured logging configuration from YAML file.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global logger

    # Create logs directory if it doesn't exist
    os_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(os_path, "..", "..")
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure log file path with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(logs_dir, f"wordle_solver_{timestamp}.log")

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

        # Configure standard logging
        logging.config.dictConfig(config)

        # Configure structlog
        structlog.configure(
            processors=[
                # Add context from structlog to log entries
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                # Format the log message in a manner compatible with standard logging
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Create a logger for our application
        logger = structlog.get_logger("wordle_solver")
        logger.info("Logging configured from YAML", config_file=config_file)

    else:
        # Basic setup for structlog if YAML file is not found
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        logger = structlog.get_logger("wordle_solver")
        logger.warning("Config file not found, using basic configuration", config_file=config_file)


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
            global logger
            if logger is None:
                setup_logging()

            # Extract method information
            module_name = func.__module__
            class_name = args[0].__class__.__name__ if args else None
            func_name = func.__name__

            # Create bound logger with method context
            bound_logger = logger.bind(module=module_name, class_name=class_name, method=func_name)

            # Prepare parameter info for logging if debug
            if level.upper() == "DEBUG":
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

                # Log method call with parameters
                getattr(bound_logger, level.lower())("Method call", params=params)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as exc:
                # Log the exception
                bound_logger.exception("Exception in method", exc_info=exc)
                raise
            finally:
                # Log execution time for performance monitoring
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                if level.upper() == "DEBUG":
                    bound_logger.debug(
                        "Method execution completed",
                        execution_time_ms=round(execution_time, 2),
                    )

        return cast(F, wrapper)

    return decorator


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
        global logger
        if logger is None:
            setup_logging()

        result = func(*args, **kwargs)

        # Extract game result information
        class_name = args[0].__class__.__name__ if args else None
        method_name = func.__name__

        # For specific outcome methods, log more detailed information
        if method_name in ("_display_solver_result", "_display_game_result", "display_game_over"):
            won = args[1] if len(args) > 1 else kwargs.get("won", None)

            # Different parameter order depending on the method
            if method_name == "_display_solver_result":
                attempt = args[2] if len(args) > 2 else kwargs.get("attempt", None)
                max_attempts = args[3] if len(args) > 3 else kwargs.get("max_attempts", None)
                target_word = None
            else:
                target_word = args[2] if len(args) > 2 else kwargs.get("target_word", None)
                attempt = args[3] if len(args) > 3 else kwargs.get("attempt", None)
                max_attempts = args[4] if len(args) > 4 else kwargs.get("max_attempts", None)

            # Log game outcome with structlog
            event_data = {
                "class": class_name,
                "event": "game_outcome",
                "won": won,
                "attempts": attempt,
                "max_attempts": max_attempts,
            }

            # Add target word if available
            if target_word:
                event_data["target_word"] = target_word

            logger.info("Game outcome", **event_data)

        return result

    return cast(F, wrapper)


# Initialize logging when the module is imported
setup_logging()
