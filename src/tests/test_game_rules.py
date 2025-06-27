#!/usr/bin/env python3
# src/tests/test_game_rules.py
"""
Test suite specifically designed to verify the implementation of game rules
as specified in GameRules.md.

This covers all test cases mentioned in the documentation as well as additional
edge cases to ensure complete coverage of the game rule logic.
"""

import pytest

from src.modules.backend.exceptions import (
    InputLengthError,
    InvalidGuessError,
)
from src.modules.backend.game_engine import GameEngine
from src.modules.backend.word_manager import WordManager


class TestGameRules:
    """Tests to verify that the game implementation follows GameRules.md"""

    @pytest.fixture
    def game_engine(self):
        """Create a test game engine with a word manager in test mode"""
        word_manager = WordManager()
        word_manager._is_test_mode = True
        game = GameEngine(word_manager)
        game.start_new_game()
        # Override the random target word for testing
        game.target_word = "TESTS"  # Default target word
        return game

    def test_basic_rules(self, game_engine):
        """Test basic game functionality"""
        # Game should start active
        assert game_engine.game_active is True

        # Player should have 6 guesses
        assert game_engine.max_guesses == 6
        assert game_engine.get_remaining_guesses() == 6

        # After one guess, 5 guesses should remain
        result, _ = game_engine.make_guess("START")
        assert game_engine.get_remaining_guesses() == 5

    def test_case_insensitivity(self, game_engine):
        """Test that case doesn't matter as specified in the rules"""
        # Set a specific target word
        game_engine.target_word = "CHAIR"

        # Try lowercase
        result_lower, is_solved_lower = game_engine.make_guess("chair")
        assert result_lower == "GGGGG"
        assert is_solved_lower is True

        # Reset game for uppercase test
        game_engine.start_new_game()
        game_engine.target_word = "CHAIR"

        # Try mixed case
        result_mixed, is_solved_mixed = game_engine.make_guess("ChAiR")
        assert result_mixed == "GGGGG"
        assert is_solved_mixed is True

    def test_error_conditions(self, game_engine):
        """Test error conditions specified in the rules"""
        # Test with too short word
        with pytest.raises(InputLengthError):
            game_engine.make_guess("ABC")

        # Test with too long word
        with pytest.raises(InputLengthError):
            game_engine.make_guess("TOOLONG")

        # Test with non-alphabetic characters
        with pytest.raises(InvalidGuessError):
            game_engine.make_guess("TE$TS")

    def test_winning_conditions(self, game_engine):
        """Test winning conditions"""
        game_engine.target_word = "TESTS"

        # Game not won yet
        assert game_engine.is_game_won() is False

        # Win the game
        result, is_solved = game_engine.make_guess("TESTS")
        assert result == "GGGGG"
        assert is_solved is True
        assert game_engine.is_game_won() is True
        assert game_engine.is_game_over() is True
        assert game_engine.game_active is False

    def test_losing_conditions(self, game_engine):
        """Test losing conditions"""
        game_engine.target_word = "TESTS"

        # Make 6 incorrect guesses
        for _ in range(6):
            game_engine.make_guess("WRONG")

        # Game should be over but not won
        assert game_engine.is_game_won() is False
        assert game_engine.is_game_over() is True
        assert game_engine.game_active is False

    # Now testing the specific test cases from GameRules.md

    def test_case1_no_letters_match(self, game_engine):
        """Test Case 1: No Letters Match"""
        game_engine.target_word = "FOUND"
        result, _ = game_engine.make_guess("APPLE")
        assert result == "BBBBB"

    def test_case2_all_letters_match(self, game_engine):
        """Test Case 2: All Letters Match"""
        game_engine.target_word = "CHAIR"
        result, _ = game_engine.make_guess("CHAIR")
        assert result == "GGGGG"

    def test_case3_some_letters_match(self, game_engine):
        """Test Case 3: Some Letters Match"""
        game_engine.target_word = "PLACE"
        result, _ = game_engine.make_guess("PLANT")
        assert result == "GGGBB"

    def test_case4_letters_wrong_position(self, game_engine):
        """Test Case 4: Letters in the wrong position"""
        game_engine.target_word = "LACEY"
        result, _ = game_engine.make_guess("TRACE")
        assert result == "BBYYY"

    def test_case5_repeat_in_hidden_not_in_guess(self, game_engine):
        """Test Case 5: Repeat letters in Hidden word but no repeats in guess"""
        game_engine.target_word = "APPLE"
        result, _ = game_engine.make_guess("RIPEN")
        assert result == "BBGYB"

    def test_case6_repeat_in_guess_not_in_hidden(self, game_engine):
        """Test Case 6: Repeat letters in guess word but no repeats in hidden word"""
        game_engine.target_word = "RIPEN"
        result, _ = game_engine.make_guess("APPLE")
        assert result == "BBGBY"

    def test_case7_repeat_in_both(self, game_engine):
        """Test Case 7: Repeat letters in guess word and repeats in hidden word"""
        game_engine.target_word = "ERASE"
        result, _ = game_engine.make_guess("SAREE")
        assert result == "YYYYG"

    def test_case8_all_letters_wrong_position(self, game_engine):
        """Test Case 8: All letters in guess exist in hidden word but not in the correct position"""
        game_engine.target_word = "STARE"
        result, _ = game_engine.make_guess("RATES")
        assert result == "YYYYY"

    # Additional test cases to cover edge cases not specifically in GameRules.md

    def test_example2_annal_banal(self, game_engine):
        """Test the specific example from rules: ANNAL vs BANAL"""
        game_engine.target_word = "BANAL"
        result, _ = game_engine.make_guess("ANNAL")
        assert result == "YBGGG"

    def test_example3_union_banal(self, game_engine):
        """Test the specific example from rules: UNION vs BANAL"""
        game_engine.target_word = "BANAL"
        result, _ = game_engine.make_guess("UNION")
        assert result == "BYBBB"

    def test_triple_letter_in_target(self, game_engine):
        """Test case with triple letter in target word"""
        game_engine.target_word = "BELLE"  # Double L, double E
        result, _ = game_engine.make_guess(
            "LABEL"
        )  # Has L, E, B but not all in right positions
        assert result == "YBYYY"

    def test_triple_letter_in_guess(self, game_engine):
        """Test case with triple letter in guess word"""
        game_engine.target_word = "BAKER"
        result, _ = game_engine.make_guess("LULLS")  # Triple L, target has none
        assert result == "BBBBB"

    def test_completely_different_words_same_letters(self, game_engine):
        """Test with words that share the same letters but in different positions"""
        game_engine.target_word = "BROAD"
        result, _ = game_engine.make_guess("BOARD")  # Same letters, different order
        assert result == "GYYYG"

    def test_complex_duplicate_handling(self, game_engine):
        """Complex test for handling of duplicate letters"""
        game_engine.target_word = "ALLOY"

        # 'LLAMA' has double 'L', target has double 'L'
        result, _ = game_engine.make_guess("LLAMA")
        # First L is green (correct position), second L is yellow (target has another L)
        assert result == "YGYBB"

        # Another example with 'HELLO', target still 'ALLOY'
        result, _ = game_engine.make_guess("HELLO")
        # L's are yellow (target has L but wrong position), O is green
        assert result == "BBGYY"

    def test_special_edge_cases(self, game_engine):
        """Test special edge cases that might challenge the algorithm"""
        # Case: Target with all same letters
        game_engine.target_word = "EEEEE"
        result, _ = game_engine.make_guess("TREND")
        # Only the 'E' in TREND matches and should be yellow
        assert result == "BBGBB"

        # Case: Guess with all same letters, target has some
        game_engine.target_word = "BEAST"
        result, _ = game_engine.make_guess("EEEEE")
        # Only one E in target, should mark just one yellow
        assert result == "BGBBB"

    def test_algorithm_consistency(self, game_engine):
        """Test that the algorithm follows the pseudocode in GameRules.md"""
        # This is a meta-test to ensure the algorithm works according to the rules
        # For this we'll test a complex case that requires the exact two-pass algorithm

        game_engine.target_word = "AAABB"
        result, _ = game_engine.make_guess("BBAAA")

        # Expected result according to the algorithm:
        # First pass: positions 3,4,5 get G (B,A,A are green)
        # Second pass: positions 1,2 get Y (B,B are yellow)
        # Result: YYGGG
        assert result == "YYGYY"

    def test_multiple_guesses_sequence(self, game_engine):
        """Test a sequence of multiple guesses leading to a win"""
        game_engine.target_word = "BROWN"

        # First guess - one match
        result1, is_solved1 = game_engine.make_guess("BREAK")
        assert result1 == "GGBBB"
        assert is_solved1 is False

        # Second guess - more matches
        result2, is_solved2 = game_engine.make_guess("GROWN")
        assert result2 == "BGGGG"
        assert is_solved2 is False

        # Third guess - win
        result3, is_solved3 = game_engine.make_guess("BROWN")
        assert result3 == "GGGGG"
        assert is_solved3 is True

        # Game should be over
        assert game_engine.is_game_over() is True
