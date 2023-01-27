"""Interactivity utils."""
from __future__ import annotations

from enum import Enum


class InteractionStatus(str, Enum):
    """Interaction status constants."""

    EXIT = "exit"
    SKIP = "skip"
    START = "start"
    RETRY = "retry"
