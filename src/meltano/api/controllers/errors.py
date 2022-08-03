from __future__ import annotations


class InvalidFileNameError(Exception):
    """Occurs when an invalid file name is provided."""

    def __init__(self, name):
        self.name = name
