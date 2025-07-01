# src/modules/backend/stats_manager.py
"""
Module for managing game statistics and history.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from ..logging_utils import log_method


class StatsManager:
    """Handles game statistics and history storage/retrieval."""

    def __init__(
        self,
        history_file: str = "game_history.json",
    ):
        self.history_file = history_file
        self.history = self._load_history()

    @log_method("DEBUG")
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load game history from file."""
        try:
            with open(self.history_file, encoding="utf-8") as f:
                return cast(List[Dict[str, Any]], json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @log_method("DEBUG")
    def save_history(self) -> None:
        """Save game history to file."""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

    @log_method("INFO")
    def record_game(
        self,
        guesses: List[List[str]],
        won: bool,
        attempts: int,
        *,  # Force keyword-only arguments
        game_id: str = "",
        target_word: str = "",
        mode: str = "manual"
    ) -> None:
        """
        Record a completed game in history.

        Args:
            guesses: List of [guess, result] pairs
            won: Whether the game was won
            attempts: Number of attempts made
            game_id: Unique ID for the game session (keyword-only)
            target_word: The target word for the game (keyword-only)
            mode: The game mode (solver/manual) (keyword-only)
        """
        # Update history
        game_record = {
            "timestamp": datetime.now().isoformat(),
            "guesses": guesses,
            "won": won,
            "attempts": attempts,
            "game_id": game_id,
            "mode": mode,
        }

        # Add target word if available
        if target_word:
            game_record["target_word"] = target_word

        self.history.append(game_record)
        self.save_history()

    @log_method("DEBUG")
    def get_stats(self) -> Dict[str, Any]:
        """Calculate and return current statistics dynamically from game history."""
        if not self.history:
            return {
                "games_played": 0,
                "games_won": 0,
                "win_rate": 0.0,
                "avg_attempts": 0.0,
            }

        games_played = len(self.history)
        games_won = sum(1 for game in self.history if game.get("won", False))
        win_rate = (games_won / games_played) * 100.0 if games_played > 0 else 0.0

        # Calculate average attempts for winning games only
        winning_games = [game for game in self.history if game.get("won", False)]
        if winning_games:
            total_attempts = sum(game.get("attempts", 0) for game in winning_games)
            avg_attempts = total_attempts / len(winning_games)
        else:
            avg_attempts = 0.0

        return {
            "games_played": games_played,
            "games_won": games_won,
            "win_rate": win_rate,
            "avg_attempts": avg_attempts,
        }

    @log_method("DEBUG")
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get game history, optionally limited to the most recent games."""
        if limit is None:
            return self.history
        return self.history[-limit:]

    @log_method("DEBUG")
    def get_game_by_id(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific game by its ID.

        Args:
            game_id: The unique ID of the game to retrieve

        Returns:
            The game record if found, None otherwise
        """
        for game in self.history:
            if game.get("game_id") == game_id:
                return game
        return None

    @log_method("DEBUG")
    def search_games(
        self,
        game_id: Optional[str] = None,
        won: Optional[bool] = None,
        target_word: Optional[str] = None,
        max_attempts: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for games matching specific criteria.

        Args:
            game_id: Filter by game ID (can be partial)
            won: Filter by game outcome (won/lost)
            target_word: Filter by target word
            max_attempts: Return only games with attempts <= this value

        Returns:
            List of matching game records
        """
        results = []

        for game in self.history:
            # Check if game matches all provided filters
            match = True

            if game_id is not None and game.get("game_id", "").find(game_id) == -1:
                match = False

            if won is not None and game.get("won") != won:
                match = False

            if (
                target_word is not None
                and game.get("target_word", "").upper() != target_word.upper()
            ):
                match = False

            if max_attempts is not None and game.get("attempts", 0) > max_attempts:
                match = False

            if match:
                results.append(game)

        return results

    @log_method("INFO")
    def clear_all_history(self) -> bool:
        """
        Clear all game history and reset to blank.

        Returns:
            bool: True if successful, False if there was an error
        """
        try:
            # Clear the in-memory history
            self.history = []

            # Save empty history to file
            self.save_history()

            return True
        except Exception:
            # If there's an error saving, restore the history and return False
            self.history = self._load_history()
            return False

    @log_method("DEBUG")
    def get_history_count(self) -> int:
        """Get the total number of games in history."""
        return len(self.history)

    @log_method("DEBUG")
    def has_history(self) -> bool:
        """Check if there is any game history."""
        return len(self.history) > 0
