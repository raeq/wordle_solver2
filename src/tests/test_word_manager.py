# src/tests/test_word_manager.py
"""
Unit tests for the WordManager class.
"""
import os
import tempfile
import unittest

from src.modules.backend.result_color import ResultColor
from src.modules.backend.word_manager import WordManager


class TestWordManager(unittest.TestCase):
    """Test cases for WordManager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary word file for testing
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a test words file in the new format: word frequency entropy
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

        # Initialize word manager with test file
        self.word_manager = WordManager(words_file=self.words_path)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_load_words(self):
        """Test that words are loaded correctly."""
        # With the new system, common words are automatically determined as top 30% by frequency
        # Top 30% of 10 words = 3 words (APPLE, FRUIT, GRAPE)
        self.assertEqual(len(self.word_manager.common_words), 3)
        self.assertEqual(len(self.word_manager.all_words), 10)
        self.assertEqual(len(self.word_manager.possible_words), 10)

        # Check that frequency and entropy data is loaded
        self.assertEqual(self.word_manager.get_word_frequency("APPLE"), 50000)
        self.assertAlmostEqual(
            self.word_manager.get_word_entropy("APPLE"), 5.2, places=1
        )

    def test_filter_words_green(self):
        """Test filtering words with green letters."""
        result_pattern = ResultColor.GREEN.value * 5  # "GGGGG"
        self.word_manager.filter_words("APPLE", result_pattern)
        self.assertEqual(len(self.word_manager.possible_words), 1)
        self.assertIn("APPLE", self.word_manager.possible_words)

    def test_filter_words_yellow(self):
        """Test filtering words with yellow letters."""
        # Enable test mode to bypass word validation
        self.word_manager._is_test_mode = True

        # Using P as a yellow letter with artificial characters that won't affect the test
        result_pattern = (
            ResultColor.YELLOW.value + ResultColor.BLACK.value * 4
        )  # "YBBBB"
        self.word_manager.filter_words("PXYZQ", result_pattern)

        # Should match words with P but not in first position
        possible = self.word_manager.get_possible_words()
        self.assertIn("APPLE", possible)  # P is in first position

        # Find a word in our test data that has P not in first position
        p_words = [
            word
            for word in self.word_manager.all_words
            if "P" in word and word[0] != "P"
        ]

        # If we have any such words in our test data, one should remain in the filtered list
        if p_words:
            self.assertTrue(
                any(word in possible for word in p_words),
                f"Expected at least one of {p_words} to pass the filter",
            )

    def test_filter_words_black(self):
        """Test filtering words with black letters."""
        # Enable test mode to bypass word validation
        self.word_manager._is_test_mode = True

        result_pattern = ResultColor.BLACK.value * 5  # "BBBBB"
        self.word_manager.filter_words("ZXCVB", result_pattern)
        # All original words should remain since none contain these letters
        self.assertEqual(len(self.word_manager.possible_words), 10)

    def test_reset(self):
        """Test resetting the word list."""
        result_pattern = ResultColor.GREEN.value * 5  # "GGGGG"
        self.word_manager.filter_words("APPLE", result_pattern)
        self.assertEqual(len(self.word_manager.possible_words), 1)

        self.word_manager.reset()
        self.assertEqual(len(self.word_manager.possible_words), 10)

    def test_is_valid_word(self):
        """Test checking if a word is valid."""
        self.assertTrue(self.word_manager.is_valid_word("APPLE"))
        self.assertTrue(
            self.word_manager.is_valid_word("apple")
        )  # Should be case-insensitive
        self.assertFalse(self.word_manager.is_valid_word("NOTAWORD"))


if __name__ == "__main__":
    unittest.main()
