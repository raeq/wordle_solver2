# src/modules/backend/solver/performance_optimizer.py
"""
Performance optimization utilities for stateless solver strategies.
"""
import time
from typing import Dict, List, Optional, Tuple

from ..legacy_word_manager import WordManager
from ..stateless_word_manager import StatelessWordManager
from .strategy_migration_factory import strategy_factory


class PerformanceOptimizer:
    """Utilities for optimizing and benchmarking stateless strategy performance."""

    def __init__(
        self,
        word_manager: WordManager,
        stateless_word_manager: Optional[StatelessWordManager] = None,
    ):
        """Initialize the performance optimizer."""
        self.word_manager = word_manager
        self.stateless_word_manager = stateless_word_manager or StatelessWordManager()

    def benchmark_all_strategies(
        self,
        test_constraints: List[Tuple[str, str]] = None,
        iterations: int = 10,
        count: int = 5,
    ) -> Dict[str, Dict[str, float]]:
        """Benchmark all available strategies."""
        if test_constraints is None:
            test_constraints = [("SLATE", "BYBBB"), ("CRANE", "YBGYB")]

        results = {}
        available_strategies = (
            strategy_factory.migration_manager.get_available_strategies()
        )

        for strategy_name in available_strategies.keys():
            # Benchmark legacy version
            legacy_time = self._benchmark_strategy(
                strategy_name, test_constraints, iterations, count, use_stateless=False
            )

            # Benchmark stateless version if available
            stateless_time = None
            if available_strategies[strategy_name]["stateless_available"]:
                stateless_time = self._benchmark_strategy(
                    strategy_name,
                    test_constraints,
                    iterations,
                    count,
                    use_stateless=True,
                )

            results[strategy_name] = {
                "legacy_time": legacy_time,
                "stateless_time": stateless_time,
                "improvement_ratio": (
                    legacy_time / stateless_time if stateless_time else None
                ),
                "available_stateless": stateless_time is not None,
            }

        return results

    def _benchmark_strategy(
        self,
        strategy_name: str,
        constraints: List[Tuple[str, str]],
        iterations: int,
        count: int,
        use_stateless: bool,
    ) -> Optional[float]:
        """Benchmark a single strategy."""
        try:
            strategy = strategy_factory.create_strategy(
                strategy_name=strategy_name,
                prefer_stateless=use_stateless,
                word_manager=self.word_manager,
                stateless_word_manager=self.stateless_word_manager,
            )

            times = []
            for _ in range(iterations):
                start_time = time.time()

                if use_stateless and hasattr(strategy, "get_top_suggestions"):
                    # Stateless interface
                    strategy.get_top_suggestions(
                        constraints=constraints,
                        count=count,
                        word_manager=self.word_manager,
                        stateless_word_manager=self.stateless_word_manager,
                    )
                else:
                    # Legacy interface
                    possible_words = self.word_manager.apply_multiple_constraints(
                        constraints
                    )
                    common_words = [
                        w for w in possible_words if w in self.word_manager.common_words
                    ]

                    strategy.get_top_suggestions(
                        possible_words=possible_words,
                        common_words=common_words,
                        guesses_so_far=constraints,
                        count=count,
                        word_manager=self.word_manager,
                    )

                end_time = time.time()
                times.append(end_time - start_time)

            return sum(times) / len(times)  # Average time

        except Exception as e:
            print(
                f"Benchmark failed for {strategy_name} ({'stateless' if use_stateless else 'legacy'}): {e}"
            )
            return None

    def optimize_strategy_parameters(
        self,
        strategy_name: str,
        parameter_ranges: Dict[str, List],
        test_scenarios: List[List[Tuple[str, str]]] = None,
    ) -> Dict[str, any]:
        """Optimize strategy parameters for best performance."""
        if test_scenarios is None:
            test_scenarios = [
                [("SLATE", "BYBBB")],
                [("SLATE", "BYBBB"), ("CRANE", "YBGYB")],
                [("SLATE", "BYBBB"), ("CRANE", "YBGYB"), ("POUND", "BBBBB")],
            ]

        best_params = {}
        best_score = float("inf")
        results = []

        # Generate parameter combinations
        param_combinations = self._generate_param_combinations(parameter_ranges)

        for params in param_combinations:
            total_time = 0.0
            total_quality = 0.0
            scenario_count = 0

            for scenario in test_scenarios:
                try:
                    # Create strategy with parameters
                    if strategy_name == "hybrid":
                        from .stateless_hybrid_strategy import StatelessHybridStrategy

                        strategy = StatelessHybridStrategy(
                            frequency_weight=params.get("frequency_weight", 0.4),
                            entropy_weight=params.get("entropy_weight", 0.6),
                        )
                    elif strategy_name == "weighted_gain":
                        from .stateless_weighted_gain_strategy import (
                            StatelessWeightedGainStrategy,
                        )

                        strategy = StatelessWeightedGainStrategy(
                            entropy_weight=params.get("entropy_weight", 0.5),
                            positional_weight=params.get("positional_weight", 0.3),
                            frequency_weight=params.get("frequency_weight", 0.2),
                        )
                    else:
                        # Use default strategy
                        strategy = strategy_factory.create_strategy(
                            strategy_name, prefer_stateless=True
                        )

                    # Benchmark this configuration
                    start_time = time.time()
                    suggestions = strategy.get_top_suggestions(
                        constraints=scenario,
                        count=5,
                        stateless_word_manager=self.stateless_word_manager,
                    )
                    end_time = time.time()

                    # Calculate metrics
                    time_taken = end_time - start_time
                    quality_score = self._calculate_quality_score(suggestions, scenario)

                    total_time += time_taken
                    total_quality += quality_score
                    scenario_count += 1

                except Exception as e:
                    print(f"Error testing params {params} on scenario {scenario}: {e}")
                    continue

            if scenario_count > 0:
                avg_time = total_time / scenario_count
                avg_quality = total_quality / scenario_count

                # Combined score (lower is better)
                combined_score = avg_time + (
                    1.0 / avg_quality if avg_quality > 0 else 1.0
                )

                results.append(
                    {
                        "params": params,
                        "avg_time": avg_time,
                        "avg_quality": avg_quality,
                        "combined_score": combined_score,
                    }
                )

                if combined_score < best_score:
                    best_score = combined_score
                    best_params = params

        return {
            "best_params": best_params,
            "best_score": best_score,
            "all_results": sorted(results, key=lambda x: x["combined_score"]),
        }

    def _generate_param_combinations(
        self, parameter_ranges: Dict[str, List]
    ) -> List[Dict]:
        """Generate all combinations of parameters."""
        import itertools

        keys = list(parameter_ranges.keys())
        values = list(parameter_ranges.values())

        combinations = []
        for value_combo in itertools.product(*values):
            combinations.append(dict(zip(keys, value_combo)))

        return combinations

    def _calculate_quality_score(
        self, suggestions: List[str], scenario: List[Tuple[str, str]]
    ) -> float:
        """Calculate a quality score for suggestions based on various metrics."""
        if not suggestions:
            return 0.0

        # Simple quality metrics
        score = 0.0

        # Diversity score (unique letters)
        unique_letters = set()
        for word in suggestions[:3]:  # Top 3 suggestions
            unique_letters.update(word)
        diversity_score = len(unique_letters) / 15.0  # Max 15 unique letters in 3 words

        # Length score (prefer full suggestion lists)
        length_score = len(suggestions) / 5.0  # Expecting 5 suggestions

        # Common word score (prefer suggestions that include common words)
        common_count = sum(
            1 for word in suggestions if word in self.word_manager.common_words
        )
        common_score = common_count / len(suggestions) if suggestions else 0.0

        # Combine scores
        score = 0.4 * diversity_score + 0.3 * length_score + 0.3 * common_score

        return score

    def analyze_memory_usage(
        self, strategy_name: str, constraint_sets: List[List[Tuple[str, str]]] = None
    ) -> Dict[str, any]:
        """Analyze memory usage patterns for a strategy."""
        import gc
        import tracemalloc

        if constraint_sets is None:
            constraint_sets = [
                [],  # No constraints
                [("SLATE", "BYBBB")],  # Single constraint
                [("SLATE", "BYBBB"), ("CRANE", "YBGYB")],  # Multiple constraints
                [
                    ("SLATE", "BYBBB"),
                    ("CRANE", "YBGYB"),
                    ("POUND", "BBBBB"),
                    ("MIGHT", "BBBBB"),
                ],  # Many constraints
            ]

        results = {}

        for i, constraints in enumerate(constraint_sets):
            # Start memory tracing
            tracemalloc.start()
            gc.collect()

            try:
                # Create strategy
                strategy = strategy_factory.create_strategy(
                    strategy_name,
                    prefer_stateless=True,
                    stateless_word_manager=self.stateless_word_manager,
                )

                # Run strategy
                suggestions = strategy.get_top_suggestions(
                    constraints=constraints,
                    count=10,
                    stateless_word_manager=self.stateless_word_manager,
                )

                # Get memory snapshot
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                results[f"scenario_{i}"] = {
                    "constraints_count": len(constraints),
                    "current_memory_mb": current / 1024 / 1024,
                    "peak_memory_mb": peak / 1024 / 1024,
                    "suggestions_count": len(suggestions),
                }

            except Exception as e:
                tracemalloc.stop()
                results[f"scenario_{i}"] = {"error": str(e)}

        return results

    def create_performance_report(self) -> Dict[str, any]:
        """Create a comprehensive performance report."""
        print("Generating comprehensive performance report...")

        # Benchmark all strategies
        benchmark_results = self.benchmark_all_strategies(iterations=5)

        # Memory analysis for key strategies
        memory_results = {}
        for strategy_name in ["frequency", "entropy", "hybrid"]:
            try:
                memory_results[strategy_name] = self.analyze_memory_usage(strategy_name)
            except Exception as e:
                memory_results[strategy_name] = {"error": str(e)}

        # Strategy validation
        validation_results = strategy_factory.run_migration_validation(
            self.word_manager, self.stateless_word_manager
        )

        # Performance recommendations
        recommendations = self._generate_performance_recommendations(
            benchmark_results, memory_results, validation_results
        )

        return {
            "benchmark_results": benchmark_results,
            "memory_analysis": memory_results,
            "validation_results": validation_results,
            "recommendations": recommendations,
            "summary": self._create_performance_summary(benchmark_results),
        }

    def _generate_performance_recommendations(
        self, benchmark_results: Dict, memory_results: Dict, validation_results: Dict
    ) -> List[str]:
        """Generate performance recommendations based on analysis."""
        recommendations = []

        # Analyze benchmark results
        fastest_strategy = None
        fastest_time = float("inf")

        for strategy_name, results in benchmark_results.items():
            if results["stateless_time"] and results["stateless_time"] < fastest_time:
                fastest_time = results["stateless_time"]
                fastest_strategy = strategy_name

        if fastest_strategy:
            recommendations.append(
                f"Fastest strategy: {fastest_strategy} ({fastest_time:.4f}s average)"
            )

        # Check for significant improvements
        for strategy_name, results in benchmark_results.items():
            if results["improvement_ratio"] and results["improvement_ratio"] > 1.5:
                recommendations.append(
                    f"{strategy_name}: {results['improvement_ratio']:.1f}x faster with stateless implementation"
                )

        # Memory recommendations
        for strategy_name, memory_data in memory_results.items():
            if isinstance(memory_data, dict) and "scenario_3" in memory_data:
                peak_memory = memory_data["scenario_3"].get("peak_memory_mb", 0)
                if peak_memory > 100:  # More than 100MB
                    recommendations.append(
                        f"{strategy_name}: High memory usage ({peak_memory:.1f}MB) - consider optimization"
                    )

        # Validation recommendations
        for strategy_name, validation in validation_results.items():
            if validation["status"] == "tested" and not validation["equivalent"]:
                recommendations.append(
                    f"{strategy_name}: Low overlap ({validation['overlap_percentage']:.1f}%) - review implementation"
                )

        return recommendations

    def _create_performance_summary(self, benchmark_results: Dict) -> Dict[str, any]:
        """Create a performance summary."""
        total_strategies = len(benchmark_results)
        migrated_count = sum(
            1 for r in benchmark_results.values() if r["available_stateless"]
        )

        avg_improvement = 0.0
        improvement_count = 0

        for results in benchmark_results.values():
            if results["improvement_ratio"]:
                avg_improvement += results["improvement_ratio"]
                improvement_count += 1

        avg_improvement = (
            avg_improvement / improvement_count if improvement_count > 0 else 1.0
        )

        return {
            "total_strategies": total_strategies,
            "migrated_strategies": migrated_count,
            "migration_percentage": (migrated_count / total_strategies) * 100,
            "average_improvement_ratio": avg_improvement,
            "significant_improvements": improvement_count,
        }
