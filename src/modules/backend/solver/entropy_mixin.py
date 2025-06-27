"""
Shared entropy calculation utilities for strategy implementations.
"""

import math
from typing import List

from .common_utils import EntropyCalculator, get_pattern_counter, return_pattern_counter
from .memory_profiler import profile_memory


class EntropyCalculationMixin:
    """Mixin class providing shared entropy calculation methods for strategies."""

    @profile_memory("EntropyCalculationMixin._calculate_entropy_optimized")
    def _calculate_entropy_optimized(
        self, candidate: str, possible_answers: List[str]
    ) -> float:
        """
        Calculate entropy with memory optimization using object pooling.
        Shared implementation to avoid code duplication across strategies.
        """
        if not possible_answers:
            return 0.0

        # Use object pool for pattern counting
        pattern_counts = get_pattern_counter()

        try:
            # OPTIMIZATION: Early termination for very high entropy scores
            total_answers = len(possible_answers)
            if total_answers > 50:
                theoretical_max = math.log2(
                    min(total_answers, 243)
                )  # 243 is 3^5 max patterns
                excellent_threshold = (
                    theoretical_max * 0.85
                )  # 85% of theoretical maximum
            else:
                excellent_threshold = float(
                    "inf"
                )  # No early termination for small sets

            # Use optimized entropy calculation with early termination
            return EntropyCalculator.calculate_entropy_with_early_termination(
                candidate, possible_answers, excellent_threshold
            )
        finally:
            # Return object to pool
            return_pattern_counter(pattern_counts)
