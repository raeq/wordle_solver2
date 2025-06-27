# src/tests/test_two_step_strategy.py
"""
Unit tests for the TwoStepStrategy class.
"""
import pytest

from src.modules.backend.solver.two_step_strategy import TwoStepStrategy

from .test_strategy_base import StrategyTestBase


@pytest.fixture
def word_manager():
    """Create a word manager for testing."""
    return StrategyTestBase.create_test_word_manager()


@pytest.fixture
def strategy():
    """Create a two_step strategy instance."""
    return TwoStepStrategy()


def test_get_top_suggestions_no_guesses(word_manager, strategy):
    """Test that the strategy returns good starter words when no guesses were made."""
    StrategyTestBase.test_get_top_suggestions_no_guesses_pattern(strategy, word_manager)


def test_get_top_suggestions_with_guesses(strategy):
    """Test strategy recommendations after some guesses."""
    StrategyTestBase.test_get_top_suggestions_with_guesses_pattern(strategy)


def test_empty_possible_words(strategy):
    """Test behavior when no possible words are available."""
    StrategyTestBase.test_empty_possible_words_pattern(strategy)


def test_very_small_word_list(strategy):
    """Test behavior with only a couple of words."""
    StrategyTestBase.test_very_small_word_list_pattern(strategy)
