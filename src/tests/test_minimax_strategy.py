# src/tests/test_minimax_strategy.py
"""
Unit tests for the MinimaxStrategy class.
"""
import pytest

from src.modules.backend.solver.minimax_strategy import MinimaxStrategy

from .test_strategy_base import StrategyTestBase


@pytest.fixture
def word_manager():
    """Create a word manager for testing."""
    return StrategyTestBase.create_test_word_manager()


@pytest.fixture
def strategy():
    """Create a minimax strategy instance."""
    return MinimaxStrategy()


def test_get_top_suggestions_no_guesses(word_manager, strategy):
    """Test that the strategy returns good starter words when no guesses were made."""
    StrategyTestBase.test_get_top_suggestions_no_guesses_pattern(strategy, word_manager)


def test_get_top_suggestions_with_guesses(strategy):
    """Test strategy recommendations after some guesses."""
    StrategyTestBase.test_get_top_suggestions_with_guesses_pattern(strategy)


def test_empty_possible_words(strategy):
    """Test behavior when no possible words are available."""
    StrategyTestBase.test_empty_possible_words_pattern(strategy)
