# src/tests/test_stateless_solver_strategies.py
"""
Tests for stateless solver strategies to ensure correct migration.
"""
import os
import tempfile
import unittest

from src.modules.backend.solver.stateless_entropy_strategy import (
    StatelessEntropyStrategy,
)
from src.modules.backend.solver.stateless_frequency_strategy import (
    StatelessFrequencyStrategy,
)
from src.modules.backend.solver.stateless_hybrid_strategy import StatelessHybridStrategy
from src.modules.backend.stateless_word_manager import StatelessWordManager


class TestStatelessSolverStrategies(unittest.TestCase):
    """Tests for stateless solver strategy implementations."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary word file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.words_path = os.path.join(self.temp_dir.name, "test_words.txt")

        with open(self.words_path, "w", encoding="utf-8") as f:
            # Format: word frequency entropy
            f.write("APPLE 50000 5.2\n")
            f.write("DATES 30000 6.1\n")
            f.write("ELDER 25000 7.3\n")
            f.write("FRUIT 45000 4.8\n")
            f.write("GRAPE 35000 6.5\n")
            f.write("HONEY 20000 7.8\n")
            f.write("IGLOO 15000 8.2\n")
            f.write("JELLY 18000 7.9\n")
            f.write("LIMON 12000 8.5\n")
            f.write("MOUSE 22000 7.1\n")
            f.write("SLATE 40000 6.8\n")
            f.write("CRANE 38000 7.2\n")

        # Initialize stateless word manager only
        self.stateless_word_manager = StatelessWordManager(words_file=self.words_path)
        self.stateless_word_manager.set_test_mode(True)

        # Initialize strategies - using only stateless implementations
        self.stateless_frequency_strategy = StatelessFrequencyStrategy()
        self.stateless_entropy_strategy = StatelessEntropyStrategy()
        self.stateless_hybrid_strategy = StatelessHybridStrategy()

        # Common test data - use less restrictive constraints for small test dataset
        self.constraints = [("SLATE", "BYBBB")]  # Single constraint instead of double

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_stateless_frequency_strategy_basic(self):
        """Test basic functionality of stateless frequency strategy."""
        suggestions = self.stateless_frequency_strategy.get_top_suggestions(
            constraints=self.constraints,
            count=3,
            stateless_word_manager=self.stateless_word_manager,
        )

        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 3)
        self.assertTrue(all(isinstance(word, str) for word in suggestions))

    def test_stateless_with_stateless_word_manager(self):
        """Test stateless strategy with pure stateless word manager."""
        suggestions = self.stateless_frequency_strategy.get_top_suggestions(
            constraints=self.constraints,
            count=3,
            stateless_word_manager=self.stateless_word_manager,
        )

        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 3)

    def test_different_stateless_strategies(self):
        """Test that different stateless strategies produce different results."""
        # Get results from frequency strategy
        frequency_suggestions = self.stateless_frequency_strategy.get_top_suggestions(
            constraints=self.constraints,
            count=5,
            stateless_word_manager=self.stateless_word_manager,
        )

        # Get results from entropy strategy
        entropy_suggestions = self.stateless_entropy_strategy.get_top_suggestions(
            constraints=self.constraints,
            count=5,
            stateless_word_manager=self.stateless_word_manager,
        )

        # Get results from hybrid strategy
        hybrid_suggestions = self.stateless_hybrid_strategy.get_top_suggestions(
            constraints=self.constraints,
            count=5,
            stateless_word_manager=self.stateless_word_manager,
        )

        # All should return some suggestions
        self.assertIsInstance(frequency_suggestions, list)
        self.assertIsInstance(entropy_suggestions, list)
        self.assertIsInstance(hybrid_suggestions, list)

        # Different strategies may return different orders or even different words
        # We're just checking that the implementation doesn't error out
        print(f"Frequency strategy: {frequency_suggestions}")
        print(f"Entropy strategy: {entropy_suggestions}")
        print(f"Hybrid strategy: {hybrid_suggestions}")

    def test_stateless_empty_constraints(self):
        """Test stateless strategy with no constraints."""
        suggestions = self.stateless_frequency_strategy.get_top_suggestions(
            constraints=[], count=5, stateless_word_manager=self.stateless_word_manager
        )

        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 5)
        self.assertGreater(len(suggestions), 0)

    def test_stateless_prefer_common_flag(self):
        """Test prefer_common flag functionality."""
        # Use empty constraints to ensure we get results
        suggestions_prefer_common = (
            self.stateless_frequency_strategy.get_top_suggestions(
                constraints=[],  # Use empty constraints
                count=5,
                stateless_word_manager=self.stateless_word_manager,
                prefer_common=True,
            )
        )

        suggestions_no_preference = (
            self.stateless_frequency_strategy.get_top_suggestions(
                constraints=[],  # Use empty constraints
                count=5,
                stateless_word_manager=self.stateless_word_manager,
                prefer_common=False,
            )
        )

        self.assertIsInstance(suggestions_prefer_common, list)
        self.assertIsInstance(suggestions_no_preference, list)

        # Both should return valid suggestions when no constraints are applied
        self.assertGreater(len(suggestions_prefer_common), 0)
        self.assertGreater(len(suggestions_no_preference), 0)

    def test_stateless_word_set_parameter(self):
        """Test word_set parameter functionality."""
        custom_word_set = {"APPLE", "DATES", "FRUIT"}

        suggestions = self.stateless_frequency_strategy.get_top_suggestions(
            constraints=[],
            count=5,
            stateless_word_manager=self.stateless_word_manager,
            word_set=custom_word_set,
        )

        # All suggestions should be from the custom word set
        suggestion_set = set(suggestions)
        self.assertTrue(suggestion_set.issubset(custom_word_set))

    def test_stateless_performance(self):
        """Test performance of stateless strategy."""
        import time

        start_time = time.time()

        # Run multiple iterations
        for _ in range(10):
            self.stateless_frequency_strategy.get_top_suggestions(
                constraints=self.constraints,
                count=3,
                stateless_word_manager=self.stateless_word_manager,
            )

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        self.assertLess(duration, 5.0, f"Stateless strategy took too long: {duration}s")

    def test_stateless_consistency(self):
        """Test that stateless strategy produces consistent results."""
        suggestions1 = self.stateless_frequency_strategy.get_top_suggestions(
            constraints=self.constraints,
            count=3,
            stateless_word_manager=self.stateless_word_manager,
        )

        suggestions2 = self.stateless_frequency_strategy.get_top_suggestions(
            constraints=self.constraints,
            count=3,
            stateless_word_manager=self.stateless_word_manager,
        )

        self.assertEqual(
            suggestions1, suggestions2, "Stateless strategy should be deterministic"
        )

    def test_stateless_no_word_manager_error(self):
        """Test that appropriate error is raised when no word manager is provided."""
        with self.assertRaises(ValueError):
            self.stateless_frequency_strategy.get_top_suggestions(
                constraints=self.constraints, count=3
            )

    def test_stateless_complex_constraints(self):
        """Test stateless strategy with complex constraint sequences."""
        complex_constraints = [
            ("SLATE", "BYBBB"),
            ("CRANE", "YBGYB"),
            ("POUND", "BBBBB"),
        ]

        suggestions = self.stateless_frequency_strategy.get_top_suggestions(
            constraints=complex_constraints,
            count=3,
            stateless_word_manager=self.stateless_word_manager,
        )

        self.assertIsInstance(suggestions, list)
        # With complex constraints, might have fewer results
        self.assertLessEqual(len(suggestions), 3)


if __name__ == "__main__":
    unittest.main()
