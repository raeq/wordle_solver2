# src/modules/backend/game_history_manager.py
"""
Game history management for reviewing previous games.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from src.modules.backend.exceptions import WordleError


class GameHistoryError(WordleError):
    """Exception raised for game history related errors."""


class GameHistoryManager:
    """Manages loading and processing game history data."""

    def __init__(self, history_file_path: str = None):
        if history_file_path is None:
            # Get the absolute path to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(current_dir))
            )
            self.history_file_path = os.path.join(
                project_root, "src", "game_history.json"
            )
        else:
            self.history_file_path = history_file_path

    def load_game_history(self) -> List[Dict]:
        """Load and parse game history from JSON file."""
        try:
            if not os.path.exists(self.history_file_path):
                return []

            with open(self.history_file_path, "r", encoding="utf-8") as file:
                games = json.load(file)
                return games if isinstance(games, list) else []

        except (json.JSONDecodeError, IOError) as e:
            raise GameHistoryError(f"Failed to load game history: {str(e)}")

    def paginate_games(
        self, games: List[Dict], page_size: int = 10
    ) -> List[List[Dict]]:
        """Split games into pages of specified size."""
        if not games:
            return []

        pages = []
        for i in range(0, len(games), page_size):
            pages.append(games[i : i + page_size])
        return pages

    def get_game_by_id(self, games: List[Dict], game_id: str) -> Optional[Dict]:
        """Find and return a game by its ID."""
        game_id = game_id.upper().strip()
        for game in games:
            if game.get("game_id", "").upper() == game_id:
                return game
        return None

    def format_game_summary(self, game: Dict) -> Dict[str, str]:
        """Format a game for display in the summary table."""
        timestamp = game.get("timestamp", "Unknown")
        try:
            # Parse timestamp and format for display
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            formatted_date = timestamp[:16] if len(timestamp) > 16 else timestamp

        return {
            "game_id": game.get("game_id", "Unknown"),
            "date": formatted_date,
            "target": game.get("target_word", "Unknown"),
            "attempts": str(game.get("attempts", 0)),
            "result": "Won" if game.get("won", False) else "Lost",
        }

    def validate_game_id(self, game_id: str) -> bool:
        """Validate that a game ID is in the correct format (6 characters)."""
        return len(game_id.strip()) == 6 and game_id.strip().isalnum()
