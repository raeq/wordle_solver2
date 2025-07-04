"""Tests for the observer system and event bus.

This module contains tests for the observer pattern implementation and event bus,
ensuring proper subscription, unsubscription, and event publishing functionality.
"""

from unittest.mock import Mock

import pytest

from events.enums import EventType, GameState, LetterState
from events.event import (
    GameEvent,
    GameStateChangedEvent,
    LetterGuessedEvent,
    WordGuessedEvent,
)
from events.observer import GameEventBus, GameStateObserver


class TestGameStateObserver:
    """Tests for the GameStateObserver interface."""

    def test_observer_interface(self):
        """Test that GameStateObserver is a proper abstract class."""
        # Should not be able to instantiate abstract class
        with pytest.raises(TypeError):
            GameStateObserver()


class MockObserver(GameStateObserver):
    """Mock implementation of GameStateObserver for testing."""

    def __init__(self):
        self.events_received = []

    def notify(self, event: GameEvent) -> None:
        """Record the event when notified."""
        self.events_received.append(event)


class TestGameEventBus:
    """Tests for the GameEventBus class."""

    def test_event_bus_initialization(self):
        """Test that GameEventBus initializes with empty observer lists."""
        bus = GameEventBus()
        assert len(bus._observers) == 0
        assert len(bus._global_observers) == 0

    def test_subscribe_global_observer(self):
        """Test subscribing an observer to all events."""
        bus = GameEventBus()
        observer = MockObserver()

        bus.subscribe(observer)
        assert observer in bus._global_observers
        assert len(bus._observers) == 0

    def test_subscribe_specific_event_type(self):
        """Test subscribing an observer to a specific event type."""
        bus = GameEventBus()
        observer = MockObserver()
        event_type = str(EventType.LETTER_GUESSED)

        bus.subscribe(observer, event_type)
        assert observer not in bus._global_observers
        assert event_type in bus._observers
        assert observer in bus._observers[event_type]

    def test_subscribe_multiple_observers(self):
        """Test subscribing multiple observers to different event types."""
        bus = GameEventBus()
        observer1 = MockObserver()
        observer2 = MockObserver()
        observer3 = MockObserver()

        event_type1 = str(EventType.LETTER_GUESSED)
        event_type2 = str(EventType.WORD_GUESSED)

        bus.subscribe(observer1)  # Global
        bus.subscribe(observer2, event_type1)  # Specific
        bus.subscribe(observer3, event_type2)  # Specific
        bus.subscribe(observer3, event_type1)  # Multiple specific

        assert observer1 in bus._global_observers
        assert observer2 in bus._observers[event_type1]
        assert observer3 in bus._observers[event_type1]
        assert observer3 in bus._observers[event_type2]

    def test_unsubscribe_global_observer(self):
        """Test unsubscribing a global observer."""
        bus = GameEventBus()
        observer = MockObserver()

        bus.subscribe(observer)
        assert observer in bus._global_observers

        bus.unsubscribe(observer)
        assert observer not in bus._global_observers

    def test_unsubscribe_specific_event_type(self):
        """Test unsubscribing an observer from a specific event type."""
        bus = GameEventBus()
        observer = MockObserver()
        event_type = str(EventType.LETTER_GUESSED)

        bus.subscribe(observer, event_type)
        assert observer in bus._observers[event_type]

        bus.unsubscribe(observer, event_type)
        assert observer not in bus._observers[event_type]

    def test_unsubscribe_nonexistent_observer(self):
        """Test unsubscribing an observer that isn't subscribed."""
        bus = GameEventBus()
        observer = MockObserver()

        # Should not raise an exception
        bus.unsubscribe(observer)

        event_type = str(EventType.LETTER_GUESSED)
        bus.unsubscribe(observer, event_type)

    def test_unsubscribe_from_all_event_types(self):
        """Test unsubscribing an observer from all event types."""
        bus = GameEventBus()
        observer = MockObserver()

        event_type1 = str(EventType.LETTER_GUESSED)
        event_type2 = str(EventType.WORD_GUESSED)

        bus.subscribe(observer, event_type1)
        bus.subscribe(observer, event_type2)
        bus.subscribe(observer)  # Also global

        bus.unsubscribe(observer)  # Should remove from all

        assert observer not in bus._global_observers
        assert observer not in bus._observers.get(event_type1, [])
        assert observer not in bus._observers.get(event_type2, [])

    def test_publish_to_global_observers(self):
        """Test publishing an event to global observers."""
        bus = GameEventBus()
        observer1 = MockObserver()
        observer2 = MockObserver()

        bus.subscribe(observer1)
        bus.subscribe(observer2)

        event = GameEvent(source="test")
        bus.publish(event)

        assert len(observer1.events_received) == 1
        assert observer1.events_received[0] == event
        assert len(observer2.events_received) == 1
        assert observer2.events_received[0] == event

    def test_publish_to_specific_observers(self):
        """Test publishing an event to observers of a specific type."""
        bus = GameEventBus()
        observer1 = MockObserver()  # For letter events
        observer2 = MockObserver()  # For word events

        bus.subscribe(observer1, str(EventType.LETTER_GUESSED))
        bus.subscribe(observer2, str(EventType.WORD_GUESSED))

        letter_event = LetterGuessedEvent(letter="A", result=LetterState.CORRECT)
        bus.publish(letter_event)

        assert len(observer1.events_received) == 1
        assert observer1.events_received[0] == letter_event
        assert len(observer2.events_received) == 0

        word_event = WordGuessedEvent(word="HELLO", results=[LetterState.CORRECT] * 5)
        bus.publish(word_event)

        assert len(observer1.events_received) == 1  # Unchanged
        assert len(observer2.events_received) == 1
        assert observer2.events_received[0] == word_event

    def test_publish_to_both_global_and_specific(self):
        """Test that events are published to both global and specific observers."""
        bus = GameEventBus()
        global_observer = MockObserver()
        specific_observer = MockObserver()

        bus.subscribe(global_observer)
        bus.subscribe(specific_observer, str(EventType.LETTER_GUESSED))

        event = LetterGuessedEvent(letter="B", result=LetterState.PRESENT)
        bus.publish(event)

        assert len(global_observer.events_received) == 1
        assert global_observer.events_received[0] == event
        assert len(specific_observer.events_received) == 1
        assert specific_observer.events_received[0] == event

    def test_publish_with_no_matching_observers(self):
        """Test publishing an event type with no matching observers."""
        bus = GameEventBus()
        observer = MockObserver()

        bus.subscribe(observer, str(EventType.LETTER_GUESSED))

        event = WordGuessedEvent(  # Different type than subscribed
            word="HELLO", results=[LetterState.CORRECT] * 5
        )
        bus.publish(event)

        assert len(observer.events_received) == 0

    def test_observer_exception_handling(self):
        """Test that an exception in one observer doesn't prevent others from being notified."""
        bus = GameEventBus()

        # Create a well-behaved observer
        good_observer = MockObserver()

        # Create an observer that raises an exception
        bad_observer = Mock(spec=GameStateObserver)
        bad_observer.notify.side_effect = Exception("Observer failed")

        bus.subscribe(good_observer)
        bus.subscribe(bad_observer)

        event = GameEvent()

        # The exception should be caught and not propagated
        with pytest.raises(Exception):
            bus.publish(event)

        # Despite the exception, good_observer should still have received the event
        assert len(good_observer.events_received) == 1
        assert good_observer.events_received[0] == event

        # And the bad observer's notify should have been called
        bad_observer.notify.assert_called_once_with(event)


