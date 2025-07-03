# src/tests/test_word_manager_integration.py
"""
Integration tests for the refactored word manager with stateless filtering.
"""
import os
import tempfile
import unittest

from src.modules.backend.stateless_word_manager import StatelessWordManager
from src.modules.backend.word_manager import WordManager


class TestWordManagerIntegration(unittest.TestCase):
    """Integration tests comparing stateful and stateless approaches."""

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

        # Initialize both managers
        self.stateful_manager = WordManager(words_file=self.words_path)
        self.stateful_manager.set_test_mode(True)

        self.stateless_manager = StatelessWordManager(words_file=self.words_path)
        self.stateless_manager.set_test_mode(True)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_backward_compatibility(self):
        """Test that existing stateful API still works."""
        # Test the old stateful approach
        original_count = self.stateful_manager.get_word_count()
        self.stateful_manager.filter_words("APPLE", "GGGGG")
        self.assertEqual(self.stateful_manager.get_word_count(), 1)
        self.assertEqual(self.stateful_manager.get_possible_words(), ["APPLE"])

        # Reset and test again
        self.stateful_manager.reset()
        self.assertEqual(self.stateful_manager.get_word_count(), original_count)

    def test_stateless_vs_stateful_equivalence(self):
        """Test that stateless and stateful approaches give same results."""
        # Apply same constraints to both managers
        constraints = [
            (
                "TEARS",
                "BYBBB",
            ),  # T not in word, E in word but not pos 1, A,R,S not in word
            ("CLOUD", "BBBBB"),  # C,L,O,U,D not in word
        ]

        # Stateless approach
        stateless_result = self.stateless_manager.apply_multiple_constraints(
            constraints
        )

        # Stateful approach (simulate step by step)
        self.stateful_manager.reset()
        for guess, result in constraints:
            self.stateful_manager.filter_words(guess, result)
        stateful_result = self.stateful_manager.get_possible_words()

        # Results should be identical
        self.assertEqual(set(stateless_result), set(stateful_result))

    def test_new_stateless_methods_integration(self):
        """Test that new stateless methods work correctly with the stateful manager."""
        # Test apply_single_constraint doesn't affect state
        original_possible = self.stateful_manager.get_possible_words()
        filtered = self.stateful_manager.apply_single_constraint("APPLE", "GGGGG")

        # State should be unchanged
        self.assertEqual(self.stateful_manager.get_possible_words(), original_possible)
        # But filtered result should be different
        self.assertEqual(filtered, ["APPLE"])

    def test_pattern_matching_consistency(self):
        """Test pattern matching gives consistent results between managers."""
        pattern = {0: "A", 4: "E"}  # Words starting with A and ending with E

        stateless_result = self.stateless_manager.get_words_matching_pattern(pattern)
        stateful_result = self.stateful_manager.get_words_matching_pattern(pattern)

        self.assertEqual(set(stateless_result), set(stateful_result))
        # Should match APPLE
        self.assertIn("APPLE", stateless_result)

    def test_letter_filtering_consistency(self):
        """Test letter inclusion/exclusion consistency."""
        # Test inclusion
        letters = ["A", "E"]
        stateless_incl = self.stateless_manager.get_words_containing_letters(letters)
        stateful_incl = self.stateful_manager.get_words_containing_letters(letters)
        self.assertEqual(set(stateless_incl), set(stateful_incl))

        # Test exclusion
        letters = ["Z", "X"]
        stateless_excl = self.stateless_manager.get_words_excluding_letters(letters)
        stateful_excl = self.stateful_manager.get_words_excluding_letters(letters)
        self.assertEqual(set(stateless_excl), set(stateful_excl))

    def test_frequency_entropy_consistency(self):
        """Test frequency and entropy methods work consistently."""
        word = "APPLE"

        # Test frequency
        stateless_freq = self.stateless_manager.get_word_frequency(word)
        stateful_freq = self.stateful_manager.get_word_frequency(word)
        self.assertEqual(stateless_freq, stateful_freq)

        # Test entropy
        stateless_entropy = self.stateless_manager.get_word_entropy(word)
        stateful_entropy = self.stateful_manager.get_word_entropy(word)
        self.assertEqual(stateless_entropy, stateful_entropy)

    def test_common_words_consistency(self):
        """Test common words identification is consistent."""
        stateless_common = set(self.stateless_manager.get_common_words())
        stateful_common = self.stateful_manager.common_words

        self.assertEqual(stateless_common, stateful_common)

    def test_performance_comparison(self):
        """Test that stateless approach performs comparably."""
        import time

        constraints = [
            ("TESTS", "BYBYB"),
            ("ROUND", "YBBYB"),
            ("FLING", "BBBBB"),
        ]

        # Time stateless approach
        start = time.time()
        stateless_result = self.stateless_manager.apply_multiple_constraints(
            constraints
        )
        stateless_time = time.time() - start

        # Time stateful approach
        self.stateful_manager.reset()
        start = time.time()
        for guess, result in constraints:
            self.stateful_manager.filter_words(guess, result)
        stateful_result = self.stateful_manager.get_possible_words()
        stateful_time = time.time() - start

        # Results should be the same
        self.assertEqual(set(stateless_result), set(stateful_result))

        # Performance should be reasonable (allow 10x difference)
        self.assertLess(stateless_time, stateful_time * 10)

    def test_functional_composition(self):
        """Test functional composition features in stateless manager."""
        # Create composed filter
        pattern_filter = self.stateless_manager.create_pattern_filter(
            {4: "E"}
        )  # Ends with E
        inclusion_filter = self.stateless_manager.create_letter_inclusion_filter(
            ["A"]
        )  # Contains A

        # Apply composed filter
        all_words = set(self.stateless_manager.get_all_words())
        result1 = set(pattern_filter(all_words))
        result2 = set(inclusion_filter(result1))

        # Should get words that end with E and contain A
        expected = {"APPLE", "GRAPE"}
        self.assertTrue(expected.issubset(result2))

    def test_immutability_guarantees(self):
        """Test that stateless manager maintains immutability."""
        original_all_words = self.stateless_manager.all_words
        original_common_words = self.stateless_manager.common_words

        # Perform various operations
        self.stateless_manager.apply_single_constraint("APPLE", "GGGGG")
        self.stateless_manager.get_words_matching_pattern({0: "A"})
        self.stateless_manager.apply_multiple_constraints([("TEST", "BBBB")])

        # Original sets should be unchanged (being frozensets)
        self.assertEqual(self.stateless_manager.all_words, original_all_words)
        self.assertEqual(self.stateless_manager.common_words, original_common_words)

        # Verify they are actually frozen
        self.assertIsInstance(self.stateless_manager.all_words, frozenset)
        self.assertIsInstance(self.stateless_manager.common_words, frozenset)

    def test_edge_case_handling(self):
        """Test edge cases are handled consistently."""
        # Empty constraints
        stateless_empty = self.stateless_manager.apply_multiple_constraints([])
        stateful_empty_stateless = self.stateful_manager.get_possible_words_stateless(
            []
        )

        self.assertEqual(
            len(stateless_empty), len(self.stateless_manager.get_all_words())
        )
        self.assertEqual(set(stateless_empty), set(stateful_empty_stateless))

        # Invalid patterns should raise same errors
        with self.assertRaises(ValueError):
            self.stateless_manager.get_words_matching_pattern({-1: "A"})

        with self.assertRaises(ValueError):
            self.stateful_manager.get_words_matching_pattern({-1: "A"})

    def test_migration_path(self):
        """Test smooth migration from stateful to stateless approach."""
        # Existing code using stateful approach
        self.stateful_manager.filter_words(
            "APPLE", "BYBBB"
        )  # A not at pos 0, P not at pos 1, etc
        stateful_words = self.stateful_manager.get_possible_words()

        # New code using stateless approach with same constraints
        stateless_words = self.stateless_manager.apply_single_constraint(
            "APPLE", "BYBBB"
        )

        # Results should be equivalent
        self.assertEqual(set(stateful_words), set(stateless_words))


if __name__ == "__main__":
    unittest.main()
