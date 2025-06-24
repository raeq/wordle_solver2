"""
Structured logging utilities for the Wordle Solver application using structlog.
"""

import contextlib
import functools
import inspect
import logging
import logging.config
import os
import sys
import time
from contextvars import ContextVar
from typing import Any, Callable, Dict, Generator, Optional, TypeVar, cast

import structlog
import yaml

# Type variables for better type hinting
F = TypeVar("F", bound=Callable[..., Any])

# Global logger instance
logger = None

# Context variable to store the current game ID
_game_id_context: ContextVar[Optional[str]] = ContextVar("game_id", default=None)


def add_game_id_processor(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processor that adds the game ID to the event dictionary if one is set in the context.
    """
    game_id = _game_id_context.get()
    if game_id:
        event_dict["game_id"] = game_id
    return event_dict


@contextlib.contextmanager
def game_id_context(game_id: Optional[str] = None) -> Generator[None, None, None]:
    """
    Context manager for setting the game ID for a block of code.

    Args:
        game_id: The game ID to set for logs within this context

    Example:
        with game_id_context("ABC123"):
            logger.info("This log will include the game ID")
    """
    if game_id:
        token = _game_id_context.set(game_id)
        try:
            yield
        finally:
            _game_id_context.reset(token)
    else:
        yield


def set_game_id(game_id: Optional[str] = None) -> None:
    """
    Set the game ID for the current context.

    Args:
        game_id: The game ID to set for subsequent log entries
    """
    if game_id:
        _game_id_context.set(game_id)
    else:
        # Reset to default (None) if no game ID provided
        _game_id_context.set(None)


def get_current_game_id() -> Optional[str]:
    """
    Get the current game ID from the context.

    Returns:
        The current game ID or None if not set
    """
    return _game_id_context.get()


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global logger

    # Create logs directory if it doesn't exist
    os_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(os_path, "..", "..")
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure base log file path (without timestamp - will use rotation instead)
    log_file = os.path.join(logs_dir, "wordle_solver.log")

    # Load logging configuration from YAML file
    config_file = os.path.join(os_path, "..", "logging_config.yaml")

    if os.path.exists(config_file):
        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Set the log file path for the rotating file handler
        if "handlers" in config and "rotating_file_handler" in config["handlers"]:
            config["handlers"]["rotating_file_handler"]["filename"] = log_file

        # Override the root logger level if specified
        if "root" in config:
            config["root"]["level"] = log_level.upper()

        # Configure standard logging
        logging.config.dictConfig(config)
    else:
        # Fall back to basic configuration
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            add_game_id_processor,  # Add our custom processor to include game ID
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger("wordle_solver")
    logger.info(
        "Logging initialized",
        log_level=log_level,
        log_file=log_file,
        rotation="daily",
    )


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

            # Create the structured log data
            log_data = {
                "module": module_name,
                "class": class_name,
                "method": func_name,
            }

            # Add parameters if debug level
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
                log_data["params"] = params

                # Log method call
                getattr(logger, level.lower())("Method call", **log_data)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as exc:
                # Log exception
                logger.exception(
                    "Exception in method",
                    module=module_name,
                    class_name=class_name,
                    method=func_name,
                    error=str(exc),
                    error_type=type(exc).__name__,
                )
                raise
            finally:
                # Log performance metrics
                execution_time = (time.time() - start_time) * 1000  # ms
                if level.upper() == "DEBUG":
                    logger.debug(
                        "Method execution completed",
                        module=module_name,
                        class_name=class_name,
                        method=func_name,
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

            # Create the structured log data (don't include 'event' as a key)
            log_data = {
                "class": class_name,
                "outcome_type": "game_outcome",
                "won": won,
                "attempts": attempt,
                "max_attempts": max_attempts,
            }

            # Add target word if available
            if target_word:
                log_data["target_word"] = target_word

            # Use "Game outcome" as the event parameter, and pass the rest as kwargs
            logger.info("Game outcome", **log_data)

        return result

    return cast(F, wrapper)


# Initialize logging when the module is imported
setup_logging()
