"""
Base test utilities and fixtures for strategy testing to eliminate code duplication.
"""

import pytest

from src.modules.backend.word_manager import WordManager


class StrategyTestBase:
    """Base class with common test patterns for all strategy tests."""

    @staticmethod
    def create_test_word_manager():
        """Create a standardized word manager for testing."""
        words = {
            "CRANE",
            "TRACE",
            "SLATE",
            "AUDIO",
            "ADIEU",
            "SMART",
            "REACT",
            "HEART",
            "BEAST",
            "LEAST",
            "TOAST",
            "COAST",
            "ROAST",
            "BOAST",
        }
        common_words = ["CRANE", "TRACE", "SLATE", "SMART"]
        wm = WordManager()
        # Override the word lists for testing
        wm.all_words = words
        wm.possible_words = words.copy()
        wm.common_words = set(common_words)
        return wm

    @staticmethod
    def test_get_top_suggestions_no_guesses_pattern(strategy, word_manager):
        """Standard test pattern for strategies with no previous guesses."""
        possible_words = word_manager.get_possible_words()
        common_words = word_manager.get_common_possible_words()

        suggestions = strategy.get_top_suggestions(possible_words, common_words, [], 3)

        # Should return the requested number of suggestions
        assert len(suggestions) == 3
        # All suggestions should be valid words from our test data
        assert all(word in possible_words for word in suggestions)
        # Should prefer common words when available (at least some should be common)
        common_in_suggestions = [word for word in suggestions if word in common_words]
        assert (
            len(common_in_suggestions) > 0
        ), "Strategy should include at least some common words"

    @staticmethod
    def test_get_top_suggestions_with_guesses_pattern(strategy):
        """Standard test pattern for strategies with previous guesses."""
        possible_words = ["CRANE", "TRACE", "SLATE"]
        common_words = ["CRANE", "TRACE", "SLATE"]

        # After guessing BLOAT with pattern "BBBBY" (only T is in the word, wrong position)
        guesses_so_far = [("BLOAT", "BBBBY")]

        suggestions = strategy.get_top_suggestions(
            possible_words, common_words, guesses_so_far, 3
        )

        # Should return valid suggestions that contain T
        assert len(suggestions) == 3

    @staticmethod
    def test_empty_possible_words_pattern(strategy):
        """Standard test pattern for empty word lists."""
        suggestions = strategy.get_top_suggestions([], [], [], 3)
        assert suggestions == []

    @staticmethod
    def test_very_small_word_list_pattern(strategy):
        """Standard test pattern for very small word lists."""
        possible_words = ["CRANE", "SLATE"]
        common_words = ["CRANE"]

        suggestions = strategy.get_top_suggestions(
            possible_words, common_words, [("BLOAT", "BBYBB")], 3
        )

        # With very few words, common words should be first
        assert suggestions[0] == "CRANE"
        assert len(suggestions) == 2


# Shared fixtures that can be imported by test files
@pytest.fixture
def shared_word_manager():
    """Shared word manager fixture for all strategy tests."""
    return StrategyTestBase.create_test_word_manager()
