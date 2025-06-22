# src/modules/tests/simple_test.py
"""
A simple demonstration of the Wordle Solver application with the new modular architecture.
This is not a formal unit test but rather a simple showcase of the modules working together.
"""
import sys
import os
from pathlib import Path

# Use relative imports instead of absolute imports
from ...modules.backend.word_manager import WordManager
from ...modules.backend.solver import Solver
from ...modules.backend.game_engine import GameEngine

def run_simple_test():
    """Run a simple test of the core components."""
    print("Starting simple test of Wordle Solver modules...")

    # Initialize word manager
    print("\n1. Testing WordManager...")
    word_manager = WordManager()
    all_words_count = len(word_manager.all_words)
    common_words_count = len(word_manager.common_words)
    print(f"   Loaded {all_words_count} total words and {common_words_count} common words")

    # Filter words with a sample guess
    print("\n   Testing word filtering...")
    initial_count = len(word_manager.possible_words)
    word_manager.filter_words("AUDIO", "BBYYB")
    filtered_count = len(word_manager.possible_words)
    print(f"   Filtered from {initial_count} to {filtered_count} words")

    # Reset word manager
    word_manager.reset()
    reset_count = len(word_manager.possible_words)
    print(f"   Reset filter - now have {reset_count} words")

    # Test solver
    print("\n2. Testing Solver...")
    solver = Solver(word_manager)
    suggestions = solver.get_top_suggestions(5)
    print(f"   Top 5 suggestions: {', '.join(suggestions)}")

    # Test adding a guess
    print("\n   Testing guess tracking...")
    solver.add_guess("ADIEU", "BBYYB")
    filtered_count = len(word_manager.possible_words)
    new_suggestions = solver.get_top_suggestions(5)
    print(f"   After guess: {filtered_count} possible words")
    print(f"   New top 5 suggestions: {', '.join(new_suggestions)}")

    # Test game engine
    print("\n3. Testing GameEngine...")
    game_engine = GameEngine(WordManager())  # Fresh word manager
    target = game_engine.start_new_game()
    print(f"   Started new game with target: {target}")

    # Make a sample guess
    try:
        result, is_solved = game_engine.make_guess(target[:4] + "X")  # Almost correct guess
        print(f"   Made guess: {target[:4] + 'X'}")
        print(f"   Result: {result}, Solved: {is_solved}")
    except ValueError:
        print("   Invalid guess (not in word list)")

    print("\nSimple test completed successfully!")

if __name__ == "__main__":
    run_simple_test()
