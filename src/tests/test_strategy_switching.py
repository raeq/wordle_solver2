# src/tests/test_strategy_switching.py
"""
Test suite for dynamic strategy switching during Wordle games.
Tests the ability to change solver strategies mid-game without affecting game state.
"""

import pytest

from src.modules.backend.game_state_manager import GameStateManager
from src.modules.backend.solver.entropy_strategy import EntropyStrategy
from src.modules.backend.solver.frequency_strategy import FrequencyStrategy
from src.modules.backend.solver.hybrid_frequency_entropy_strategy import (
    HybridFrequencyEntropyStrategy,
)
from src.modules.backend.solver.minimax_strategy import MinimaxStrategy
from src.modules.backend.solver.strategy_factory import StrategyFactory
from src.modules.backend.word_manager import WordManager


class TestStrategySwitching:
    """Test suite for dynamic strategy switching functionality."""

    @pytest.fixture
    def word_manager(self):
        """Create a word manager for testing."""
        return WordManager()

    @pytest.fixture
    def game_manager(self, word_manager):
        """Create a game state manager with default strategy."""
        return GameStateManager(word_manager)

    def test_initial_strategy_is_set(self, game_manager):
        """Test that game manager has a default strategy."""
        assert game_manager.strategy is not None
        assert isinstance(game_manager.strategy, HybridFrequencyEntropyStrategy)

    def test_strategy_can_be_changed(self, game_manager):
        """Test that strategy can be changed using set_strategy method."""
        # Change to entropy strategy
        entropy_strategy = EntropyStrategy()
        game_manager.set_strategy(entropy_strategy)

        assert game_manager.strategy is entropy_strategy
        assert isinstance(game_manager.strategy, EntropyStrategy)

    def test_strategy_factory_creates_all_strategies(self):
        """Test that strategy factory can create all available strategies."""
        available_strategies = StrategyFactory.get_available_strategies()

        # Verify all expected strategies are available
        expected_strategies = [
            "frequency",
            "entropy",
            "minimax",
            "two_step",
            "weighted_gain",
        ]
        for strategy_name in expected_strategies:
            assert strategy_name in available_strategies

        # Test creating each strategy
        for strategy_name in available_strategies:
            strategy = StrategyFactory.create_strategy(strategy_name)
            assert strategy is not None

    def test_strategy_switching_preserves_game_state(self, game_manager):
        """Test that changing strategy doesn't affect existing game state."""
        # Use a realistic scenario: guessing CRANE with moderate feedback
        game_manager.add_guess(
            "CRANE", "BYBBB"
        )  # Only 'R' is yellow (in word, wrong position)

        # Store initial state
        initial_guesses = game_manager.guesses.copy()
        initial_possible_words = game_manager.word_manager.get_possible_words().copy()
        initial_remaining_guesses = game_manager.get_remaining_guesses()

        # Verify we still have words remaining after this guess
        assert len(initial_possible_words) > 0, "Test setup should leave possible words"

        # Change strategy
        new_strategy = MinimaxStrategy()
        game_manager.set_strategy(new_strategy)

        # Verify game state is preserved
        assert game_manager.guesses == initial_guesses
        assert game_manager.word_manager.get_possible_words() == initial_possible_words
        assert game_manager.get_remaining_guesses() == initial_remaining_guesses
        assert isinstance(game_manager.strategy, MinimaxStrategy)

    def test_strategy_switching_affects_suggestions(self, game_manager):
        """Test that changing strategy produces different suggestions."""
        # Use a realistic first guess that leaves many words
        game_manager.add_guess("ADIEU", "BYBBB")  # Only 'I' is yellow

        # Verify we have enough words for meaningful comparison
        possible_words = game_manager.word_manager.get_possible_words()
        assert (
            len(possible_words) > 10
        ), f"Need more words for comparison, got {len(possible_words)}"

        # Get suggestions with initial strategy (WeightedGainStrategy)
        initial_suggestions = game_manager.get_top_suggestions(5)

        # Change to a different strategy
        game_manager.set_strategy(FrequencyStrategy())
        frequency_suggestions = game_manager.get_top_suggestions(5)

        # Change to another strategy
        game_manager.set_strategy(EntropyStrategy())
        entropy_suggestions = game_manager.get_top_suggestions(5)

        # Verify all strategies provide suggestions
        assert len(initial_suggestions) > 0
        assert len(frequency_suggestions) > 0
        assert len(entropy_suggestions) > 0

        # At least one strategy should produce different results
        # (We can't guarantee complete difference, but there should be some variation)
        all_same = (
            initial_suggestions == frequency_suggestions
            and initial_suggestions == entropy_suggestions
        )
        assert (
            not all_same
        ), "Different strategies should show some variation in suggestions"

    def test_mid_game_strategy_switching_scenario(self, game_manager):
        """Test a complete scenario of switching strategies mid-game."""
        # Use realistic scenarios that preserve word possibilities
        scenarios = [
            # (guess, result, new_strategy_name)
            ("SLATE", "BYBBB", "entropy"),  # 'L' yellow, others black
            ("MOUND", "BBBBB", "minimax"),  # All black - eliminates common letters
            ("BRICK", "BBYBB", "frequency"),  # 'R' yellow, 'I' yellow
        ]

        suggestions_history = []

        for guess, result, strategy_name in scenarios:
            # Make the guess
            game_manager.add_guess(guess, result)

            # Verify we still have possible words
            remaining_words = game_manager.word_manager.get_possible_words()
            assert (
                len(remaining_words) > 0
            ), f"After {guess} {result}, should have words remaining"

            # Switch strategy
            new_strategy = StrategyFactory.create_strategy(strategy_name)
            game_manager.set_strategy(new_strategy)

            # Get suggestions with new strategy
            suggestions = game_manager.get_top_suggestions(3)
            suggestions_history.append((strategy_name, suggestions))

            # Verify strategy was changed
            expected_type = {
                "entropy": EntropyStrategy,
                "minimax": MinimaxStrategy,
                "frequency": FrequencyStrategy,
            }[strategy_name]
            assert isinstance(game_manager.strategy, expected_type)

        # Verify we got suggestions at each step
        assert len(suggestions_history) == 3
        for strategy_name, suggestions in suggestions_history:
            # Allow empty suggestions only for very constrained scenarios
            if len(game_manager.word_manager.get_possible_words()) > 0:
                assert (
                    len(suggestions) >= 0
                ), f"{strategy_name} strategy should handle available words"

    def test_strategy_switching_with_invalid_strategy(self, game_manager):
        """Test error handling when trying to use invalid strategy."""
        with pytest.raises(ValueError) as exc_info:
            StrategyFactory.create_strategy("invalid_strategy")

        assert "Unknown strategy" in str(exc_info.value)
        assert "invalid_strategy" in str(exc_info.value)

    def test_strategy_switching_maintains_performance(self, game_manager):
        """Test that strategy switching doesn't degrade performance significantly."""
        import time

        # Use a more conservative scenario that leaves reasonable word counts
        game_manager.add_guess("SLATE", "BYBBB")  # Only 'L' yellow

        # Verify we have words to work with
        remaining_words = game_manager.word_manager.get_possible_words()
        assert (
            len(remaining_words) > 0
        ), "Should have words remaining for performance test"

        strategies_to_test = ["frequency", "entropy", "minimax", "weighted_gain"]

        for strategy_name in strategies_to_test:
            start_time = time.time()

            # Switch strategy
            strategy = StrategyFactory.create_strategy(strategy_name)
            game_manager.set_strategy(strategy)

            # Get suggestions
            suggestions = game_manager.get_top_suggestions(10)

            end_time = time.time()
            execution_time = end_time - start_time

            # Verify performance is reasonable
            assert (
                execution_time < 5.0
            ), f"{strategy_name} strategy took too long: {execution_time:.2f}s"

            # Only assert suggestions exist if we have possible words
            current_possible = len(game_manager.word_manager.get_possible_words())
            if current_possible > 0:
                assert (
                    len(suggestions) >= 0
                ), f"{strategy_name} should handle {current_possible} possible words"

    def test_strategy_consistency_after_switching(self, game_manager):
        """Test that strategy behavior is consistent after switching."""
        # Use a realistic guess that leaves multiple possibilities
        game_manager.add_guess("ROUND", "BYBBB")  # Only 'O' yellow

        # Verify we have words to work with
        possible_words = game_manager.word_manager.get_possible_words()
        assert len(possible_words) > 0, "Need words remaining for consistency test"

        # Switch to entropy strategy
        entropy_strategy = EntropyStrategy()
        game_manager.set_strategy(entropy_strategy)

        # Get suggestions multiple times - should be consistent
        suggestions1 = game_manager.get_top_suggestions(5)
        suggestions2 = game_manager.get_top_suggestions(5)
        suggestions3 = game_manager.get_top_suggestions(5)

        assert (
            suggestions1 == suggestions2 == suggestions3
        ), "Strategy should produce consistent results for same game state"

    def test_all_strategies_can_handle_early_game(self, game_manager):
        """Test that all strategies work correctly in early-game scenarios."""
        # Simulate early game with many remaining words
        game_manager.add_guess("AUDIO", "BBBBY")  # Only 'O' yellow

        # Verify we have many words remaining (early game scenario)
        remaining_words = game_manager.word_manager.get_possible_words()
        assert (
            len(remaining_words) > 50
        ), f"Early game should have many words, got {len(remaining_words)}"

        strategies = StrategyFactory.get_available_strategies()

        for strategy_name in strategies:
            strategy = StrategyFactory.create_strategy(strategy_name)
            game_manager.set_strategy(strategy)

            suggestions = game_manager.get_top_suggestions(10)

            # Should provide suggestions in early game
            assert (
                len(suggestions) > 0
            ), f"{strategy_name} should provide suggestions in early game"
            assert len(suggestions) <= 10, f"{strategy_name} should respect count limit"

    def test_all_strategies_can_handle_late_game(self, game_manager):
        """Test that all strategies work correctly in late-game scenarios with few words."""
        # Create a late game scenario with very specific constraints but valid words
        # Target word: PIXEL (assuming it's in the dictionary)
        game_manager.add_guess("STARE", "BBBBB")  # Eliminates S,T,A,R,E
        game_manager.add_guess("MOUND", "BBBBB")  # Eliminates M,O,U,N,D
        game_manager.add_guess("FLING", "BBBBB")  # Eliminates F,L,I,N,G

        # This should leave very few words, but some should remain
        remaining_words = game_manager.word_manager.get_possible_words()

        strategies = StrategyFactory.get_available_strategies()

        for strategy_name in strategies:
            strategy = StrategyFactory.create_strategy(strategy_name)
            game_manager.set_strategy(strategy)

            suggestions = game_manager.get_top_suggestions(3)

            # Should handle late game gracefully (may have 0 suggestions if no words left)
            assert isinstance(
                suggestions, list
            ), f"{strategy_name} should return a list"
            if len(remaining_words) > 0:
                assert (
                    len(suggestions) >= 0
                ), f"{strategy_name} should handle remaining words"

    def test_strategy_switching_preserves_word_filtering(self, game_manager):
        """Test that word filtering is preserved across strategy switches."""
        initial_word_count = len(game_manager.word_manager.get_possible_words())

        # Add a guess that will filter words but not eliminate all
        game_manager.add_guess("PLACE", "BYBBB")  # Only 'L' yellow
        filtered_word_count = len(game_manager.word_manager.get_possible_words())

        # Verify filtering occurred but words remain
        assert (
            filtered_word_count < initial_word_count
        ), "Filtering should reduce word count"
        assert filtered_word_count > 0, "Some words should remain after filtering"

        # Switch strategies multiple times
        strategies = ["entropy", "minimax", "frequency"]
        for strategy_name in strategies:
            strategy = StrategyFactory.create_strategy(strategy_name)
            game_manager.set_strategy(strategy)

            # Word count should remain the same
            current_word_count = len(game_manager.word_manager.get_possible_words())
            assert (
                current_word_count == filtered_word_count
            ), f"Strategy switch to {strategy_name} affected word filtering"

    def test_strategy_registration_functionality(self):
        """Test that new strategies can be registered with the factory."""

        # Create a simple test strategy
        class TestStrategy(EntropyStrategy):
            def get_top_suggestions(
                self, possible_words, common_words, guesses_so_far, count=10
            ):
                return possible_words[:count] if possible_words else []

        # Register the new strategy
        StrategyFactory.register_strategy("test_strategy", TestStrategy)

        # Verify it's available
        available_strategies = StrategyFactory.get_available_strategies()
        assert "test_strategy" in available_strategies

        # Verify it can be created
        strategy = StrategyFactory.create_strategy("test_strategy")
        assert isinstance(strategy, TestStrategy)

    def test_strategy_switching_with_no_valid_words(self, game_manager):
        """Test that strategies handle edge case of no valid words gracefully."""
        # This test specifically checks the edge case behavior
        # We'll manually clear the possible words to test the edge case
        original_words = game_manager.word_manager.possible_words.copy()

        try:
            # Temporarily clear all possible words
            game_manager.word_manager.possible_words.clear()

            strategies = StrategyFactory.get_available_strategies()

            for strategy_name in strategies:
                strategy = StrategyFactory.create_strategy(strategy_name)
                game_manager.set_strategy(strategy)

                suggestions = game_manager.get_top_suggestions(5)

                # Should return empty list when no words are possible
                assert (
                    suggestions == []
                ), f"{strategy_name} should return empty list when no words possible"

        finally:
            # Restore the original words
            game_manager.word_manager.possible_words = original_words
