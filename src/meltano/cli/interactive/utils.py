"""Interactivity utils."""

from __future__ import annotations

import enum
import sys

if sys.version_info < (3, 11):
    from backports.strenum import StrEnum
else:
    from enum import StrEnum


class InteractionStatus(StrEnum):
    """Interaction status constants."""

    EXIT = enum.auto()
    SKIP = enum.auto()
    START = enum.auto()
    RETRY = enum.auto()
