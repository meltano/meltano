from __future__ import annotations


class InvalidFileNameError(Exception):
    """An invalid file name is provided."""

    def __init__(self, name):
        self.name = name
