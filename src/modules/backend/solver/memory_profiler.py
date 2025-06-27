# src/modules/backend/solver/memory_profiler.py
"""
Memory profiling utilities for monitoring memory usage in computation-heavy methods.
"""
import functools
import gc
import os
import time
from typing import Any, Callable, Dict, Optional

import psutil


class MemoryProfiler:
    """Utility class for profiling memory usage."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.profile_data: Dict[str, Dict[str, Any]] = {}

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage in MB."""
        memory_info = self.process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
            "vms": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
        }

    def profile_method(self, method_name: Optional[str] = None):
        """Decorator to profile memory usage of a method."""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = method_name or f"{func.__module__}.{func.__name__}"
                return self._execute_with_profiling(func, name, *args, **kwargs)

            return wrapper

        return decorator

    def _execute_with_profiling(self, func: Callable, name: str, *args, **kwargs):
        """Execute function with memory profiling."""
        # Force garbage collection before measurement
        gc.collect()

        # Get initial memory usage
        start_memory = self.get_memory_usage()
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            self._record_successful_execution(name, start_memory, start_time)
            return result
        except Exception as e:
            self._record_failed_execution(name, start_memory, start_time)
            raise e

    def _record_successful_execution(
        self, name: str, start_memory: Dict[str, float], start_time: float
    ):
        """Record data for successful execution."""
        end_memory = self.get_memory_usage()
        end_time = time.time()

        memory_delta = {
            "rss": end_memory["rss"] - start_memory["rss"],
            "vms": end_memory["vms"] - start_memory["vms"],
        }

        self._update_profile_data(name, end_time - start_time, memory_delta, end_memory)

    def _record_failed_execution(
        self, name: str, start_memory: Dict[str, float], start_time: float
    ):
        """Record data for failed execution."""
        # Note: start_memory parameter kept for API consistency but not used in error cases
        # We don't calculate memory delta for failed executions to avoid misleading data
        end_time = time.time()

        self._initialize_profile_data_if_needed(name)
        profile = self.profile_data[name]
        profile["call_count"] += 1
        profile["total_time"] += end_time - start_time
        profile["error_count"] = profile.get("error_count", 0) + 1

    def _update_profile_data(
        self,
        name: str,
        execution_time: float,
        memory_delta: Dict[str, float],
        end_memory: Dict[str, float],
    ):
        """Update profile data with execution results."""
        self._initialize_profile_data_if_needed(name)

        profile = self.profile_data[name]
        profile["call_count"] += 1
        profile["total_time"] += execution_time
        profile["total_memory_delta"]["rss"] += memory_delta["rss"]
        profile["total_memory_delta"]["vms"] += memory_delta["vms"]

        # Update max memory delta
        if memory_delta["rss"] > profile["max_memory_delta"]["rss"]:
            profile["max_memory_delta"]["rss"] = memory_delta["rss"]
        if memory_delta["vms"] > profile["max_memory_delta"]["vms"]:
            profile["max_memory_delta"]["vms"] = memory_delta["vms"]

        # Update peak memory
        if end_memory["rss"] > profile["peak_memory"]["rss"]:
            profile["peak_memory"]["rss"] = end_memory["rss"]
        if end_memory["vms"] > profile["peak_memory"]["vms"]:
            profile["peak_memory"]["vms"] = end_memory["vms"]

    def _initialize_profile_data_if_needed(self, name: str):
        """Initialize profile data structure if it doesn't exist."""
        if name not in self.profile_data:
            self.profile_data[name] = {
                "call_count": 0,
                "total_time": 0.0,
                "total_memory_delta": {"rss": 0.0, "vms": 0.0},
                "max_memory_delta": {"rss": 0.0, "vms": 0.0},
                "peak_memory": {"rss": 0.0, "vms": 0.0},
            }

    def get_profile_report(self) -> str:
        """Generate a human-readable profile report."""
        if not self.profile_data:
            return "No profiling data available."

        report_lines = ["Memory Profiling Report", "=" * 50]

        for method_name, data in sorted(self.profile_data.items()):
            call_count = data["call_count"]
            avg_time = data["total_time"] / call_count if call_count > 0 else 0
            avg_memory_rss = (
                data["total_memory_delta"]["rss"] / call_count if call_count > 0 else 0
            )
            avg_memory_vms = (
                data["total_memory_delta"]["vms"] / call_count if call_count > 0 else 0
            )

            report_lines.extend(
                [
                    f"\nMethod: {method_name}",
                    f"  Calls: {call_count}",
                    f"  Total Time: {data['total_time']:.3f}s",
                    f"  Avg Time: {avg_time:.3f}s",
                    f"  Avg Memory Delta (RSS): {avg_memory_rss:.2f}MB",
                    f"  Avg Memory Delta (VMS): {avg_memory_vms:.2f}MB",
                    f"  Max Memory Delta (RSS): {data['max_memory_delta']['rss']:.2f}MB",
                    f"  Max Memory Delta (VMS): {data['max_memory_delta']['vms']:.2f}MB",
                    f"  Peak Memory (RSS): {data['peak_memory']['rss']:.2f}MB",
                    f"  Peak Memory (VMS): {data['peak_memory']['vms']:.2f}MB",
                ]
            )

            if "error_count" in data:
                report_lines.append(f"  Errors: {data['error_count']}")

        return "\n".join(report_lines)

    def clear_profile_data(self):
        """Clear all collected profile data."""
        self.profile_data.clear()

    def get_memory_intensive_methods(
        self, threshold_mb: float = 10.0
    ) -> Dict[str, Dict[str, Any]]:
        """Get methods that use more than the specified threshold of memory."""
        intensive_methods = {}

        for method_name, data in self.profile_data.items():
            call_count = data["call_count"]
            if call_count > 0:
                avg_memory_rss = data["total_memory_delta"]["rss"] / call_count
                if (
                    avg_memory_rss > threshold_mb
                    or data["max_memory_delta"]["rss"] > threshold_mb
                ):
                    intensive_methods[method_name] = data

        return intensive_methods


# Global memory profiler instance
global_profiler = MemoryProfiler()


def profile_memory(method_name: Optional[str] = None):
    """Decorator function for easy memory profiling."""
    return global_profiler.profile_method(method_name)


def get_memory_report() -> str:
    """Get the global memory profiling report."""
    return global_profiler.get_profile_report()


def clear_memory_profile_data():
    """Clear the global memory profiling data."""
    global_profiler.clear_profile_data()


def get_memory_intensive_methods(
    threshold_mb: float = 10.0,
) -> Dict[str, Dict[str, Any]]:
    """Get memory-intensive methods from global profiler."""
    return global_profiler.get_memory_intensive_methods(threshold_mb)
