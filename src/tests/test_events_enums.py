"""Tests for the event system enumerations.

This module contains tests for the event system's enumeration classes.
"""


from events.enums import EventType, GameState, LetterState


class TestEventEnums:
    """Tests for the event system enumerations."""

    def test_wordle_enum_str_representation(self):
        """Test that WordleEnum __str__ method works correctly."""
        # Since we can't instantiate WordleEnum directly (it's not meant to be),
        # we'll test its functionality through its child classes
        assert str(EventType.BASE_EVENT) == "base_event"
        assert str(GameState.STARTED) == "started"
        assert str(LetterState.CORRECT) == "correct"

    def test_event_type_values(self):
        """Test that EventType enum has the expected values and they are unique."""
        # Test all values are present
        assert hasattr(EventType, "BASE_EVENT")
        assert hasattr(EventType, "LETTER_GUESSED")
        assert hasattr(EventType, "WORD_GUESSED")
        assert hasattr(EventType, "GAME_STATE_CHANGED")

        # Test uniqueness of values
        values = [member.value for member in EventType]
        assert len(values) == len(set(values)), "EventType values should be unique"

        # Test specific values if they're defined explicitly
        # These should be updated if the actual values change
        expected_values = {
            EventType.BASE_EVENT: 300,
            EventType.LETTER_GUESSED: 310,
            EventType.WORD_GUESSED: 320,
            EventType.GAME_STATE_CHANGED: 330,
        }
        for enum_member, expected_value in expected_values.items():
            assert (
                enum_member.value == expected_value
            ), f"Expected {enum_member.name} to have value {expected_value}"

    def test_game_state_values(self):
        """Test that GameState enum has the expected values and they are unique."""
        # Test all values are present
        assert hasattr(GameState, "INITIALIZED")
        assert hasattr(GameState, "STARTED")
        assert hasattr(GameState, "IN_PROGRESS")
        assert hasattr(GameState, "GAME_OVER")
        assert hasattr(GameState, "PAUSED")

        # Test uniqueness of values
        values = [member.value for member in GameState]
        assert len(values) == len(set(values)), "GameState values should be unique"

        # Test specific values if they're defined explicitly
        expected_values = {
            GameState.INITIALIZED: 100,
            GameState.STARTED: 110,
            GameState.IN_PROGRESS: 120,
            GameState.GAME_OVER: 130,
            GameState.PAUSED: 140,
        }
        for enum_member, expected_value in expected_values.items():
            assert (
                enum_member.value == expected_value
            ), f"Expected {enum_member.name} to have value {expected_value}"

    def test_letter_state_values(self):
        """Test that LetterState enum has the expected values and they are unique."""
        # Test all values are present
        assert hasattr(LetterState, "UNDEFINED")
        assert hasattr(LetterState, "CORRECT")
        assert hasattr(LetterState, "PRESENT")
        assert hasattr(LetterState, "ABSENT")

        # Test uniqueness of values
        values = [member.value for member in LetterState]
        assert len(values) == len(set(values)), "LetterState values should be unique"

        # Test specific values if they're defined explicitly
        expected_values = {
            LetterState.UNDEFINED: 200,
            LetterState.CORRECT: 210,
            LetterState.PRESENT: 220,
            LetterState.ABSENT: 230,
        }
        for enum_member, expected_value in expected_values.items():
            assert (
                enum_member.value == expected_value
            ), f"Expected {enum_member.name} to have value {expected_value}"
