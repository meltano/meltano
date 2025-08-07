"""Interactivity utils."""

from __future__ import annotations

import enum
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class InteractionStatus(StrEnum):
    """Interaction status constants."""

    EXIT = enum.auto()
    SKIP = enum.auto()
    START = enum.auto()
    RETRY = enum.auto()
