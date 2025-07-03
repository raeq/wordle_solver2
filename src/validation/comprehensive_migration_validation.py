# src/validation/comprehensive_migration_validation.py
"""
Comprehensive validation script for the complete solver strategy migration.
"""
import sys
import time
from pathlib import Path
from typing import Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.backend.enhanced_game_state_manager import (
    EnhancedGameStateManager,
    StatelessGameStateManager,
)
from modules.backend.solver.performance_optimizer import PerformanceOptimizer
from modules.backend.solver.strategy_migration_factory import strategy_factory
from modules.backend.stateless_word_manager import StatelessWordManager
from modules.backend.word_manager import WordManager


class ComprehensiveMigrationValidator:
    """Comprehensive validator for the complete migration."""

    def __init__(self, words_file: str = None):
        """Initialize the validator."""
        self.word_manager = WordManager(words_file=words_file)
        self.stateless_word_manager = StatelessWordManager(words_file=words_file)
        self.performance_optimizer = PerformanceOptimizer(
            self.word_manager, self.stateless_word_manager
        )

    def run_full_validation(self) -> Dict[str, any]:
        """Run comprehensive validation of the entire migration."""
        print("🚀 Starting Comprehensive Migration Validation...")

        results = {
            "timestamp": time.time(),
            "strategy_validation": self.validate_all_strategies(),
            "performance_validation": self.validate_performance(),
            "integration_validation": self.validate_integration(),
            "functional_validation": self.validate_functionality(),
            "summary": {},
        }

        # Generate summary
        results["summary"] = self.generate_validation_summary(results)

        return results

    def validate_all_strategies(self) -> Dict[str, any]:
        """Validate all migrated strategies."""
        print("\n📋 Validating All Strategies...")

        strategy_results = {}
        available_strategies = (
            strategy_factory.migration_manager.get_available_strategies()
        )

        for strategy_name, info in available_strategies.items():
            print(f"  🔍 Testing {strategy_name}...")

            strategy_results[strategy_name] = {
                "legacy_available": info["legacy_available"],
                "stateless_available": info["stateless_available"],
                "migration_status": info["migration_status"],
                "tests": {},
            }

            # Test legacy strategy
            try:
                legacy_strategy = strategy_factory.create_strategy(
                    strategy_name, prefer_stateless=False
                )

                # Test with sample constraints
                possible_words = self.word_manager.apply_multiple_constraints(
                    [("SLATE", "BYBBB")]
                )
                common_words = [
                    w for w in possible_words if w in self.word_manager.common_words
                ]

                legacy_suggestions = legacy_strategy.get_top_suggestions(
                    possible_words=possible_words,
                    common_words=common_words,
                    guesses_so_far=[("SLATE", "BYBBB")],
                    count=5,
                    word_manager=self.word_manager,
                )

                strategy_results[strategy_name]["tests"]["legacy"] = {
                    "success": True,
                    "suggestions_count": len(legacy_suggestions),
                    "sample_suggestions": legacy_suggestions[:3],
                }

            except Exception as e:
                strategy_results[strategy_name]["tests"]["legacy"] = {
                    "success": False,
                    "error": str(e),
                }

            # Test stateless strategy if available
            if info["stateless_available"]:
                try:
                    stateless_strategy = strategy_factory.create_strategy(
                        strategy_name, prefer_stateless=True
                    )

                    stateless_suggestions = stateless_strategy.get_top_suggestions(
                        constraints=[("SLATE", "BYBBB")],
                        count=5,
                        stateless_word_manager=self.stateless_word_manager,
                    )

                    strategy_results[strategy_name]["tests"]["stateless"] = {
                        "success": True,
                        "suggestions_count": len(stateless_suggestions),
                        "sample_suggestions": stateless_suggestions[:3],
                    }

                    # Compare results
                    if "legacy" in strategy_results[strategy_name]["tests"]:
                        legacy_set = set(
                            strategy_results[strategy_name]["tests"]["legacy"].get(
                                "sample_suggestions", []
                            )
                        )
                        stateless_set = set(stateless_suggestions[:3])
                        overlap = len(legacy_set.intersection(stateless_set))

                        strategy_results[strategy_name]["tests"]["comparison"] = {
                            "overlap_count": overlap,
                            "total_compared": min(len(legacy_set), len(stateless_set)),
                            "overlap_percentage": (
                                (overlap / min(len(legacy_set), len(stateless_set)))
                                * 100
                                if min(len(legacy_set), len(stateless_set)) > 0
                                else 0
                            ),
                        }

                except Exception as e:
                    strategy_results[strategy_name]["tests"]["stateless"] = {
                        "success": False,
                        "error": str(e),
                    }

        return strategy_results

    def validate_performance(self) -> Dict[str, any]:
        """Validate performance improvements."""
        print("\n⚡ Validating Performance...")

        try:
            # Run comprehensive benchmarks
            benchmark_results = self.performance_optimizer.benchmark_all_strategies(
                iterations=3  # Reduced for validation speed
            )

            # Create performance report
            performance_report = self.performance_optimizer.create_performance_report()

            return {
                "benchmark_success": True,
                "benchmark_results": benchmark_results,
                "performance_summary": performance_report.get("summary", {}),
                "recommendations": performance_report.get("recommendations", []),
            }

        except Exception as e:
            return {"benchmark_success": False, "error": str(e)}

    def validate_integration(self) -> Dict[str, any]:
        """Validate integration components."""
        print("\n🔗 Validating Integration...")

        integration_results = {}

        # Test EnhancedGameStateManager
        try:
            enhanced_manager = EnhancedGameStateManager(
                word_manager=self.word_manager,
                strategy_name="frequency",
                use_stateless=True,
                stateless_word_manager=self.stateless_word_manager,
            )

            # Test basic functionality
            enhanced_manager.make_guess("SLATE", "BYBBB")
            suggestions = enhanced_manager.get_top_suggestions(5)
            strategy_info = enhanced_manager.get_strategy_info()

            # Test strategy switching
            switch_success = enhanced_manager.switch_strategy(
                "entropy", use_stateless=True
            )

            integration_results["enhanced_game_manager"] = {
                "success": True,
                "suggestions_count": len(suggestions),
                "is_stateless": strategy_info["is_stateless"],
                "strategy_switch_success": switch_success,
            }

        except Exception as e:
            integration_results["enhanced_game_manager"] = {
                "success": False,
                "error": str(e),
            }

        # Test StatelessGameStateManager
        try:
            stateless_manager = StatelessGameStateManager(
                stateless_word_manager=self.stateless_word_manager,
                default_strategy="frequency",
            )

            # Test stateless suggestions
            suggestions = stateless_manager.get_suggestions(
                constraints=[("SLATE", "BYBBB"), ("CRANE", "YBGYB")], count=5
            )

            # Test game state analysis
            analysis = stateless_manager.analyze_game_state([("SLATE", "BYBBB")])

            integration_results["stateless_game_manager"] = {
                "success": True,
                "suggestions_count": len(suggestions),
                "analysis_keys": list(analysis.keys()),
            }

        except Exception as e:
            integration_results["stateless_game_manager"] = {
                "success": False,
                "error": str(e),
            }

        return integration_results

    def validate_functionality(self) -> Dict[str, any]:
        """Validate key functionality works correctly."""
        print("\n⚙️ Validating Core Functionality...")

        functionality_results = {}

        # Test stateless word filtering
        try:
            # Test single constraint
            single_result = self.word_manager.apply_single_constraint("SLATE", "BYBBB")

            # Test multiple constraints
            multiple_result = self.word_manager.apply_multiple_constraints(
                [("SLATE", "BYBBB"), ("CRANE", "YBGYB")]
            )

            # Test pattern matching
            pattern_result = self.word_manager.get_words_matching_pattern(
                {0: "A", 4: "E"}
            )

            functionality_results["word_filtering"] = {
                "success": True,
                "single_constraint_count": len(single_result),
                "multiple_constraints_count": len(multiple_result),
                "pattern_matching_count": len(pattern_result),
            }

        except Exception as e:
            functionality_results["word_filtering"] = {
                "success": False,
                "error": str(e),
            }

        # Test stateless word manager
        try:
            stateless_result = self.stateless_word_manager.apply_multiple_constraints(
                [("SLATE", "BYBBB"), ("CRANE", "YBGYB")]
            )

            common_from_set = self.stateless_word_manager.get_common_words_from_set(
                set(stateless_result)
            )

            functionality_results["stateless_word_manager"] = {
                "success": True,
                "filtered_words_count": len(stateless_result),
                "common_words_count": len(common_from_set),
            }

        except Exception as e:
            functionality_results["stateless_word_manager"] = {
                "success": False,
                "error": str(e),
            }

        return functionality_results

    def generate_validation_summary(self, results: Dict[str, any]) -> Dict[str, any]:
        """Generate a comprehensive validation summary."""
        summary = {
            "overall_success": True,
            "total_strategies": 0,
            "migrated_strategies": 0,
            "successful_strategies": 0,
            "performance_improvement": False,
            "integration_success": False,
            "functionality_success": False,
            "issues": [],
        }

        # Analyze strategy validation
        if "strategy_validation" in results:
            strategy_data = results["strategy_validation"]
            summary["total_strategies"] = len(strategy_data)

            for strategy_name, strategy_info in strategy_data.items():
                if strategy_info.get("stateless_available", False):
                    summary["migrated_strategies"] += 1

                # Check if both legacy and stateless tests passed
                tests = strategy_info.get("tests", {})
                legacy_success = tests.get("legacy", {}).get("success", False)
                stateless_success = tests.get("stateless", {}).get("success", False)

                if legacy_success and (
                    not strategy_info.get("stateless_available", False)
                    or stateless_success
                ):
                    summary["successful_strategies"] += 1
                else:
                    summary["issues"].append(
                        f"Strategy {strategy_name} has test failures"
                    )

        # Analyze performance validation
        if "performance_validation" in results:
            performance_data = results["performance_validation"]
            summary["performance_improvement"] = performance_data.get(
                "benchmark_success", False
            )

            if not summary["performance_improvement"]:
                summary["issues"].append("Performance benchmarking failed")

        # Analyze integration validation
        if "integration_validation" in results:
            integration_data = results["integration_validation"]
            enhanced_success = integration_data.get("enhanced_game_manager", {}).get(
                "success", False
            )
            stateless_success = integration_data.get("stateless_game_manager", {}).get(
                "success", False
            )

            summary["integration_success"] = enhanced_success and stateless_success

            if not summary["integration_success"]:
                summary["issues"].append("Integration components have failures")

        # Analyze functionality validation
        if "functional_validation" in results:
            functional_data = results["functional_validation"]
            word_filtering_success = functional_data.get("word_filtering", {}).get(
                "success", False
            )
            stateless_wm_success = functional_data.get(
                "stateless_word_manager", {}
            ).get("success", False)

            summary["functionality_success"] = (
                word_filtering_success and stateless_wm_success
            )

            if not summary["functionality_success"]:
                summary["issues"].append("Core functionality has failures")

        # Overall success
        summary["overall_success"] = (
            summary["successful_strategies"] == summary["total_strategies"]
            and summary["performance_improvement"]
            and summary["integration_success"]
            and summary["functionality_success"]
        )

        return summary

    def print_validation_report(self, results: Dict[str, any]) -> None:
        """Print a formatted validation report."""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE MIGRATION VALIDATION REPORT")
        print("=" * 80)

        summary = results.get("summary", {})

        # Overall status
        status_icon = "✅" if summary.get("overall_success", False) else "❌"
        print(
            f"\n{status_icon} Overall Migration Status: {'SUCCESS' if summary.get('overall_success', False) else 'ISSUES FOUND'}"
        )

        # Strategy summary
        print("\n📋 Strategy Migration:")
        print(f"   Total Strategies: {summary.get('total_strategies', 0)}")
        print(f"   Migrated to Stateless: {summary.get('migrated_strategies', 0)}")
        print(f"   Successfully Tested: {summary.get('successful_strategies', 0)}")

        # Performance summary
        perf_icon = "✅" if summary.get("performance_improvement", False) else "❌"
        print(f"\n⚡ Performance: {perf_icon}")

        # Integration summary
        integration_icon = "✅" if summary.get("integration_success", False) else "❌"
        print(f"\n🔗 Integration: {integration_icon}")

        # Functionality summary
        func_icon = "✅" if summary.get("functionality_success", False) else "❌"
        print(f"\n⚙️ Core Functionality: {func_icon}")

        # Issues
        if summary.get("issues"):
            print("\n⚠️ Issues Found:")
            for issue in summary["issues"]:
                print(f"   - {issue}")
        else:
            print("\n🎉 No issues found! Migration completed successfully.")

        # Performance details
        if "performance_validation" in results:
            perf_data = results["performance_validation"]
            if "performance_summary" in perf_data:
                perf_summary = perf_data["performance_summary"]
                print("\n📈 Performance Details:")
                print(
                    f"   Migration Percentage: {perf_summary.get('migration_percentage', 0):.1f}%"
                )
                print(
                    f"   Average Improvement: {perf_summary.get('average_improvement_ratio', 1.0):.2f}x"
                )

        print("\n" + "=" * 80)


def main():
    """Main validation entry point."""
    validator = ComprehensiveMigrationValidator()

    # Run full validation
    results = validator.run_full_validation()

    # Print report
    validator.print_validation_report(results)

    # Return exit code based on success
    return 0 if results.get("summary", {}).get("overall_success", False) else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
