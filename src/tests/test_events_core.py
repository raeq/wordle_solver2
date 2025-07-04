"""Tests for the event system's core event classes.

This module contains tests for the event system's core event classes,
ensuring that they handle event creation, properties, and data correctly.
"""

import re
from datetime import datetime, timezone

import pytest

from events.enums import EventType, GameState, LetterState
from events.event import (
    GameEvent,
    GameStateChangedEvent,
    LetterGuessedEvent,
    WordGuessedEvent,
)


class TestGameEvent:
    """Tests for the base GameEvent class."""

    def test_game_event_initialization(self):
        """Test that a GameEvent can be properly initialized."""
        event = GameEvent(source="test_source")

        assert event.source == "test_source"
        assert isinstance(event._timestamp, datetime)
        assert event._timestamp.tzinfo == timezone.utc  # Ensure timestamp is in UTC
        assert isinstance(event._event_id, str)
        assert event.event_type == EventType.BASE_EVENT

    def test_game_event_immutable_properties(self):
        """Test that timestamp and event_id are immutable (read-only)."""
        event = GameEvent()

        # Verify properties return the private attributes
        assert event.timestamp == event._timestamp
        assert event.event_id == event._event_id

        # Verify we can't set these attributes
        with pytest.raises(AttributeError):
            event.timestamp = datetime.now()

        with pytest.raises(AttributeError):
            event.event_id = "new_id"

    def test_game_event_unique_ids(self):
        """Test that each GameEvent gets a unique ID."""
        events = [GameEvent() for _ in range(100)]
        event_ids = [event.event_id for event in events]

        # Check all IDs are unique
        assert len(event_ids) == len(set(event_ids))

        # Check UUID format (basic check)
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        for event_id in event_ids:
            assert uuid_pattern.match(event_id), f"Invalid UUID format: {event_id}"

    def test_game_event_timestamp_accuracy(self):
        """Test that the event timestamp is accurate."""
        before = datetime.now(timezone.utc)
        event = GameEvent()
        after = datetime.now(timezone.utc)

        assert before <= event.timestamp <= after

    def test_game_event_data(self):
        """Test that get_event_data returns correct data structure."""
        event = GameEvent(source="test_source")
        data = event.get_event_data()

        assert isinstance(data, dict)
        assert data["event_id"] == event.event_id
        assert data["event_type"] == str(event.event_type)
        assert data["source"] == "test_source"
        assert data["timestamp"] == event.timestamp.isoformat()

    def test_game_event_with_none_source(self):
        """Test that GameEvent handles None source correctly."""
        event = GameEvent(source=None)
        data = event.get_event_data()

        assert event.source is None
        assert data["source"] is None


class TestLetterGuessedEvent:
    """Tests for the LetterGuessedEvent class."""

    def test_letter_guessed_event_initialization(self):
        """Test that LetterGuessedEvent can be properly initialized."""
        event = LetterGuessedEvent(
            letter="A", result=LetterState.CORRECT, source="test_source"
        )

        assert event.letter == "A"
        assert event.result == LetterState.CORRECT
        assert event.source == "test_source"
        assert event.event_type == EventType.LETTER_GUESSED

    def test_letter_guessed_event_data(self):
        """Test that get_event_data returns correct data structure."""
        event = LetterGuessedEvent(
            letter="B", result=LetterState.ABSENT, source="test_source"
        )
        data = event.get_event_data()

        assert isinstance(data, dict)
        # Check base event fields
        assert data["event_id"] == event.event_id
        assert data["event_type"] == str(event.event_type)
        assert data["source"] == "test_source"
        assert data["timestamp"] == event.timestamp.isoformat()
        # Check specific fields
        assert data["letter"] == "B"
        assert data["result"] == str(LetterState.ABSENT)

    def test_letter_guessed_event_with_edge_cases(self):
        """Test LetterGuessedEvent with edge case inputs."""
        # Test with empty letter
        event = LetterGuessedEvent(letter="", result=LetterState.PRESENT)
        assert event.letter == ""

        # Test with non-string letter
        from events.exceptions import EventValidationError

        with pytest.raises(EventValidationError) as exc_info:
            LetterGuessedEvent(letter=123, result=LetterState.PRESENT)

        assert "Letter must be a string, got int" in str(exc_info.value)


