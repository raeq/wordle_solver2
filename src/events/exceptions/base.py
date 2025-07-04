"""
Base exceptions for the event system.

This module provides the base exception classes for the Wordle Solver's event system.
"""


class WordleEventSystemException(Exception):
    """Base exception for all event system related errors.

    This exception serves as the root of the event system exception hierarchy,
    allowing for general error catching while still enabling specific error types.
    """

    def __init__(self, message: str, *args):
        """Initialize the exception with a message.

        Args:
            message: A human-readable error description
            *args: Additional arguments to pass to the parent Exception class
        """
        self.message = message
        super().__init__(message, *args)
