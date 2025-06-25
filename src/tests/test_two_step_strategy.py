# src/tests/test_two_step_strategy.py
"""
Test cases for the Two-step Look-ahead strategy implementation.
"""
import pytest

from src.modules.backend.solver.strategy_factory import StrategyFactory
from src.modules.backend.solver.two_step_strategy import TwoStepStrategy
from src.modules.backend.word_manager import WordManager


@pytest.fixture
def word_manager():
    """Create a word manager with test words."""
    words = ["CRANE", "BLOAT", "TRACE", "SLEEP", "SLATE", "SHARK", "SONAR", "SMART"]
    common_words = ["CRANE", "TRACE", "SLATE", "SMART"]
    wm = WordManager()
    # Override the word lists for testing
    wm.all_words = words
    wm.possible_words = words.copy()
    wm.common_words = common_words
    return wm


@pytest.fixture
def strategy():
    """Create a two_step strategy instance."""
    return TwoStepStrategy(max_patterns_to_evaluate=3)  # Limited for testing


def test_get_top_suggestions_no_guesses(word_manager, strategy):
    """Test that the strategy returns good starter words when no guesses were made."""
    possible_words = word_manager.get_possible_words()
    common_words = word_manager.get_common_possible_words()

    suggestions = strategy.get_top_suggestions(possible_words, common_words, [], 3)

    # Should return some of our predefined good starters that exist in our test data
    assert len(suggestions) == 3
    assert any(word in suggestions for word in ["CRANE", "TRACE", "SLATE"])


def test_get_top_suggestions_with_guesses(strategy):
    """Test strategy recommendations after some guesses."""
    possible_words = ["CRANE", "TRACE", "SLATE"]
    common_words = ["CRANE", "TRACE", "SLATE"]

    # After guessing BLOAT with pattern "BBBBY" (only T is in the word, wrong position)
    guesses_so_far = [("BLOAT", "BBBBY")]

    suggestions = strategy.get_top_suggestions(possible_words, common_words, guesses_so_far, 3)

    # Should return valid suggestions that contain T
    assert len(suggestions) == 3
    assert all(word in possible_words for word in suggestions)


def test_empty_possible_words(strategy):
    """Test behavior when no possible words are available."""
    suggestions = strategy.get_top_suggestions([], [], [], 3)
    assert suggestions == []


def test_very_small_word_list(strategy):
    """Test behavior with only a couple of words."""
    possible_words = ["CRANE", "SLATE"]
    common_words = ["CRANE"]

    suggestions = strategy.get_top_suggestions(possible_words, common_words, [("BLOAT", "BBYBB")], 3)

    # With very few words, common words should be first
    assert suggestions[0] == "CRANE"
    assert len(suggestions) == 2


def test_group_by_pattern(strategy):
    """Test that words are correctly grouped by pattern."""
    answers = ["SLATE", "CRANE", "TRACE"]
    groups = strategy._group_by_pattern("SMART", answers)

    # Each word should produce a different pattern when guessed against "SMART"
    assert len(groups) == 3  # Each word should have its own pattern
    assert sum(len(words) for words in groups.values()) == 3  # All words accounted for


def test_calculate_entropy_from_groups(strategy):
    """Test entropy calculation from groups."""
    # Mock groups: perfectly split (best case)
    perfect_groups = {
        "pattern1": ["word1"],
        "pattern2": ["word2"],
        "pattern3": ["word3"],
    }

    # Uneven split (less informative)
    uneven_groups = {
        "pattern1": ["word1", "word2", "word3", "word4"],
        "pattern2": ["word5"],
    }

    perfect_entropy = strategy._calculate_entropy_from_groups(perfect_groups, 3)
    uneven_entropy = strategy._calculate_entropy_from_groups(uneven_groups, 5)

    # Perfect split should have higher entropy
    assert perfect_entropy > uneven_entropy


def test_two_step_score_calculation(strategy):
    """Test the two-step score calculation."""
    possible_answers = ["SLATE", "CRANE", "TRACE", "SMART"]
    common_words = ["SLATE", "CRANE", "TRACE", "SMART"]

    # Score should be better for words that effectively partition the answer space
    score = strategy._calculate_two_step_score("BLOAT", possible_answers, common_words)

    # Score should be in the valid range [0, 1]
    assert 0 <= score <= 1


def test_calculate_pattern():
    """Test that the pattern calculation matches the expected output."""
    from src.modules.backend.solver.solver_utils import calculate_pattern

    pattern = calculate_pattern("HELLO", "BELOW")
    assert pattern == "BGGBY"  # Based on the game rules and actual implementation

    pattern = calculate_pattern("KEEPS", "SHEEP")
    assert pattern == "BYGYY"  # Based on the game rules and actual implementation


def test_strategy_factory_integration():
    """Test that the strategy can be created through the factory."""
    strategy = StrategyFactory.create_strategy("two_step")
    assert isinstance(strategy, TwoStepStrategy)
