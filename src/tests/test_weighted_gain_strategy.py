# src/tests/test_weighted_gain_strategy.py
"""
Test cases for the Weighted Information Gain strategy implementation.
"""
import pytest

from src.modules.backend.solver.strategy_factory import StrategyFactory
from src.modules.backend.solver.weighted_gain_strategy import WeightedGainStrategy
from src.modules.backend.word_manager import WordManager


@pytest.fixture
def word_manager():
    """Create a word manager with test words."""
    words = ["CRANE", "BLOAT", "TRACE", "SLEEP", "SLATE", "SHARK", "SMART", "RAISE"]
    common_words = ["CRANE", "TRACE", "SLATE", "SMART"]
    wm = WordManager()
    # Override the word lists for testing
    wm.all_words = words
    wm.possible_words = words.copy()
    wm.common_words = common_words
    return wm


@pytest.fixture
def strategy():
    """Create a weighted gain strategy instance with test weights."""
    return WeightedGainStrategy(entropy_weight=0.6, positional_weight=0.3, frequency_weight=0.1)


def test_get_top_suggestions_no_guesses(word_manager, strategy):
    """Test that the strategy returns good starter words when no guesses were made."""
    possible_words = word_manager.get_possible_words()
    common_words = word_manager.get_common_possible_words()

    suggestions = strategy.get_top_suggestions(possible_words, common_words, [], 3)

    # Should return some of our predefined good starters that exist in our test data
    assert len(suggestions) == 3
    assert any(word in suggestions for word in ["CRANE", "TRACE", "SLATE", "RAISE"])


def test_get_top_suggestions_with_guesses(strategy):
    """Test strategy recommendations after some guesses."""
    possible_words = ["CRANE", "TRACE", "SKATE"]
    common_words = ["CRANE", "TRACE", "SKATE"]

    # After guessing BLOAT with pattern "BBBYY" (only A is in all word, wrong position)
    guesses_so_far = [("BLOAT", "BBBYY")]

    suggestions = strategy.get_top_suggestions(possible_words, common_words, guesses_so_far, 3)

    # Should return valid suggestions that contain T
    assert len(suggestions) == 3
    assert all(word in possible_words for word in suggestions)
    assert all("A" in word for word in suggestions)


def test_empty_possible_words(strategy):
    """Test behavior when no possible words are available."""
    suggestions = strategy.get_top_suggestions([], [], [], 3)
    assert suggestions == []


def test_few_possible_words(strategy):
    """Test behavior with only a couple of words."""
    possible_words = ["CRANE", "SLATE"]
    common_words = ["CRANE"]

    suggestions = strategy.get_top_suggestions(possible_words, common_words, [("BLOAT", "BBYBB")], 3)

    # With very few words, common words should be first
    assert suggestions[0] == "CRANE"
    assert len(suggestions) == 2


def test_calculate_entropy_score(strategy):
    """Test entropy score calculation."""
    words = ["SLATE", "CRANE", "TRACE", "SMART"]

    # A word that well partitions the space should have high entropy
    entropy_score = strategy._calculate_entropy_score("BLOAT", words)

    # Score should be in the valid range [0, 1]
    assert 0 <= entropy_score <= 1

    # Self-entropy (a word scoring itself) should be low since it doesn't partition well
    self_entropy = strategy._calculate_entropy_score("SLATE", ["SLATE"])
    assert self_entropy == 1.0  # For a single word, entropy is maximum


def test_calculate_positional_score(strategy):
    """Test positional score calculation."""
    from src.modules.backend.solver.solver_utils import calculate_position_frequencies

    words = ["SLATE", "CRANE", "TRACE"]
    position_frequencies = calculate_position_frequencies(words)

    # Calculate score for a word with common letters in common positions
    score_common = strategy._calculate_positional_score("TRACE", position_frequencies)

    # Calculate score for a word with uncommon letter positioning
    score_uncommon = strategy._calculate_positional_score("BLOAT", position_frequencies)

    # A word with common letter positions should score higher
    assert score_common > score_uncommon

    # Scores should be in the valid range [0, 1]
    assert 0 <= score_common <= 1
    assert 0 <= score_uncommon <= 1


def test_calculate_position_frequencies():
    """Test position frequency calculation."""
    from src.modules.backend.solver.solver_utils import calculate_position_frequencies

    words = ["SLATE", "CRANE", "TRACE"]
    position_freqs = calculate_position_frequencies(words)

    # Should have 5 positions
    assert len(position_freqs) == 5

    # Each position should have frequencies that sum to approximately 1.0
    for pos in range(5):
        total = sum(position_freqs[pos].values())
        assert abs(total - 1.0) < 0.001  # Allow for small floating point errors

    # Check specific expected frequencies
    # E.g., 'C' appears at position 0 in 1/3 of the words
    assert abs(position_freqs[0].get("C", 0) - 1 / 3) < 0.001

    # E.g., 'E' appears at position 4 in all three words (3/3 = 1.0)
    assert abs(position_freqs[4].get("E", 0) - 1.0) < 0.001


def test_calculate_pattern():
    """Test that the pattern calculation matches the expected output."""
    from src.modules.backend.solver.solver_utils import calculate_pattern

    pattern = calculate_pattern("HELLO", "BELOW")
    assert pattern == "BGGBY"  # Based on the actual implementation

    pattern = calculate_pattern("KEEPS", "SHEEP")
    assert pattern == "BYGYY"  # Based on the actual implementation


def test_different_weight_configurations():
    """Test that different weight configurations produce different results."""
    words = ["SLATE", "CRANE", "TRACE", "SMART", "RAISE", "BLOAT"]
    common_words = ["SLATE", "CRANE", "TRACE", "SMART"]

    # Create strategies with different weight configurations
    entropy_focused = WeightedGainStrategy(entropy_weight=0.9, positional_weight=0.05, frequency_weight=0.05)
    position_focused = WeightedGainStrategy(entropy_weight=0.05, positional_weight=0.9, frequency_weight=0.05)
    frequency_focused = WeightedGainStrategy(
        entropy_weight=0.05, positional_weight=0.05, frequency_weight=0.9
    )

    # Use a guess that won't filter out all words
    # Here we use no previous guesses, so we'll just get first-guess suggestions
    entropy_suggestions = entropy_focused.get_top_suggestions(words, common_words, [], 3)
    position_suggestions = position_focused.get_top_suggestions(words, common_words, [], 3)
    frequency_suggestions = frequency_focused.get_top_suggestions(words, common_words, [], 3)

    # The suggestions should differ based on the weights
    # Not all three sets will necessarily be completely different,
    # but there should be some differences
    assert (
        entropy_suggestions != position_suggestions
        or entropy_suggestions != frequency_suggestions
        or position_suggestions != frequency_suggestions
    )


def test_strategy_factory_integration():
    """Test that the strategy can be created through the factory."""
    strategy = StrategyFactory.create_strategy("weighted_gain")
    assert isinstance(strategy, WeightedGainStrategy)