class TestWordGuessedEvent:
    """Tests for the WordGuessedEvent class."""

    def test_word_guessed_event_initialization(self):
        """Test that WordGuessedEvent can be properly initialized."""
        results = [
            LetterState.CORRECT,
            LetterState.ABSENT,
            LetterState.PRESENT,
            LetterState.ABSENT,
            LetterState.CORRECT,
        ]

        event = WordGuessedEvent(word="HELLO", results=results, source="test_source")

        assert event.word == "HELLO"
        assert event.results == results
        assert event.source == "test_source"
        assert event.event_type == EventType.WORD_GUESSED

    def test_word_guessed_event_data(self):
        """Test that get_event_data returns correct data structure."""
        results = [LetterState.CORRECT, LetterState.ABSENT]

        event = WordGuessedEvent(word="AB", results=results, source="test_source")
        data = event.get_event_data()

        assert isinstance(data, dict)
        # Check base event fields
        assert data["event_id"] == event.event_id
        assert data["event_type"] == str(event.event_type)
        assert data["source"] == "test_source"
        assert data["timestamp"] == event.timestamp.isoformat()
        # Check specific fields
        assert data["word"] == "AB"
        assert data["results"] == [str(state) for state in results]

    def test_word_guessed_event_with_edge_cases(self):
        """Test WordGuessedEvent with edge case inputs."""
        # Test with empty word
        event = WordGuessedEvent(word="", results=[])
        assert event.word == ""
        assert event.results == []

        # Test with mismatched word length and results length
        # This is technically valid from a type perspective but might be logically inconsistent
        event = WordGuessedEvent(word="ABC", results=[LetterState.CORRECT])
        assert len(event.word) != len(event.results)

        # Test with non-string word
        from events.exceptions import EventValidationError

        with pytest.raises(EventValidationError) as exc_info:
            WordGuessedEvent(word=123, results=[LetterState.CORRECT])

        assert "Word must be a string, got int" in str(exc_info.value)


class TestGameStateChangedEvent:
    """Tests for the GameStateChangedEvent class."""

    def test_game_state_changed_event_initialization(self):
        """Test that GameStateChangedEvent can be properly initialized."""
        metadata = {"won": True, "attempts": 3}

        event = GameStateChangedEvent(
            old_state=GameState.IN_PROGRESS,
            new_state=GameState.GAME_OVER,
            metadata=metadata,
            source="test_source",
        )

        assert event.old_state == GameState.IN_PROGRESS
        assert event.new_state == GameState.GAME_OVER
        assert event.metadata == metadata
        assert event.source == "test_source"
        assert event.event_type == EventType.GAME_STATE_CHANGED

    def test_game_state_changed_event_data(self):
        """Test that get_event_data returns correct data structure."""
        metadata = {"won": False}

        event = GameStateChangedEvent(
            old_state=GameState.STARTED,
            new_state=GameState.IN_PROGRESS,
            metadata=metadata,
            source="test_source",
        )
        data = event.get_event_data()

        assert isinstance(data, dict)
        # Check base event fields
        assert data["event_id"] == event.event_id
        assert data["event_type"] == str(event.event_type)
        assert data["source"] == "test_source"
        assert data["timestamp"] == event.timestamp.isoformat()
        # Check specific fields
        assert data["old_state"] == str(GameState.STARTED)
        assert data["new_state"] == str(GameState.IN_PROGRESS)
        assert data["metadata"] == metadata

    def test_game_state_changed_event_with_edge_cases(self):
        """Test GameStateChangedEvent with edge case inputs."""
        # Test with None metadata
        event = GameStateChangedEvent(
            old_state=GameState.INITIALIZED, new_state=GameState.STARTED, metadata=None
        )
        assert event.metadata == {}  # Should default to empty dict

        # Test with same old and new state
        event = GameStateChangedEvent(
            old_state=GameState.STARTED, new_state=GameState.STARTED
        )
        assert event.old_state == event.new_state