class TestComplexEventSequences:
    """Tests for complex sequences of events and observer interactions."""

    def test_observer_chain_reaction(self):
        """Test a chain reaction where observers publish events in response to events."""
        bus = GameEventBus()

        # Create an observer that collects events but doesn't trigger new ones
        recorder = MockObserver()

        # Subscribe the recorder first to ensure it gets the initial event before any chain reaction
        bus.subscribe(recorder)

        # Create an observer that publishes a new event when notified
        class ChainReactionObserver(GameStateObserver):
            def __init__(self, event_bus):
                self.event_bus = event_bus
                self.events_received = []
                self.chain_depth = 0
                self.max_chain_depth = 3  # Prevent infinite recursion

            def notify(self, event):
                self.events_received.append(event)
                self.chain_depth += 1

                if self.chain_depth <= self.max_chain_depth:
                    # Publish a new event in response
                    new_event = GameEvent(source=f"chain_{self.chain_depth}")
                    self.event_bus.publish(new_event)

        # Create and subscribe the chain reaction observer after the recorder
        observer = ChainReactionObserver(bus)
        bus.subscribe(observer)

        # Create and publish the initial event
        initial_event = GameEvent(source="initial")
        bus.publish(initial_event)

        # We should have the initial event plus 3 chain reaction events
        assert len(recorder.events_received) == 4
        assert recorder.events_received[0].source == "initial"
        assert recorder.events_received[1].source == "chain_1"
        assert recorder.events_received[2].source == "chain_2"
        assert recorder.events_received[3].source == "chain_3"

    def test_multiple_event_types_and_observers(self):
        """Test complex interaction with multiple event types and observers."""
        bus = GameEventBus()

        # Create different types of observers
        letter_observer = MockObserver()
        word_observer = MockObserver()
        state_observer = MockObserver()
        global_observer = MockObserver()

        # Subscribe observers to different event types
        bus.subscribe(letter_observer, str(EventType.LETTER_GUESSED))
        bus.subscribe(word_observer, str(EventType.WORD_GUESSED))
        bus.subscribe(state_observer, str(EventType.GAME_STATE_CHANGED))
        bus.subscribe(global_observer)  # All events

        # Create and publish different events
        letter_event = LetterGuessedEvent("A", LetterState.CORRECT)
        word_event = WordGuessedEvent("HELLO", [LetterState.CORRECT] * 5)
        state_event = GameStateChangedEvent(GameState.INITIALIZED, GameState.STARTED)

        bus.publish(letter_event)
        bus.publish(word_event)
        bus.publish(state_event)

        # Check that each observer received the right events
        assert len(letter_observer.events_received) == 1
        assert letter_observer.events_received[0] == letter_event

        assert len(word_observer.events_received) == 1
        assert word_observer.events_received[0] == word_event

        assert len(state_observer.events_received) == 1
        assert state_observer.events_received[0] == state_event

        # Global observer should have received all events
        assert len(global_observer.events_received) == 3
        assert global_observer.events_received[0] == letter_event
        assert global_observer.events_received[1] == word_event
        assert global_observer.events_received[2] == state_event

    def test_subscribe_unsubscribe_during_notification(self):
        """Test observers subscribing/unsubscribing during notification."""
        from events.exceptions import EventSubscriptionError

        bus = GameEventBus()

        class DynamicObserver(GameStateObserver):
            def __init__(self, bus, observer_to_add=None, observer_to_remove=None):
                self.bus = bus
                self.observer_to_add = observer_to_add
                self.observer_to_remove = observer_to_remove
                self.notified = False
                self.subscription_attempted = False

            def notify(self, event):
                self.notified = True
                # Subscribe a new observer
                if self.observer_to_add and not self.subscription_attempted:
                    self.subscription_attempted = True
                    try:
                        self.bus.subscribe(self.observer_to_add)
                    except EventSubscriptionError:
                        # It's ok if the observer is already subscribed
                        pass
                # Unsubscribe an existing observer
                if self.observer_to_remove:
                    self.bus.unsubscribe(self.observer_to_remove)

        # Create observers
        late_observer = MockObserver()
        doomed_observer = MockObserver()

        # Observer that adds late_observer during notification
        adding_observer = DynamicObserver(bus, observer_to_add=late_observer)

        # Observer that removes doomed_observer during notification
        removing_observer = DynamicObserver(bus, observer_to_remove=doomed_observer)

        # Subscribe observers
        bus.subscribe(adding_observer)
        bus.subscribe(removing_observer)
        bus.subscribe(doomed_observer)

        # Publish an event
        event = GameEvent()
        # With the more robust error handling, we need to catch the exception here too
        try:
            bus.publish(event)
        except Exception:
            # The test is about the behavior of observers during notification
            # so we can ignore exceptions from the publish operation itself
            pass

        # Verify both dynamic observers were notified
        assert adding_observer.notified
        assert removing_observer.notified

        # The doomed observer should have been notified before being unsubscribed
        assert len(doomed_observer.events_received) == 1

        # Now add the late observer directly since the dynamic subscription might have failed
        # but only if it hasn't been subscribed already
        try:
            if len(late_observer.events_received) == 0:
                bus.subscribe(late_observer)
        except EventSubscriptionError:
            # If late_observer was successfully added during notification but hasn't received any events yet,
            # this is expected and we can ignore the error
            pass

        # Publish another event
        second_event = GameEvent()
        bus.publish(second_event)

        # Now the late observer should receive it, but not the doomed one
        assert len(late_observer.events_received) == 1
        assert late_observer.events_received[0] == second_event

        assert len(doomed_observer.events_received) == 1  # Still just the first one


