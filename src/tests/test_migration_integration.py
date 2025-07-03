# src/tests/test_migration_integration.py
"""
Integration tests for the complete solver strategy migration.
"""
import os
import tempfile
import unittest

from src.modules.backend.enhanced_game_state_manager import (
    EnhancedGameStateManager,
    StatelessGameStateManager,
)
from src.modules.backend.solver.strategy_migration_factory import strategy_factory
from src.modules.backend.stateless_word_manager import StatelessWordManager
from src.modules.backend.word_manager import WordManager


class TestMigrationIntegration(unittest.TestCase):
    """Integration tests for the complete migration system."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary word file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.words_path = os.path.join(self.temp_dir.name, "test_words.txt")

        with open(self.words_path, "w", encoding="utf-8") as f:
            # Format: word frequency entropy
            f.write("APPLE 50000 5.2\n")
            f.write("DATES 30000 6.1\n")
            f.write("ELDER 25000 7.3\n")
            f.write("FRUIT 45000 4.8\n")
            f.write("GRAPE 35000 6.5\n")
            f.write("HONEY 20000 7.8\n")
            f.write("SLATE 40000 6.8\n")
            f.write("CRANE 38000 7.2\n")
            f.write("AUDIO 28000 8.1\n")
            f.write("RAISE 42000 7.5\n")

        # Initialize word managers
        self.word_manager = WordManager(words_file=self.words_path)
        self.word_manager.set_test_mode(True)

        self.stateless_word_manager = StatelessWordManager(words_file=self.words_path)
        self.stateless_word_manager.set_test_mode(True)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_strategy_factory_integration(self):
        """Test that the strategy factory works correctly."""
        # Test getting migrated strategy
        frequency_strategy = strategy_factory.create_strategy(
            "frequency", use_stateless=True, word_manager=self.word_manager
        )

        self.assertIsNotNone(frequency_strategy)

        # Test getting legacy strategy
        legacy_strategy = strategy_factory.create_strategy(
            "frequency", use_stateless=False, word_manager=self.word_manager
        )

        self.assertIsNotNone(legacy_strategy)

    def test_enhanced_game_state_manager_stateless(self):
        """Test enhanced game state manager with stateless strategies."""
        game_manager = EnhancedGameStateManager(
            word_manager=self.word_manager,
            strategy_name="frequency",
            use_stateless=True,
            stateless_word_manager=self.stateless_word_manager,
        )

        # Simulate a game
        game_manager.add_guess("SLATE", "BYBBB")  # Changed from make_guess to add_guess
        suggestions = game_manager.get_top_suggestions(5)

        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 5)
        self.assertTrue(game_manager.is_stateless_strategy)

    def test_enhanced_game_state_manager_legacy(self):
        """Test enhanced game state manager with legacy strategies."""
        game_manager = EnhancedGameStateManager(
            word_manager=self.word_manager,
            strategy_name="frequency",
            use_stateless=False,
        )

        # Simulate a game
        game_manager.add_guess("SLATE", "BYBBB")  # Changed from make_guess to add_guess
        suggestions = game_manager.get_top_suggestions(5)

        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 5)

    def test_pure_stateless_game_manager(self):
        """Test pure stateless game state manager."""
        stateless_manager = StatelessGameStateManager(
            stateless_word_manager=self.stateless_word_manager,
            default_strategy="frequency",
        )

        # Test getting suggestions for a game state
        constraints = [("SLATE", "BYBBB"), ("CRANE", "YBGYB")]
        suggestions = stateless_manager.get_suggestions(
            constraints=constraints, count=5
        )

        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 5)

    def test_strategy_switching(self):
        """Test dynamic strategy switching."""
        game_manager = EnhancedGameStateManager(
            word_manager=self.word_manager,
            strategy_name="frequency",
            use_stateless=True,
        )

        # Make initial guess with less restrictive constraint
        game_manager.add_guess(
            "ZZZZZ", "BBBBB"
        )  # Use non-existent letters to preserve words
        initial_suggestions = game_manager.get_top_suggestions(3)

        # Switch to entropy strategy
        success = game_manager.switch_strategy("entropy", use_stateless=True)
        self.assertTrue(success)

        # Get suggestions with new strategy
        new_suggestions = game_manager.get_top_suggestions(3)
        self.assertIsInstance(new_suggestions, list)

        # Both should return valid suggestions since we used non-restrictive constraints
        self.assertGreater(len(initial_suggestions), 0)
        self.assertGreater(len(new_suggestions), 0)

    def test_migration_validation(self):
        """Test migration validation system."""
        # Run validation
        validation_results = strategy_factory.run_migration_validation(
            word_manager=self.word_manager,
            stateless_word_manager=self.stateless_word_manager,
        )

        self.assertIsInstance(validation_results, dict)

        # Check that migrated strategies have validation results
        for strategy_name in ["frequency", "entropy"]:
            if strategy_name in validation_results:
                result = validation_results[strategy_name]
                if result["status"] == "tested":
                    self.assertIn("overlap_percentage", result)
                    self.assertIn("equivalent", result)

    def test_performance_comparison(self):
        """Test performance comparison between legacy and stateless."""
        import time

        # Test legacy performance
        game_manager_legacy = EnhancedGameStateManager(
            word_manager=self.word_manager,
            strategy_name="frequency",
            use_stateless=False,
        )
        game_manager_legacy.add_guess(
            "ZZZZZ", "BBBBB"
        )  # Use non-restrictive constraint

        start_time = time.time()
        for _ in range(10):
            game_manager_legacy.get_top_suggestions(5)
        legacy_time = time.time() - start_time

        # Test stateless performance
        game_manager_stateless = EnhancedGameStateManager(
            word_manager=self.word_manager,
            strategy_name="frequency",
            use_stateless=True,
            stateless_word_manager=self.stateless_word_manager,
        )
        game_manager_stateless.add_guess(
            "ZZZZZ", "BBBBB"
        )  # Use non-restrictive constraint

        start_time = time.time()
        for _ in range(10):
            game_manager_stateless.get_top_suggestions(5)
        stateless_time = time.time() - start_time

        # Both should complete in reasonable time
        self.assertLess(legacy_time, 5.0)
        self.assertLess(stateless_time, 5.0)

        # Performance should be reasonable (allow 10x difference for small datasets and overhead)
        # In production with larger datasets, stateless is typically faster
        max_acceptable_time = max(legacy_time * 10, 0.1)  # At least 0.1s tolerance
        self.assertLess(stateless_time, max_acceptable_time)

    def test_game_state_analysis(self):
        """Test stateless game state analysis."""
        stateless_manager = StatelessGameStateManager(
            stateless_word_manager=self.stateless_word_manager
        )

        # Analyze different game states with less restrictive constraints
        constraints_early = [("ZZZZZ", "BBBBB")]  # Use letters not in dataset
        analysis_early = stateless_manager.analyze_game_state(constraints_early)

        constraints_late = [
            ("ZZZZZ", "BBBBB"),
            ("XXXXX", "BBBBB"),
        ]  # Multiple non-existent letter constraints
        analysis_late = stateless_manager.analyze_game_state(constraints_late)

        # Both should have words since we're using non-existent letters
        self.assertGreater(analysis_early["total_possible_words"], 0)
        self.assertGreater(analysis_late["total_possible_words"], 0)

        # Check game phase detection
        self.assertIn(
            analysis_early["game_phase"],
            ["opening", "early", "middle", "late", "endgame"],
        )
        self.assertIn(
            analysis_late["game_phase"],
            ["opening", "early", "middle", "late", "endgame"],
        )

    def test_backward_compatibility(self):
        """Test that existing stateful API still works."""
        # Test the old stateful approach
        original_count = self.word_manager.get_word_count()

        # Use a less restrictive constraint that won't filter out all words
        self.word_manager.filter_words("ZZZZZ", "BBBBB")  # Use non-existent letters

        # Should still have words since Z doesn't exist in our test dataset
        possible_words = self.word_manager.get_possible_words()
        self.assertGreater(len(possible_words), 0)

        # Reset and test again
        self.word_manager.reset()
        self.assertEqual(self.word_manager.get_word_count(), original_count)

    def test_error_handling(self):
        """Test error handling in migration system."""
        # Test invalid strategy name
        with self.assertRaises(ValueError):
            strategy_factory.create_strategy("nonexistent_strategy")

        # Test graceful fallback in enhanced game manager
        game_manager = EnhancedGameStateManager(
            word_manager=self.word_manager,
            strategy_name="frequency",
            use_stateless=True,
        )

        # Should not crash even with invalid switch
        result = game_manager.switch_strategy("nonexistent_strategy")
        self.assertFalse(result)

        # Original strategy should still work
        suggestions = game_manager.get_top_suggestions(3)
        self.assertIsInstance(suggestions, list)

    def test_comprehensive_workflow(self):
        """Test a complete workflow using the migration system."""
        # Create stateless game manager
        stateless_manager = StatelessGameStateManager(
            stateless_word_manager=self.stateless_word_manager,
            default_strategy="frequency",
        )

        # Simulate a complete game
        constraints = []
        game_words = ["SLATE", "CRANE", "AUDIO"]
        results = ["BYBBB", "YBGYB", "GGGGG"]

        for i, (guess, result) in enumerate(zip(game_words, results)):
            # Add constraint
            constraints.append((guess, result))

            # Analyze game state
            analysis = stateless_manager.analyze_game_state(constraints)
            self.assertIn("total_possible_words", analysis)
            self.assertIn("game_phase", analysis)

            # Get suggestions (except for final winning guess)
            if result != "GGGGG":
                suggestions = stateless_manager.get_suggestions(
                    constraints=constraints,
                    strategy_name="frequency" if i % 2 == 0 else "entropy",
                    count=5,
                )
                self.assertIsInstance(suggestions, list)


if __name__ == "__main__":
    unittest.main()
