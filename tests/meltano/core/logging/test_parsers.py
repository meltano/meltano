"""Tests for logging parsers module."""

from __future__ import annotations

import json
import logging
import typing as t
from unittest.mock import patch

import pytest

from meltano.core.logging.models import ParsedLogRecord, PluginException
from meltano.core.logging.parsers import (
    LogParser,
    LogParserFactory,
    PassthroughLogParser,
    SingerSDKLogParser,
    get_parser_factory,
)


class TestParsedLogRecord:
    """Test ParsedLogRecord dataclass."""

    def test_parsed_log_record_creation(self):
        """Test creating a ParsedLogRecord with all fields."""
        record = ParsedLogRecord(
            level=logging.INFO,
            message="Test message",
            extra={"key": "value"},
            timestamp="2023-12-20T10:00:00",
            logger_name="test.logger",
        )

        assert record.level == logging.INFO
        assert record.message == "Test message"
        assert record.extra == {"key": "value"}
        assert record.timestamp == "2023-12-20T10:00:00"
        assert record.logger_name == "test.logger"

    def test_parsed_log_record_with_defaults(self):
        """Test creating a ParsedLogRecord with minimal fields."""
        record = ParsedLogRecord(
            level=logging.ERROR,
            message="Error message",
            extra={},
        )

        assert record.level == logging.ERROR
        assert record.message == "Error message"
        assert record.extra == {}
        assert record.timestamp is None
        assert record.logger_name is None

    def test_parsed_log_record_immutable(self):
        """Test that ParsedLogRecord is immutable (frozen dataclass)."""
        record = ParsedLogRecord(
            level=logging.INFO,
            message="Test",
            extra={},
        )

        with pytest.raises(AttributeError):
            record.level = logging.ERROR

        with pytest.raises(AttributeError):
            record.message = "Changed"


class TestSingerSDKLogParser:
    """Test SingerSDKLogParser class."""

    @pytest.fixture
    def log(self) -> dict[str, t.Any]:
        """A valid Singer SDK log."""
        return {
            "level": "info",
            "pid": 12345,
            "logger_name": "tap_example.streams",
            "ts": 1703097600.123456,
            "thread_name": "MainThread",
            "app_name": "tap-example",
            "stream_name": "users",
            "message": "Processing records",
            "extra": {
                "custom_field": "custom_value",
            },
        }

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SingerSDKLogParser()

    def test_parse_valid_singer_sdk_log(self, log: dict[str, t.Any]):
        """Test parsing a valid Singer SDK JSON log line."""
        log_line = json.dumps(log)
        result = self.parser.parse(log_line)

        assert result is not None
        assert result.level == logging.INFO
        assert result.message == "Processing records"
        assert result.logger_name == "tap_example.streams"
        assert result.timestamp == "1703097600.123456"
        assert result.extra == {
            "pid": 12345,
            "thread_name": "MainThread",
            "app_name": "tap-example",
            "stream_name": "users",
            "custom_field": "custom_value",
        }

    def test_parse_unknown_log_level(self, log: dict[str, t.Any]):
        """Test parsing log with unknown log level falls back to INFO."""
        log["level"] = "UNKNOWN_LEVEL"
        log_line = json.dumps(log)

        result = self.parser.parse(log_line)

        assert result is not None
        assert result.level == logging.INFO  # Default fallback

    def test_parse_empty_line(self):
        """Test parsing empty line returns None."""
        result = self.parser.parse("")
        assert result is None

        result = self.parser.parse("   ")
        assert result is None

    def test_parse_non_json_line(self):
        """Test parsing non-JSON line returns None."""
        result = self.parser.parse("This is not JSON")
        assert result is None

        result = self.parser.parse("INFO - Some log message")
        assert result is None

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON returns None."""
        result = self.parser.parse('{"incomplete": json')
        assert result is None

        result = self.parser.parse("{invalid json}")
        assert result is None

    def test_parse_non_dict_json(self):
        """Test parsing JSON that's not a dict returns None."""
        result = self.parser.parse('["not", "a", "dict"]')
        assert result is None

        result = self.parser.parse('"just a string"')
        assert result is None

    def test_parse_missing_required_fields(self):
        """Test parsing JSON missing required fields returns None."""
        # Missing level
        result = self.parser.parse(
            json.dumps(
                {
                    "pid": 12345,
                    "logger_name": "test.logger",
                    "ts": 1703097600.123456,
                    "thread_name": "MainThread",
                    "app_name": "test",
                    "stream_name": "test",
                    "message": "Test",
                }
            )
        )
        assert result is None

        # Missing message
        result = self.parser.parse(
            json.dumps(
                {
                    "level": "info",
                    "logger_name": "test.logger",
                    "ts": 1703097600.123456,
                    "thread_name": "MainThread",
                    "app_name": "test",
                    "stream_name": "test",
                    "message": "Test",
                }
            )
        )
        assert result is None

    def test_parse_filters_core_fields_from_extra(self, log: dict[str, t.Any]):
        """Test that core logging fields are filtered from extra."""
        log["extra"]["my_custom_field"] = "should_be_in_extra"
        log_line = json.dumps(log)

        result = self.parser.parse(log_line)

        assert result is not None
        # Custom fields should be in extra
        assert result.extra["my_custom_field"] == "should_be_in_extra"

    def test_parse_type_error_handling(self):
        """Test handling of TypeError during parsing."""
        # Create a scenario that could cause TypeError
        log_line = json.dumps(
            {
                "levelname": None,  # This could cause issues with getattr
                "message": "Test",
                "name": "test.logger",
            }
        )

        result = self.parser.parse(log_line)
        assert result is None

    def test_parse_attribute_error_handling(self):
        """Test handling of AttributeError during parsing."""
        with patch("meltano.core.logging.parsers.getattr", side_effect=AttributeError):
            log_line = json.dumps(
                {
                    "levelname": "INFO",
                    "message": "Test",
                    "name": "test.logger",
                }
            )

            result = self.parser.parse(log_line)
            assert result is None

    def test_parse_line_without_braces(self):
        """Test that lines without JSON braces are quickly rejected."""
        result = self.parser.parse("No braces here")
        assert result is None

        result = self.parser.parse("{missing closing brace")
        assert result is None

        result = self.parser.parse("missing opening brace}")
        assert result is None