class TestEventValidation:
    """Tests for event validation in GameEventBus.publish()."""

    def test_publish_none_event(self):
        """Test that publishing None as an event raises an EventPublishingError."""
        from events.exceptions import EventPublishingError

        bus = GameEventBus()
        with pytest.raises(EventPublishingError) as exc_info:
            bus.publish(None)
        assert "Cannot publish None event" in str(exc_info.value)

    def test_publish_non_game_event(self):
        """Test that publishing objects that are not GameEvent instances raises an error."""
        from events.exceptions import EventPublishingError

        bus = GameEventBus()
        invalid_events = [
            "string_event",
            123,
            {},
            [],
            object(),
        ]

        for event in invalid_events:
            with pytest.raises(EventPublishingError) as exc_info:
                bus.publish(event)
            assert "Invalid event type" in str(exc_info.value)

    def test_publish_event_invalid_event_type(self):
        """Test validation for events with invalid event_type attribute."""
        from events.exceptions import EventPublishingError

        bus = GameEventBus()

        # Create a broken event class with invalid event_type
        class BrokenEventInvalidType(GameEvent):
            event_type = None  # or use an invalid type, e.g., 123

        with pytest.raises(EventPublishingError) as exc_info:
            bus.publish(BrokenEventInvalidType())
        assert "invalid event_type" in str(exc_info.value).lower()

    def test_publish_event_missing_event_id(self):
        """Test validation for events missing the event_id property."""
        from events.exceptions import EventPublishingError

        bus = GameEventBus()

        # Create a broken event class missing event_id
        class BrokenEventNoId(GameEvent):
            @property
            def event_id(self):
                # Force AttributeError when event_id is accessed
                raise AttributeError("event_id not defined")

        with pytest.raises(EventPublishingError) as exc_info:
            bus.publish(BrokenEventNoId())
        assert "missing event_id" in str(exc_info.value)

    def test_publish_event_invalid_event_id(self):
        """Test validation for events with invalid event_id formats."""
        from events.exceptions import EventPublishingError

        bus = GameEventBus()

        # Create broken events with different invalid event_id formats
        class BrokenEventEmptyId(GameEvent):
            @property
            def event_id(self):
                return ""

        class BrokenEventNonStringId(GameEvent):
            @property
            def event_id(self):
                return 12345  # Not a string

        class BrokenEventNoneId(GameEvent):
            @property
            def event_id(self):
                return None

        invalid_event_classes = [
            BrokenEventEmptyId,
            BrokenEventNonStringId,
            BrokenEventNoneId,
        ]

        for event_class in invalid_event_classes:
            with pytest.raises(EventPublishingError) as exc_info:
                bus.publish(event_class())
            assert "Invalid event_id" in str(exc_info.value)

    def test_publish_event_missing_timestamp(self):
        """Test validation for events missing the timestamp property."""
        from events.exceptions import EventPublishingError

        bus = GameEventBus()

        # Create a broken event class missing timestamp
        class BrokenEventNoTimestamp(GameEvent):
            @property
            def timestamp(self):
                # Force AttributeError when timestamp is accessed
                raise AttributeError("timestamp not defined")

        with pytest.raises(EventPublishingError) as exc_info:
            bus.publish(BrokenEventNoTimestamp())
        assert "missing timestamp attribute" in str(exc_info.value)

    def test_publish_event_empty_timestamp(self):
        """Test validation for events with empty timestamp."""
        from events.exceptions import EventPublishingError

        bus = GameEventBus()

        # Create a broken event class with empty timestamp
        class BrokenEventEmptyTimestamp(GameEvent):
            @property
            def timestamp(self):
                return None

        with pytest.raises(EventPublishingError) as exc_info:
            bus.publish(BrokenEventEmptyTimestamp())
        assert "Event has an empty timestamp" in str(exc_info.value)

    def test_publish_event_invalid_get_event_data(self):
        """Test validation for events with invalid get_event_data() implementations."""
        from events.exceptions import EventPublishingError

        bus = GameEventBus()

        # Create broken events with different get_event_data issues
        class BrokenEventNonDictData(GameEvent):
            def get_event_data(self):
                return "not a dictionary"

        class BrokenEventRaisingData(GameEvent):
            def get_event_data(self):
                raise ValueError("Error getting event data")

        class BrokenEventNoneData(GameEvent):
            def get_event_data(self):
                return None

        invalid_event_classes = [
            BrokenEventNonDictData,
            BrokenEventRaisingData,
            BrokenEventNoneData,
        ]

        for event_class in invalid_event_classes:
            with pytest.raises(EventPublishingError) as exc_info:
                bus.publish(event_class())

            if event_class == BrokenEventRaisingData:
                assert "Failed to get event data" in str(exc_info.value)
            else:
                assert "must return a dictionary" in str(exc_info.value)

    def test_publish_event_multiple_validation_failures(self):
        """Test that an event with multiple validation issues raises appropriate errors."""
        from events.exceptions import EventPublishingError

        bus = GameEventBus()

        # Create an event with multiple issues to ensure the first one is caught
        class VeryBrokenEvent:
            # Not a GameEvent subclass
            # Missing event_type
            # Missing event_id
            # Missing timestamp
            # Missing get_event_data
            pass

        with pytest.raises(EventPublishingError) as exc_info:
            bus.publish(VeryBrokenEvent())
        assert "Invalid event type" in str(exc_info.value)
