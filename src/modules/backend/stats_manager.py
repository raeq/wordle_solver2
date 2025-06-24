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
        stats_file: str = "game_stats.json",
        history_file: str = "game_history.json",
    ):
        self.stats_file = stats_file
        self.history_file = history_file
        self.stats = self._load_stats()
        self.history = self._load_history()

    @log_method("DEBUG")
    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        try:
            with open(self.stats_file) as f:
                return cast(Dict[str, Any], json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "games_played": 0,
                "games_won": 0,
                "win_rate": 0.0,
                "avg_attempts": 0.0,
            }

    @log_method("DEBUG")
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load game history from file."""
        try:
            with open(self.history_file) as f:
                return cast(List[Dict[str, Any]], json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @log_method("DEBUG")
    def save_stats(self) -> None:
        """Save statistics to file."""
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)

    @log_method("DEBUG")
    def save_history(self) -> None:
        """Save game history to file."""
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    @log_method("INFO")
    def record_game(
        self, guesses: List[List[str]], won: bool, attempts: int, game_id: str = "", target_word: str = ""
    ) -> None:
        """
        Record a completed game in history and update statistics.

        Args:
            guesses: List of [guess, result] pairs
            won: Whether the game was won
            attempts: Number of attempts made
            game_id: Unique ID for the game session
            target_word: The target word for the game (if available)
        """
        # Update history
        game_record = {
            "timestamp": datetime.now().isoformat(),
            "guesses": guesses,
            "won": won,
            "attempts": attempts,
            "game_id": game_id,
        }

        # Add target word if available
        if target_word:
            game_record["target_word"] = target_word

        self.history.append(game_record)
        self.save_history()

        # Update stats
        self.stats["games_played"] += 1
        if won:
            self.stats["games_won"] += 1

        # Recalculate win rate and average attempts
        self.stats["win_rate"] = (self.stats["games_won"] / self.stats["games_played"]) * 100.0

        total_attempts = 0
        completed_games = 0

        for game in self.history:
            if game["won"]:  # Only count winning games for average attempts
                total_attempts += game["attempts"]
                completed_games += 1

        if completed_games > 0:
            self.stats["avg_attempts"] = total_attempts / completed_games

        self.save_stats()

    @log_method("DEBUG")
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return self.stats

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

            if target_word is not None and game.get("target_word", "").upper() != target_word.upper():
                match = False

            if max_attempts is not None and game.get("attempts", 0) > max_attempts:
                match = False

            if match:
                results.append(game)

        return results
