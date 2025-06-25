from __future__ import annotations

import enum
import sys

if sys.version_info < (3, 11):
    from backports.strenum import StrEnum
else:
    from enum import StrEnum


class StateStrategy(StrEnum):
    """Strategy to use for state management."""

    MERGE = enum.auto()
    OVERWRITE = enum.auto()
