# src/tests/test_weighted_gain_strategy.py
"""
Unit tests for the WeightedGainStrategy class.
"""
import pytest

from src.modules.backend.solver.weighted_gain_strategy import WeightedGainStrategy

from .test_strategy_base import StrategyTestBase


@pytest.fixture
def word_manager():
    """Create a word manager for testing."""
    return StrategyTestBase.create_test_word_manager()


@pytest.fixture
def strategy():
    """Create a weighted gain strategy instance with test weights."""
    return WeightedGainStrategy(
        entropy_weight=0.5, positional_weight=0.3, frequency_weight=0.2
    )


def test_get_top_suggestions_no_guesses(word_manager, strategy):
    """Test that the strategy returns good starter words when no guesses were made."""
    StrategyTestBase.test_get_top_suggestions_no_guesses_pattern(strategy, word_manager)


def test_get_top_suggestions_with_guesses(strategy):
    """Test strategy recommendations after some guesses."""
    StrategyTestBase.test_get_top_suggestions_with_guesses_pattern(strategy)


def test_empty_possible_words(strategy):
    """Test behavior when no possible words are available."""
    StrategyTestBase.test_empty_possible_words_pattern(strategy)


def test_few_possible_words(strategy):
    """Test behavior with only a couple of words."""
    StrategyTestBase.test_very_small_word_list_pattern(strategy)