class TestPassthroughLogParser:
    """Test PassthroughLogParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PassthroughLogParser()

    def test_parse_normal_line(self):
        """Test parsing a normal log line."""
        line = "2023-12-20 10:00:00 | INFO | test.logger | Test message"
        result = self.parser.parse(line)

        assert result is not None
        assert result.level == logging.INFO
        assert result.message == line
        assert result.extra == {}
        assert result.timestamp is None
        assert result.logger_name is None

    def test_parse_empty_line(self):
        """Test parsing empty line returns None."""
        result = self.parser.parse("")
        assert result is None

        result = self.parser.parse("   ")
        assert result is None

    def test_parse_strips_whitespace(self):
        """Test that whitespace is stripped from input."""
        line = "  Test message with whitespace  "
        result = self.parser.parse(line)

        assert result is not None
        assert result.message == "Test message with whitespace"

    def test_parse_complex_line(self):
        """Test parsing a complex line with special characters."""
        line = "Complex log: {key: 'value', numbers: [1, 2, 3]}"
        result = self.parser.parse(line)

        assert result is not None
        assert result.level == logging.INFO
        assert result.message == line
        assert result.extra == {}


class TestLogParserFactory:
    """Test LogParserFactory class."""

    @pytest.fixture
    def log(self) -> dict[str, t.Any]:
        """A valid Singer SDK log."""
        return {
            "level": "info",
            "pid": 12345,
            "logger_name": "tap_example.streams",
            "ts": 1703097600.123456,
            "thread_name": "MainThread",
            "app_name": "tap-example",
            "stream_name": "users",
            "message": "Processing records",
            "extra": {
                "custom_field": "custom_value",
            },
        }

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = LogParserFactory()

    def test_factory_initialization(self):
        """Test that factory initializes with default parsers."""
        # Should have singer-sdk parser registered
        parser = self.factory.get_parser("singer-sdk")
        assert parser is not None
        assert isinstance(parser, SingerSDKLogParser)

        # Should have default parsers for fallback
        assert len(self.factory._default_parsers) > 0
        assert isinstance(self.factory._default_parsers[0], PassthroughLogParser)

    def test_register_and_get_parser(self):
        """Test registering and retrieving parsers."""
        custom_parser = PassthroughLogParser()
        self.factory.register_parser("custom", custom_parser)

        retrieved = self.factory.get_parser("custom")
        assert retrieved is custom_parser

    def test_get_nonexistent_parser(self):
        """Test getting a parser that doesn't exist returns None."""
        result = self.factory.get_parser("nonexistent")
        assert result is None

    def test_parse_line_with_preferred_parser(self):
        """Test parsing with a preferred parser."""

        # Register a custom parser that always returns a specific result
        class MockParser(LogParser):
            def parse(self, line: str) -> ParsedLogRecord | None:
                if line == "test":
                    return ParsedLogRecord(
                        level=logging.DEBUG,
                        message="mock result",
                        extra={"source": "mock"},
                    )
                return None

        mock_parser = MockParser()
        self.factory.register_parser("mock", mock_parser)

        result = self.factory.parse_line("test", preferred_parser="mock")
        assert result is not None
        assert result.message == "mock result"
        assert result.extra["source"] == "mock"

        result = self.factory.parse_line("foo", preferred_parser="mock")
        assert result is not None
        assert result.message == "foo"
        assert result.extra == {}
        assert result.level == logging.INFO
        assert result.timestamp is None
        assert result.logger_name is None

    def test_parse_line_preferred_parser_fails_fallback(self, log: dict[str, t.Any]):
        """Test that if preferred parser fails, it tries other parsers."""
        # Create a line that singer-sdk parser can handle
        line = json.dumps(log)

        # Try with a nonexistent preferred parser
        result = self.factory.parse_line(line, preferred_parser="nonexistent")

        # Should still parse with singer-sdk parser
        assert result is not None
        assert result.message == "Processing records"

    def test_parse_line_all_parsers_fail_uses_default(self):
        """Test that if all registered parsers fail, default parsers are used."""
        line = "Regular log line that can't be parsed as JSON"

        result = self.factory.parse_line(line)

        # Should be handled by PassthroughLogParser
        assert result is not None
        assert result.message == line
        assert result.level == logging.INFO

    def test_parse_line_empty_line(self):
        """Test parsing an empty line."""
        result = self.factory.parse_line("")
        assert result is None

        result = self.factory.parse_line("   ")
        assert result is None

    def test_parse_line_no_parsers_can_handle(self):
        """Test case where no parser can handle the line."""
        # Create a factory with no default parsers
        factory = LogParserFactory()
        factory._default_parsers = []

        # Add a parser that always returns None
        class FailingParser(LogParser):
            def parse(self, line: str) -> ParsedLogRecord | None:  # noqa: ARG002
                return None

        factory.register_parser("failing", FailingParser())

        result = factory.parse_line("any line")
        assert result is None

    def test_parse_line_tries_all_registered_parsers(self):
        """Test that parse_line tries all registered parsers in order."""
        parse_attempts = []

        class TrackingParser(LogParser):
            def __init__(self, name: str):
                self.name = name

            def parse(self, line: str) -> ParsedLogRecord | None:  # noqa: ARG002
                parse_attempts.append(self.name)
                return None

        factory = LogParserFactory()
        factory._default_parsers = []  # Remove defaults for cleaner test

        factory.register_parser("parser1", TrackingParser("parser1"))
        factory.register_parser("parser2", TrackingParser("parser2"))

        factory.parse_line("test line")

        # Should have tried all registered parsers
        assert "parser1" in parse_attempts
        assert "parser2" in parse_attempts

    def test_multiple_parser_registration(self):
        """Test registering multiple parsers and their retrieval."""
        parser1 = PassthroughLogParser()
        parser2 = SingerSDKLogParser()

        self.factory.register_parser("parser1", parser1)
        self.factory.register_parser("parser2", parser2)

        assert self.factory.get_parser("parser1") is parser1
        assert self.factory.get_parser("parser2") is parser2

    def test_parser_override(self):
        """Test that registering a parser with existing name overrides it."""
        original_parser = PassthroughLogParser()
        new_parser = SingerSDKLogParser()

        self.factory.register_parser("test", original_parser)
        assert self.factory.get_parser("test") is original_parser

        self.factory.register_parser("test", new_parser)
        assert self.factory.get_parser("test") is new_parser


