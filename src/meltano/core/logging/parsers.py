"""Log parsers for different plugin output formats."""

from __future__ import annotations

import json
import logging
import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)  # noqa: TID251


@dataclass(frozen=True, kw_only=True, slots=True)
class ParsedLogRecord:
    """Represents a parsed log record with structured data."""

    level: int
    message: str
    extra: dict[str, t.Any]
    timestamp: str | None = None
    logger_name: str | None = None


class LogParser(ABC):
    """Base class for log parsers."""

    @abstractmethod
    def parse(self, line: str) -> ParsedLogRecord | None:
        """Parse a log line into structured data.

        Args:
            line: Raw log line to parse.

        Returns:
            ParsedLogRecord if parsing succeeds, None otherwise.
        """


class SingerSDKLogParser(LogParser):
    """Parser for Singer SDK structured JSON logs."""

    def parse(self, line: str) -> ParsedLogRecord | None:
        """Parse Singer SDK JSON log line.

        Args:
            line: Raw JSON log line.

        Returns:
            ParsedLogRecord with structured data or None if parsing fails.
        """
        line = line.strip()
        if not line:
            return None

        # Quick check for JSON structure
        if not (line.startswith("{") and line.endswith("}")):
            return None

        try:
            data = json.loads(line)

            # Singer SDK logs should have at least these fields
            if not (
                isinstance(data, dict)
                and "levelname" in data
                and "message" in data
                and "name" in data
            ):
                return None

            # Extract core log fields
            level_name = data.get("levelname", "INFO")
            level = getattr(logging, level_name, logging.INFO)
            message = data.get("message", "")
            logger_name = data.get("name")
            timestamp = data.get("created") or data.get("asctime")

            # Prepare extra fields (everything except core logging fields)
            skip_fields = {
                "levelname",
                "message",
                "name",
                "created",
                "asctime",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }

            extra = {
                key: value for key, value in data.items() if key not in skip_fields
            }

            return ParsedLogRecord(
                level=level,
                message=message,
                extra=extra,
                timestamp=str(timestamp) if timestamp else None,
                logger_name=logger_name,
            )

        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            # Log parsing failure for debugging
            logger.debug(
                "Failed to parse Singer SDK log line: %s",
                e,
                extra={"raw_line": line[:200]},  # Truncate for safety
            )
            return None


class PassthroughLogParser(LogParser):
    """Fallback parser that passes through unparsed lines."""

    def parse(self, line: str) -> ParsedLogRecord | None:
        """Return line as-is with minimal structure.

        Args:
            line: Raw log line.

        Returns:
            ParsedLogRecord with the line as message.
        """
        line = line.strip()
        if not line:
            return None

        return ParsedLogRecord(
            level=logging.INFO,
            message=line,
            extra={},
        )


class LogParserFactory:
    """Factory for creating and managing log parsers."""

    def __init__(self) -> None:
        """Initialize the parser factory."""
        self._parsers: dict[str, LogParser] = {}
        self._default_parsers: list[LogParser] = []

        # Register default parsers
        self.register_parser("singer-sdk", SingerSDKLogParser())
        self._default_parsers = [PassthroughLogParser()]

    def register_parser(self, name: str, parser: LogParser) -> None:
        """Register a named parser.

        Args:
            name: Name to register the parser under.
            parser: Parser instance to register.
        """
        self._parsers[name] = parser

    def get_parser(self, name: str) -> LogParser | None:
        """Get a parser by name.

        Args:
            name: Name of the parser to retrieve.

        Returns:
            Parser instance or None if not found.
        """
        return self._parsers.get(name)

    def parse_line(
        self,
        line: str,
        preferred_parser: str | None = None,
    ) -> ParsedLogRecord | None:
        """Parse a log line using the most appropriate parser.

        Args:
            line: Raw log line to parse.
            preferred_parser: Name of preferred parser to try first.

        Returns:
            ParsedLogRecord or None if no parser could handle the line.
        """
        # Try preferred parser first if specified
        if (
            preferred_parser
            and (parser := self.get_parser(preferred_parser))
            and (result := parser.parse(line)) is not None
        ):
            return result

        # Try all registered parsers
        for parser in self._parsers.values():
            if (result := parser.parse(line)) is not None:
                return result

        # Fall back to default parsers
        for parser in self._default_parsers:
            if (result := parser.parse(line)) is not None:
                return result

        return None


# Global parser factory instance
_parser_factory = LogParserFactory()


def get_parser_factory() -> LogParserFactory:
    """Get the global parser factory instance.

    Returns:
        The global LogParserFactory instance.
    """
    return _parser_factory
