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
from typing import (
    Any,
    Callable,
    Generator,
    Mapping,
    MutableMapping,
    Optional,
    TypeVar,
    Union,
    cast,
)

import structlog
import yaml
from structlog.stdlib import BoundLogger

# Import constants for magic number replacement
from .backend.solver.constants import (
    FIFTH_ARRAY_INDEX,
    FIRST_ARRAY_INDEX,
    FOURTH_ARRAY_INDEX,
    MILLISECONDS_CONVERSION_FACTOR,
    ROUND_PRECISION_DIGITS,
    SECOND_ARRAY_INDEX,
    SKIP_SELF_PARAMETER_INDEX,
    THIRD_ARRAY_INDEX,
)

# Type variables for better type hinting
F = TypeVar("F", bound=Callable[..., Any])

# Global logger instance
logger: Optional[BoundLogger] = None

# Context variable to store the current game ID
_game_id_context: ContextVar[Optional[str]] = ContextVar("game_id", default=None)


def add_game_id_processor(
    _logger: Any, _method_name: str, event_dict: MutableMapping[str, Any]
) -> Union[Mapping[str, Any], str, bytes, bytearray, tuple[Any, ...]]:
    """
    Processor that adds the game ID to the event dictionary if one is set in the context.

    Args:
        _logger: Logger instance (unused but required by structlog interface)
        _method_name: Method name (unused but required by structlog interface)
        event_dict: Event dictionary to modify
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
    # Use module-level logger instead of global statement
    import src.modules.logging_utils as logging_module

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
        with open(config_file, encoding="utf-8") as f:
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
        wrapper_class=BoundLogger,  # FIX: Use BoundLogger, not BindableLogger
        cache_logger_on_first_use=True,
    )

    # Set the module-level logger
    logging_module.logger = structlog.get_logger("wordle_solver")
    if logging_module.logger is not None:
        logging_module.logger.info(
            "Logging initialized",
            log_level=log_level,
            log_file=log_file,
            rotation="daily",
        )


def _extract_log_data(func: Callable, args: Any, kwargs: Any, level: str) -> dict:
    """
    Extracts and prepares log data from the function, its arguments, and the logging level.

    Args:
        func: The function being logged
        args: The positional arguments passed to the function
        kwargs: The keyword arguments passed to the function
        level: The logging level as a string (e.g., "DEBUG", "INFO")

    Returns:
        A dictionary containing the extracted log data
    """
    module_name = func.__module__
    class_name = args[FIRST_ARRAY_INDEX].__class__.__name__ if args else None
    func_name = func.__name__
    log_data = {
        "module": module_name,
        "class": class_name,
        "method": func_name,
    }
    if level.upper() == "DEBUG":
        params = {}
        if args and len(args) > SKIP_SELF_PARAMETER_INDEX:  # Skip 'self' parameter
            # Get parameter names from function signature
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            # Map positional args to their parameter names (excluding 'self')
            for i, arg in enumerate(
                args[SKIP_SELF_PARAMETER_INDEX:], SKIP_SELF_PARAMETER_INDEX
            ):
                if i < len(param_names):
                    params[param_names[i]] = repr(arg)
                else:
                    params[f"arg{i}"] = repr(arg)

        # Add keyword arguments
        params.update({k: repr(v) for k, v in kwargs.items()})
        log_data["params"] = params
    return log_data


def _log_exception(_logger_instance, exc, log_data):
    """
    Logs the exception information using the provided logger.

    Args:
        _logger_instance: The logger instance (renamed to avoid outer scope conflict)
        exc: The exception instance
        log_data: The log data dictionary containing contextual information
    """
    if _logger_instance is not None:
        _logger_instance.exception(
            "Exception in method",
            **log_data,
            error=str(exc),
            error_type=type(exc).__name__,
        )


def _log_performance(_logger_instance, log_data, execution_time, level):
    """
    Logs the performance metrics of the method execution.

    Args:
        _logger_instance: The logger instance (renamed to avoid outer scope conflict)
        log_data: The log data dictionary containing contextual information
        execution_time: The execution time of the method in milliseconds
        level: The logging level as a string (e.g., "DEBUG", "INFO")
    """
    if level.upper() == "DEBUG" and _logger_instance is not None:
        _logger_instance.debug(
            "Method execution completed",
            **log_data,
            execution_time_ms=round(execution_time, ROUND_PRECISION_DIGITS),
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
            # Get current logger or initialize if needed
            current_logger = logger
            if current_logger is None:
                setup_logging()
                current_logger = logger

            # Skip performance logging for utility functions to avoid overhead
            skip_performance_logging = func.__name__ in [
                "calculate_pattern",
                "is_valid_result_string",
                "_matches_green_positions",
                "_matches_yellow_positions",
                "_matches_black_positions",
                "_calculate_entropy_score",
                "_calculate_frequency_score",
                "_calculate_minimax_score",
                "calculate_letter_frequencies",
            ]

            # Extract method information and log data only if needed
            log_data = None
            if not skip_performance_logging:
                log_data = _extract_log_data(func, args, kwargs, level)

                # Log method entry at the specified log level
                if current_logger is not None and level.upper() == "DEBUG":
                    getattr(current_logger, level.lower())("Method call", **log_data)

            start_time = time.time() if not skip_performance_logging else None
            try:
                # Call the actual method
                result = func(*args, **kwargs)
                return result
            except Exception as exc:
                # Log exception details (always log exceptions)
                if log_data is None:
                    log_data = _extract_log_data(func, args, kwargs, level)
                _log_exception(current_logger, exc, log_data)
                raise
            finally:
                # Calculate and log performance metrics only for non-utility functions
                if (
                    not skip_performance_logging
                    and start_time is not None
                    and log_data is not None
                ):
                    execution_time = (
                        time.time() - start_time
                    ) * MILLISECONDS_CONVERSION_FACTOR  # ms
                    _log_performance(current_logger, log_data, execution_time, level)

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
        # Get current logger or initialize if needed
        current_logger = logger
        if current_logger is None:
            setup_logging()
            current_logger = logger

        result = func(*args, **kwargs)

        # Extract game result information
        class_name = args[FIRST_ARRAY_INDEX].__class__.__name__ if args else None
        method_name = func.__name__

        # For specific outcome methods, log more detailed information
        if method_name in (
            "_display_solver_result",
            "_display_game_result",
            "display_game_over",
        ):
            won = (
                args[SECOND_ARRAY_INDEX]
                if len(args) > SECOND_ARRAY_INDEX
                else kwargs.get("won", None)
            )

            # Different parameter order depending on the method
            if method_name == "_display_solver_result":
                attempt = (
                    args[THIRD_ARRAY_INDEX]
                    if len(args) > THIRD_ARRAY_INDEX
                    else kwargs.get("attempt", None)
                )
                max_attempts = (
                    args[FOURTH_ARRAY_INDEX]
                    if len(args) > FOURTH_ARRAY_INDEX
                    else kwargs.get("max_attempts", None)
                )
                target_word = (
                    args[THIRD_ARRAY_INDEX]
                    if len(args) > THIRD_ARRAY_INDEX
                    else kwargs.get("target_word", None)
                )
                attempt = (
                    args[FOURTH_ARRAY_INDEX]
                    if len(args) > FOURTH_ARRAY_INDEX
                    else kwargs.get("attempt", None)
                )
                max_attempts = (
                    args[FIFTH_ARRAY_INDEX]
                    if len(args) > FIFTH_ARRAY_INDEX
                    else kwargs.get("max_attempts", None)
                )

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
            if current_logger is not None:
                current_logger.info("Game outcome", **log_data)

        return result

    return cast(F, wrapper)
