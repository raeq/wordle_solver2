# src/tests/test_minimax_strategy.py
"""
Test cases for the Minimax strategy implementation.
"""
import pytest

from src.modules.backend.solver.minimax_strategy import MinimaxStrategy
from src.modules.backend.solver.solver_utils import calculate_pattern
from src.modules.backend.word_manager import WordManager


@pytest.fixture
def word_manager():
    """Create a word manager with test words."""
    words = ["CRANE", "BLOAT", "TRACE", "SLEEP", "SLATE", "SHARK"]
    common_words = ["CRANE", "TRACE", "SLATE"]
    wm = WordManager()
    # Override the word lists for testing
    wm.all_words = words
    wm.possible_words = words.copy()
    wm.common_words = common_words
    return wm


@pytest.fixture
def strategy():
    """Create a minimax strategy instance."""
    return MinimaxStrategy()


def test_get_top_suggestions_no_guesses(word_manager, strategy):
    """Test that the strategy returns good starter words when no guesses were made."""
    possible_words = word_manager.get_possible_words()
    common_words = word_manager.get_common_possible_words()

    suggestions = strategy.get_top_suggestions(possible_words, common_words, [], 3)

    # Since CRANE, TRACE, and SLATE are in our test common words and are good starters,
    # they should be in the suggestions
    assert len(suggestions) == 3
    assert any(word in suggestions for word in ["CRANE", "TRACE", "SLATE"])


def test_get_top_suggestions_with_guesses(strategy):
    """Test strategy recommendations after some guesses."""
    possible_words = ["CRANE", "TRACE", "SLATE"]
    common_words = ["CRANE", "TRACE", "SLATE"]

    # After guessing BLOAT with pattern "BBBBY" (only T is in the word, wrong position)
    guesses_so_far = [("BLOAT", "BBBBY")]

    suggestions = strategy.get_top_suggestions(possible_words, common_words, guesses_so_far, 3)

    # All words have T, so they're all equally good from minimax perspective
    # But common words should be prioritized
    assert len(suggestions) == 3
    assert suggestions == ["CRANE", "TRACE", "SLATE"]


def test_empty_possible_words(strategy):
    """Test behavior when no possible words are available."""
    suggestions = strategy.get_top_suggestions([], [], [], 3)
    assert suggestions == []


def test_minimax_score_calculation(strategy):
    """Test the minimax score calculation."""
    possible_answers = ["SLATE", "CRANE", "TRACE"]

    # For "SLATE" with possible answers ["SLATE", "CRANE", "TRACE"]
    # - SLATE vs SLATE: "GGGGG" (1 word with this pattern)
    # - SLATE vs CRANE: "BBGBG" (1 word with this pattern)
    # - SLATE vs TRACE: "BBGYB" (1 word with this pattern)
    # Worst case: 1 word remains, score = 1
    score_slate = strategy._calculate_minimax_score("SLATE", possible_answers)

    # For "CRANE" with possible answers ["SLATE", "CRANE", "TRACE"]
    # - CRANE vs SLATE: "YYBBB" (1 word with this pattern)
    # - CRANE vs CRANE: "GGGGG" (1 word with this pattern)
    # - CRANE vs TRACE: "YGBBY" (1 word with this pattern)
    # Worst case: 1 word remains, score = 1
    score_crane = strategy._calculate_minimax_score("CRANE", possible_answers)

    # For "BLOAT" with possible answers ["SLATE", "CRANE", "TRACE"]
    # - BLOAT vs SLATE: "BYBBB" (1 word with this pattern)
    # - BLOAT vs CRANE: "BYBBB" (1 word with this pattern)
    # - BLOAT vs TRACE: "BBBBY" (1 word with this pattern)
    # Worst case: 1 word remains, score = 1
    score_bloat = strategy._calculate_minimax_score("BLOAT", possible_answers)

    # In this example, all words have unique patterns, so worst case is 1
    assert score_slate == 1
    assert score_crane == 1
    assert score_bloat == 1

    # Now let's test a case where patterns overlap
    possible_answers = ["SLATE", "SLANT", "SLAIN", "SLUMP"]

    # Create a specific case where we know patterns will overlap
    # For "EEEEE" with these answers:
    # - All words will give different patterns with "SLATE", "CRANE", etc.
    # - But with "EEEEE", we'll get:
    #   * EEEEE vs SLATE: "BYBBB" (E exists in SLATE)
    #   * EEEEE vs SLANT: "BYBBB" (E exists in SLANT)
    #   * EEEEE vs SLAIN: "BYBBB" (E exists in SLAIN)
    #   * EEEEE vs SLUMP: "BBBBB" (E doesn't exist in SLUMP)
    # So 3 words will share the same pattern, worst case is 3
    score_special = strategy._calculate_minimax_score("EEEEE", possible_answers)
    assert score_special > 1  # Multiple words would match the same pattern


def test_calculate_pattern_with_repeated_letters():
    """Test that the pattern calculation handles repeated letters correctly."""
    # Use the shared utility function directly instead of through the strategy
    # "HELLO" vs "BELOW"
    # H doesn't match
    # E matches at position 1
    # L is in wrong position (only mark one L as yellow since BELOW only has one L)
    # L is not matched after first L is accounted for
    # O matches at position 4
    pattern = calculate_pattern("HELLO", "BELOW")
    assert pattern == "BGGBY"  # B(H) G(E) G(L) B(L) Y(O)

    # "KEEPS" vs "SHEEP"
    # K doesn't match
    # E in wrong position for first E in KEEPS
    # E in wrong position for second E in SHEEP
    # P in wrong position
    # S doesn't match (S in SHEEP already used)
    pattern = calculate_pattern("KEEPS", "SHEEP")
    assert pattern == "BYGYY"  # Based on the game rules and previous tests


def test_minimax_strategy_prefers_low_worst_case():
    """Test that minimax strategy prefers words with lower worst-case scenarios."""
    strategy = MinimaxStrategy()

    # Create a scenario where one word has a better worst-case than others
    possible_words = ["APPLE", "HAPPY", "PAPER", "PARTY", "SMART", "GHOST"]
    common_words = ["APPLE", "PAPER", "SMART"]

    # Let's assume:
    # - Guessing "SMART" splits the words better than other words
    # This is a simplified test, real minimax would compute actual partitioning

    # Mock the _calculate_minimax_score method to return controlled values
    original_method = strategy._calculate_minimax_score

    try:
        # Monkey patch for testing
        def mock_score(candidate, answers):
            scores = {
                "SMART": 1,  # Good split - worst case only 1 word remains
                "GHOST": 3,  # Bad split - worst case 3 words remain
                "APPLE": 2,
                "HAPPY": 2,
                "PAPER": 2,
                "PARTY": 2,
            }
            return scores.get(candidate, 2)

        strategy._calculate_minimax_score = mock_score

        suggestions = strategy.get_top_suggestions(
            possible_words, common_words, [("BLAST", "BBBYB")], 3  # Some previous guess
        )

        # SMART should be first because it has the best worst-case scenario
        # and it's in the common words list
        assert "SMART" in suggestions
        assert suggestions.index("SMART") < suggestions.index("APPLE") if "APPLE" in suggestions else True

    finally:
        # Restore original method
        strategy._calculate_minimax_score = original_method
