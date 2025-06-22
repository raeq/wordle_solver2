# src/modules/backend/result_color.py
"""
Enumeration of result colors for Wordle feedback.
"""
from enum import Enum
from typing import List

from .exceptions import InvalidColorError


class ResultColor(Enum):
    """Enumeration of possible letter result colors in Wordle."""

    GREEN = "G"  # Letter is correct and in the right position
    YELLOW = "Y"  # Letter is in the word but in the wrong position
    BLACK = "B"  # Letter is not in the word

    @classmethod
    def from_char(cls, char: str) -> "ResultColor":
        """Convert a character representation to the corresponding ResultColor."""
        char = char.upper()
        for color in cls:
            if color.value == char:
                return color
        raise InvalidColorError(char)

    @classmethod
    def is_valid_result_string(cls, result: str) -> bool:
        """Check if a string contains only valid result characters."""
        return all(char.upper() in [color.value for color in cls] for char in result)

    @classmethod
    def is_winning_result(cls, result: str) -> bool:
        """Check if a result string represents a winning game (all green)."""
        return result == cls.GREEN.value * 5

    @classmethod
    def result_to_emoji(cls, result: str) -> str:
        """Convert a result string to emoji representation for sharing."""
        emoji_map = {
            cls.GREEN.value: "🟩",
            cls.YELLOW.value: "🟨",
            cls.BLACK.value: "⬛",
        }
        return "".join(emoji_map.get(char.upper(), "❓") for char in result)

    @classmethod
    def parse_result(cls, result_str: str) -> List["ResultColor"]:
        """Parse a string of result characters into a list of ResultColor objects."""
        return [cls.from_char(char) for char in result_str]

    @classmethod
    def format_result(cls, colors: List["ResultColor"]) -> str:
        """Convert a list of ResultColor objects to a string representation."""
        return "".join(color.value for color in colors)

    def to_style(self) -> str:
        """Get the Rich style string for this color."""
        if self == self.GREEN:
            return "black on green"
        elif self == self.YELLOW:
            return "black on yellow"
        else:  # BLACK
            return "white on grey23"