class TestGlobalParserFactory:
    """Test global parser factory functions."""

    def test_get_parser_factory_returns_same_instance(self):
        """Test that get_parser_factory returns the same instance."""
        factory1 = get_parser_factory()
        factory2 = get_parser_factory()

        assert factory1 is factory2

    def test_global_factory_has_default_parsers(self):
        """Test that global factory is initialized with default parsers."""
        factory = get_parser_factory()

        # Should have singer-sdk parser
        singer_parser = factory.get_parser("singer-sdk")
        assert singer_parser is not None
        assert isinstance(singer_parser, SingerSDKLogParser)

    def test_global_factory_registration_persists(self):
        """Test that registrations on global factory persist."""
        factory = get_parser_factory()
        custom_parser = PassthroughLogParser()

        factory.register_parser("test_global", custom_parser)

        # Get factory again and check parser is still there
        factory2 = get_parser_factory()
        assert factory2.get_parser("test_global") is custom_parser


class TestLogParserIntegration:
    """Integration tests for parser interactions."""

    @pytest.fixture
    def log(self) -> dict[str, t.Any]:
        """A valid Singer SDK log."""
        return {
            "level": "info",
            "pid": 12345,
            "logger_name": "tap_example.streams",
            "ts": 1703097600.123456,
            "thread_name": "MainThread",
            "app_name": "tap-example",
            "stream_name": "users",
            "message": "Processing records",
            "extra": {
                "custom_field": "custom_value",
            },
        }

    def test_singer_sdk_to_passthrough_fallback(self):
        """Test fallback from Singer SDK parser to passthrough."""
        factory = LogParserFactory()

        # Non-JSON line should fall through to passthrough
        result = factory.parse_line("Regular log message")

        assert result is not None
        assert result.message == "Regular log message"
        assert result.level == logging.INFO

    def test_complex_singer_sdk_log_parsing(self):
        """Test parsing a complex Singer SDK log with all features."""
        complex_log = {
            "level": "error",
            "pid": 12345,
            "logger_name": "tap_example.client",
            "ts": 1703097600.789012,
            "thread_name": "MainThread",
            "app_name": "tap-example",
            "stream_name": None,
            "message": "API connection failed",
            "extra": {
                "phase": "discovery",
            },
            "exception": {
                "type": "Exception",
                "module": "tap_example.client",
                "message": "API connection failed",
            },
        }

        factory = LogParserFactory()
        result = factory.parse_line(json.dumps(complex_log))

        assert result is not None
        assert result.level == logging.ERROR
        assert result.message == "API connection failed"
        assert result.logger_name == "tap_example.client"
        assert result.timestamp == "1703097600.789012"
        assert isinstance(result.exception, PluginException)
        assert result.exception.type == "Exception"
        assert result.extra == {
            "pid": 12345,
            "thread_name": "MainThread",
            "app_name": "tap-example",
            "stream_name": None,
            "phase": "discovery",
        }

    def test_all_log_levels_parsing(self, log: dict[str, t.Any]):
        """Test parsing all standard log levels."""
        factory = LogParserFactory()
        levels = ["debug", "info", "warning", "error", "critical"]

        for level_name in levels:
            log["level"] = level_name
            log_line = json.dumps(log)

            result = factory.parse_line(log_line)
            assert result is not None
            assert result.level == getattr(logging, level_name.upper())

    def test_edge_case_field_values(self):
        """Test parsing with edge case field values."""
        edge_cases = [
            {"level": "", "message": "", "logger_name": ""},  # Empty strings
            {"level": "INFO", "message": None, "logger_name": "test"},  # None message
            {
                "level": "INFO",
                "message": 123,  # Non-string message
                "logger_name": "test",
            },
        ]

        factory = LogParserFactory()

        assert all(
            isinstance(
                factory.parse_line(json.dumps(case)),
                ParsedLogRecord,
            )
            for case in edge_cases
        )
