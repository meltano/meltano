"""Logging data structures."""

from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class ParsedLogRecord:
    """Represents a parsed log record with structured data."""

    level: int
    message: str
    extra: dict[str, t.Any]
    timestamp: str | None = None
    logger_name: str | None = None
    exception: PluginException | None = None


@dataclass
class TracebackFrame:
    """A frame in a traceback."""

    #: The filename location of the frame.
    filename: str
    #: The function name location of the frame.
    function: str
    #: The line number location of the frame.
    lineno: int
    #: The line of code in the original file.
    line: str


@dataclass
class PluginException:
    """A Singer exception."""

    #: The type of the exception.
    type: str
    #: The module that contains the exception.
    module: str
    #: The message of the exception.
    message: str

    _: KW_ONLY

    #: The traceback of the exception.
    traceback: list[TracebackFrame] | None = None
    #: The cause of the exception.
    cause: PluginException | None = None
    #: The context of the exception.
    context: PluginException | None = None

    @classmethod
    def from_dict(cls, data: dict) -> PluginException:
        """Create a PluginException from a dictionary."""
        exc_traceback = data.get("traceback")
        exc_cause = data.get("cause")
        exc_context = data.get("context")
        exc_traceback = (
            [
                TracebackFrame(
                    filename=frame["filename"],
                    function=frame["function"],
                    lineno=frame["lineno"],
                    line=frame["line"],
                )
                for frame in exc_traceback
            ]
            if exc_traceback
            else None
        )
        exc_cause = cls.from_dict(exc_cause) if exc_cause else None
        exc_context = cls.from_dict(exc_context) if exc_context else None
        return cls(
            type=data["type"],
            module=data["module"],
            message=data["message"],
            traceback=exc_traceback,
            cause=exc_cause,
            context=exc_context,
        )

    def to_dict(self) -> dict:
        """Convert the PluginException to a dictionary."""
        result: dict[str, t.Any] = {
            "type": self.type,
            "module": self.module,
            "message": self.message,
        }

        if self.traceback:
            result["traceback"] = [
                {
                    "filename": frame.filename,
                    "function": frame.function,
                    "lineno": frame.lineno,
                    "line": frame.line,
                }
                for frame in self.traceback
            ]
        if self.cause:
            result["cause"] = self.cause.to_dict()
        if self.context:
            result["context"] = self.context.to_dict()
        return result

    def __structlog__(self) -> dict:
        """Convert the PluginException to a dictionary."""
        return self.to_dict()
