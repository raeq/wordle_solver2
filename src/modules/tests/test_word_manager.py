# src/modules/tests/test_word_manager.py
"""
Unit tests for the WordManager class.
"""
import unittest
import os
import tempfile

from ..backend.word_manager import WordManager
from ..backend.result_color import ResultColor


class TestWordManager(unittest.TestCase):
    """Test cases for WordManager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary word files for testing
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create a test common words file with only 5-letter words
        self.common_words_path = os.path.join(self.temp_dir.name, "common_words.txt")
        with open(self.common_words_path, "w") as f:
            f.write("APPLE\nDATES\nELDER\nFRUIT\nGRAPE\n")

        # Create a test all words file with only 5-letter words
        self.all_words_path = os.path.join(self.temp_dir.name, "words.txt")
        with open(self.all_words_path, "w") as f:
            f.write(
                "APPLE\nDATES\nELDER\nFRUIT\nGRAPE\nHONEY\nIGLOO\nJELLY\nLIMON\nMOUSE\n"
            )

        # Initialize word manager with test files
        self.word_manager = WordManager(
            common_words_file=self.common_words_path, all_words_file=self.all_words_path
        )

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_load_words(self):
        """Test that words are loaded correctly."""
        self.assertEqual(len(self.word_manager.common_words), 5)
        self.assertEqual(len(self.word_manager.all_words), 10)
        self.assertEqual(len(self.word_manager.possible_words), 10)

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
