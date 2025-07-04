# src/tests/simple_test.py
"""
A simple demonstration of the Wordle Solver application with the new modular architecture.
This is not a formal unit test but rather a simple showcase of the modules working together.
"""

# Use absolute imports instead of relative imports
from src.modules.backend.game_engine import GameEngine
from src.modules.backend.solver.strategy_factory import StrategyFactory
from src.modules.backend.stateless_word_manager import StatelessWordManager


def run_simple_test():
    """Run a simple test of the core components."""
    print("Starting simple test of Wordle Solver modules...")

    # Initialize word manager
    print("\n1. Testing WordManager...")
    word_manager = StatelessWordManager()  # Using StatelessWordManager now
    word_manager._is_test_mode = True  # Enable test mode
    all_words_count = len(word_manager.all_words)
    common_words_count = len(word_manager.common_words)
    print(
        f"   Loaded {all_words_count} total words and {common_words_count} common words"
    )

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

    # Test strategy factory
    print("\n2. Testing StrategyFactory...")
    strategy = StrategyFactory.create_strategy("frequency")
    suggestions = strategy.get_top_suggestions(
        list(word_manager.possible_words), list(word_manager.common_words), [], 5
    )
    print(f"   Top 5 suggestions: {', '.join(suggestions)}")

    # Test adding a guess effect
    print("\n   Testing guess filtering...")
    word_manager.filter_words("ADIEU", "BBYYB")
    filtered_count = len(word_manager.possible_words)
    new_suggestions = strategy.get_top_suggestions(
        list(word_manager.possible_words),
        list(word_manager.common_words),
        [("ADIEU", "BBYYB")],
        5,
    )
    print(f"   After guess: {filtered_count} possible words")
    print(f"   New top 5 suggestions: {', '.join(new_suggestions)}")

    # Test game engine
    print("\n3. Testing GameEngine...")
    game_engine = GameEngine()  # GameEngine now creates its own WordManager
    game_engine.word_manager._is_test_mode = (
        True  # Set test mode for internal WordManager
    )
    target = game_engine.start_new_game()
    print(f"   Started new game with target: {target}")

    # Make a sample guess
    try:
        result, is_solved = game_engine.make_guess(
            target[:4] + "X"
        )  # Almost correct guess
        print(f"   Made guess: {target[:4] + 'X'}")
        print(f"   Result: {result}, Solved: {is_solved}")
    except ValueError:
        print("   Invalid guess (not in word list)")

    print("\nSimple test completed successfully!")


if __name__ == "__main__":
    run_simple_test()
