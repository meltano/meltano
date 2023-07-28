"""Example Python module which provides a Meltano-invocable echo command."""

from __future__ import annotations

import sys


def echo() -> None:
    """Echo process arguments."""
    print(*sys.argv[1:])  # noqa: WPS421
