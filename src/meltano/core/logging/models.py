"""Logging data structures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TracebackFrame:
    """A frame in a traceback."""

    filename: str
    function: str
    lineno: int


@dataclass
class SingerSDKException:
    """A Singer exception."""

    type: str
    module: str
    message: str
    traceback: list[TracebackFrame] | None = None
    cause: SingerSDKException | None = None
    context: SingerSDKException | None = None
