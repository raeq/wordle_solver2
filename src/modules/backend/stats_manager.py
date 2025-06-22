# src/modules/backend/stats_manager.py
"""
Module for managing game statistics and history.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional


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

    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        try:
            with open(self.stats_file) as f:
                return json.load(f)  # type: Dict[str, Any]
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "games_played": 0,
                "games_won": 0,
                "win_rate": 0.0,
                "avg_attempts": 0.0,
            }

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load game history from file."""
        try:
            with open(self.history_file) as f:
                return json.load(f)  # type: List[Dict[str, Any]]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_stats(self) -> None:
        """Save statistics to file."""
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)

    def save_history(self) -> None:
        """Save game history to file."""
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def record_game(self, guesses: List[List[str]], won: bool, attempts: int) -> None:
        """Record a completed game in history and update statistics."""
        # Update history
        game_record = {
            "timestamp": datetime.now().isoformat(),
            "guesses": guesses,
            "won": won,
            "attempts": attempts,
        }
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

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return self.stats

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get game history, optionally limited to the most recent games."""
        if limit is None:
            return self.history
        return self.history[-limit:]
