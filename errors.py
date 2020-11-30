import logging

logger = logging.getLogger(__name__)


class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        print(message)


class WrongDateError(Error):
    def __init__(self, message: str = "The provided date is not valid."):
        super().__init__(message)


class NoSuchNote(Error):
    def __init__(self, message: str = "Note not found."):
        super().__init__(message)


class DuplicateNote(Error):
    def __init__(self, message: str = "Note already exists."):
        super().__init__(message)
