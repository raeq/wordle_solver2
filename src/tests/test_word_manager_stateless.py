# src/tests/test_word_manager_stateless.py
"""
Unit tests for the stateless WordManager refactoring.
"""
import os
import tempfile
import unittest

from src.modules.backend.legacy_word_manager import WordManager


class TestWordManagerStateless(unittest.TestCase):
    """Test cases for stateless WordManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary word file for testing
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a test words file with diverse patterns for comprehensive testing
        self.words_path = os.path.join(self.temp_dir.name, "test_words.txt")
        with open(self.words_path, "w", encoding="utf-8") as f:
            # Format: word frequency entropy
            f.write(
                "APPLE 50000 5.2\n"
            )  # A at pos 0, P at pos 1&2, L at pos 3, E at pos 4
            f.write(
                "DATES 30000 6.1\n"
            )  # D at pos 0, A at pos 1, T at pos 2, E at pos 3, S at pos 4
            f.write(
                "ELDER 25000 7.3\n"
            )  # E at pos 0&3, L at pos 1, D at pos 2, R at pos 4
            f.write(
                "FRUIT 45000 4.8\n"
            )  # F at pos 0, R at pos 1, U at pos 2, I at pos 3, T at pos 4
            f.write(
                "GRAPE 35000 6.5\n"
            )  # G at pos 0, R at pos 1, A at pos 2, P at pos 3, E at pos 4
            f.write(
                "HONEY 20000 7.8\n"
            )  # H at pos 0, O at pos 1, N at pos 2, E at pos 3, Y at pos 4
            f.write(
                "IGLOO 15000 8.2\n"
            )  # I at pos 0, G at pos 1, L at pos 2, O at pos 3&4
            f.write(
                "JELLY 18000 7.9\n"
            )  # J at pos 0, E at pos 1, L at pos 2&3, Y at pos 4
            f.write(
                "LIMON 12000 8.5\n"
            )  # L at pos 0, I at pos 1, M at pos 2, O at pos 3, N at pos 4
            f.write(
                "MOUSE 22000 7.1\n"
            )  # M at pos 0, O at pos 1, U at pos 2, S at pos 3, E at pos 4

        # Initialize word manager with test file
        self.word_manager = WordManager(words_file=self.words_path)
        self.word_manager.set_test_mode(True)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_apply_single_constraint_green(self):
        """Test applying a single green (correct position) constraint."""
        # Test green E at position 4 (should match APPLE, GRAPE, MOUSE)
        result = self.word_manager.apply_single_constraint("RAISE", "GGGGB")
        expected = {"RAISE"}  # Only RAISE itself if it were in the word list
        # Since RAISE is not in our test set, let's test with actual words

        # Test with a word that gives us green letters
        result = self.word_manager.apply_single_constraint("APPLE", "GGGGG")
        expected = {"APPLE"}
        self.assertEqual(set(result), expected)

    def test_apply_single_constraint_yellow(self):
        """Test applying a single yellow (wrong position) constraint."""
        # Test yellow A at position 0 (A appears elsewhere but not at pos 0)
        # Use a guess that doesn't conflict with our expected results
        all_words = set(self.word_manager.all_words)
        # Use AZZZZ to test yellow A without conflicting black letters
        result = self.word_manager.apply_single_constraint("AZZZZ", "YBBBB")

        result_set = set(result)

        # Words with A not at position 0: DATES (A at pos 1), GRAPE (A at pos 2)
        # These should be in the result since they have A elsewhere and don't contain Z
        expected_words = {"DATES", "GRAPE"}
        for word in expected_words:
            self.assertIn(
                word,
                result_set,
                f"Word {word} should be in result for yellow A constraint",
            )

        # Verify that words with A at position 0 are excluded (APPLE)
        words_with_a_at_pos_0 = {
            word for word in all_words if len(word) > 0 and word[0] == "A"
        }
        for word in words_with_a_at_pos_0:
            self.assertNotIn(
                word,
                result_set,
                f"Word {word} should not be in result (A at position 0)",
            )

        # Verify that words without A are excluded
        words_without_a = {word for word in all_words if "A" not in word}
        for word in words_without_a:
            self.assertNotIn(
                word, result_set, f"Word {word} should not be in result (no A)"
            )

    def test_apply_single_constraint_black(self):
        """Test applying a single black (not in word) constraint."""
        # Test black Z (should match all words since none contain Z)
        result = self.word_manager.apply_single_constraint("ZEBRA", "BBBBB")
        # Since our test words don't contain Z, E, B, R, A combination,
        # let's test with a letter we know exists

        # Test black P - should exclude APPLE and GRAPE
        all_words = set(self.word_manager.all_words)
        result = self.word_manager.apply_single_constraint("PUDGE", "BBBBB")
        result_set = set(result)

        # The result should be a subset since we're filtering out words
        self.assertLessEqual(len(result_set), len(all_words))
        # Verify no words with P, U, D, G, E letters are in the result
        self.assertTrue(
            not any(letter in word for word in result_set for letter in "PUDGE")
        )

    def test_apply_multiple_constraints(self):
        """Test applying multiple constraints in sequence."""
        constraints = [
            (
                "TEARS",
                "BYBBB",
            ),  # T not in word, E in word but not pos 1, A,R,S not in word
            ("CLOUD", "BBBBB"),  # C,L,O,U,D not in word
        ]

        result = self.word_manager.apply_multiple_constraints(constraints)
        result_set = set(result)

        # Should progressively filter the word list
        self.assertLessEqual(len(result_set), len(self.word_manager.all_words))

        # Verify constraints are applied correctly
        for word in result_set:
            # Should not contain T, A, R, S, C, L, O, U, D
            forbidden_letters = set("TARSCLOUD")
            self.assertFalse(any(letter in word for letter in forbidden_letters))

    def test_get_words_matching_pattern(self):
        """Test getting words that match a specific pattern."""
        # Pattern: _A___ (A at position 1)
        pattern = {1: "A"}
        result = self.word_manager.get_words_matching_pattern(pattern)
        expected = {"DATES"}  # Only DATES has A at position 1
        self.assertEqual(set(result), expected)

        # Pattern: ___E_ (E at position 3)
        pattern = {3: "E"}
        result = self.word_manager.get_words_matching_pattern(pattern)
        expected = {"DATES", "ELDER", "HONEY"}  # Words with E at position 3
        self.assertEqual(set(result), expected)

    def test_get_words_containing_letters(self):
        """Test getting words that contain specific letters anywhere."""
        # Words containing both A and E
        letters = ["A", "E"]
        result = self.word_manager.get_words_containing_letters(letters)
        expected = {"APPLE", "DATES", "GRAPE"}  # Words containing both A and E
        self.assertEqual(set(result), expected)

    def test_get_words_excluding_letters(self):
        """Test getting words that exclude specific letters."""
        # Words not containing P or G
        letters = ["P", "G"]
        result = self.word_manager.get_words_excluding_letters(letters)
        # Should exclude APPLE, GRAPE, IGLOO
        excluded = {"APPLE", "GRAPE", "IGLOO"}
        result_set = set(result)
        self.assertTrue(excluded.isdisjoint(result_set))

    def test_get_words_with_yellow_constraints(self):
        """Test getting words with yellow letter constraints."""
        # E must be in word but not at position 1
        yellow_constraints = {1: ["E"]}
        result = self.word_manager.get_words_with_yellow_constraints(yellow_constraints)
        result_set = set(result)

        # Should include words with E but not at position 1
        for word in result_set:
            self.assertIn("E", word)  # Must contain E
            self.assertNotEqual(word[1], "E")  # But not at position 1

    def test_stateless_property(self):
        """Test that filtering operations don't modify the original word set."""
        original_word_count = len(self.word_manager.all_words)

        # Apply various filtering operations
        self.word_manager.apply_single_constraint("TESTS", "BBBBB")
        self.word_manager.apply_multiple_constraints([("ROUND", "BBBBB")])
        self.word_manager.get_words_matching_pattern({0: "A"})

        # Verify original word set is unchanged
        self.assertEqual(len(self.word_manager.all_words), original_word_count)
        self.assertIsNotNone(self.word_manager.all_words)

    def test_performance_with_large_constraints(self):
        """Test performance doesn't degrade with multiple constraints."""
        # This is more of a smoke test to ensure the implementation is efficient
        constraints = [
            ("TESTS", "BYBBY"),
            ("ROUND", "YBBYB"),
            ("FLING", "BBBBB"),
        ]

        # Should complete without timing out
        result = self.word_manager.apply_multiple_constraints(constraints)
        self.assertIsInstance(result, list)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Empty constraints
        result = self.word_manager.apply_multiple_constraints([])
        self.assertEqual(len(result), len(self.word_manager.all_words))

        # All black letters
        result = self.word_manager.apply_single_constraint("ZZZZZ", "BBBBB")
        # Should return all words since Z is not in any word
        self.assertGreater(len(result), 0)

        # All green letters (perfect match)
        result = self.word_manager.apply_single_constraint("APPLE", "GGGGG")
        self.assertEqual(result, ["APPLE"])


if __name__ == "__main__":
    unittest.main()
