"""
Caching utilities for performance optimization in the Wordle Solver.
"""

import threading
import time
from collections.abc import Hashable
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, Optional, TypeVar

from src.modules.backend.result_color import (  # Move import to top level to fix pylint warning
    ResultColor,
)

T = TypeVar("T")


class TTLCache:
    """Time-to-live cache implementation."""

    def __init__(self, max_size: int = 128, ttl_seconds: float = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[Hashable, tuple] = {}
        self._lock = threading.RLock()

    def get(self, key: Hashable) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    return value
                del self._cache[key]
            return None

    def set(self, key: Hashable, value: Any) -> None:
        """Set value in cache with current timestamp."""
        with self._lock:
            # Remove oldest entries if cache is full
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]

            self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Get the current size of the cache (public method)."""
        with self._lock:
            return len(self._cache)


# Global caches for different types of data
_word_frequency_cache = TTLCache(max_size=1000, ttl_seconds=3600)  # 1 hour
_strategy_result_cache = TTLCache(max_size=500, ttl_seconds=300)  # 5 minutes
_pattern_calculation_cache = TTLCache(max_size=2000, ttl_seconds=1800)  # 30 minutes


def cache_word_frequency(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to cache word frequency calculations."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # Create cache key from function arguments
        cache_key = (func.__name__, args, tuple(sorted(kwargs.items())))

        # Try to get from cache
        result = _word_frequency_cache.get(cache_key)
        if result is not None:
            return result  # type: ignore

        # Calculate and cache result
        result = func(*args, **kwargs)
        _word_frequency_cache.set(cache_key, result)
        return result

    return wrapper


def cache_strategy_results(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to cache strategy calculation results."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # Create cache key from function arguments
        cache_key = (func.__name__, args, tuple(sorted(kwargs.items())))

        # Try to get from cache
        result = _strategy_result_cache.get(cache_key)
        if result is not None:
            return result  # type: ignore

        # Calculate and cache result
        result = func(*args, **kwargs)
        _strategy_result_cache.set(cache_key, result)
        return result

    return wrapper


def cache_pattern_calculation(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to cache pattern calculation results."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # Create cache key from function arguments
        cache_key = (func.__name__, args, tuple(sorted(kwargs.items())))

        # Try to get from cache
        result = _pattern_calculation_cache.get(cache_key)
        if result is not None:
            return result  # type: ignore

        # Calculate and cache result
        result = func(*args, **kwargs)
        _pattern_calculation_cache.set(cache_key, result)
        return result

    return wrapper


@lru_cache(maxsize=1000)
def cached_word_pattern(guess: str, target: str) -> str:
    """
    Cached version of word pattern calculation.
    This is the most frequently called function in strategy calculations.
    """

    result = [""] * 5
    target_letters: list[str | None] = list(target)
    guess_letters: list[str | None] = list(guess)

    # First pass: mark exact matches (GREEN)
    for i in range(5):
        if guess_letters[i] == target_letters[i]:
            result[i] = ResultColor.GREEN.value
            target_letters[i] = None  # Mark as used
            guess_letters[i] = None  # Mark as processed

    # Second pass: mark partial matches (YELLOW)
    for i in range(5):
        if guess_letters[i] is not None:  # Not already processed
            if guess_letters[i] in target_letters:
                result[i] = ResultColor.YELLOW.value
                # Remove one occurrence from target
                target_letters[target_letters.index(guess_letters[i])] = None
            else:
                result[i] = ResultColor.BLACK.value

    return "".join(result)


def clear_all_caches() -> None:
    """Clear all performance caches."""
    _word_frequency_cache.clear()
    _strategy_result_cache.clear()
    _pattern_calculation_cache.clear()
    cached_word_pattern.cache_clear()


def get_cache_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics about cache usage."""
    return {
        "word_frequency_cache": {
            "size": _word_frequency_cache.size(),
            "max_size": _word_frequency_cache.max_size,
            "ttl_seconds": _word_frequency_cache.ttl_seconds,
        },
        "strategy_result_cache": {
            "size": _strategy_result_cache.size(),
            "max_size": _strategy_result_cache.max_size,
            "ttl_seconds": _strategy_result_cache.ttl_seconds,
        },
        "pattern_calculation_cache": {
            "size": _pattern_calculation_cache.size(),
            "max_size": _pattern_calculation_cache.max_size,
            "ttl_seconds": _pattern_calculation_cache.ttl_seconds,
        },
        "cached_word_pattern": {
            "cache_info": cached_word_pattern.cache_info()._asdict()
        },  # pylint: disable=no-value-for-parameter
    }
