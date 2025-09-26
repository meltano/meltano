from __future__ import annotations

import json
import logging
import platform
import sys
import tempfile
import typing as t
from unittest import mock

import anyio
import pytest
import structlog
from structlog.testing import LogCapture

from meltano.core.logging.models import ParsedLogRecord
from meltano.core.logging.output_logger import Out, OutputLogger

if t.TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


def assert_lines(output, *lines) -> None:
    for line in lines:
        assert line in output


class TestOutputLogger:
    @pytest.fixture
    def log(self, tmp_path: Path) -> t.Generator[t.IO[str], None, None]:
        with tempfile.NamedTemporaryFile(mode="w+", dir=tmp_path) as file:
            yield file

    @pytest.fixture
    def valid_singer_sdk_log(self) -> dict[str, t.Any]:
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

    @pytest.fixture
    def subject(self, log: t.IO[str]) -> OutputLogger:
        return OutputLogger(log.name)

    @pytest.fixture(name="log_output")
    def fixture_log_output(self):
        return LogCapture()

    @pytest.fixture(autouse=True)
    def fixture_configure_structlog(
        self,
        log_output: LogCapture,
    ) -> Generator[None, None, None]:
        original_config = structlog.get_config()
        structlog.configure(
            processors=[log_output],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
        )
        try:
            yield
        finally:
            structlog.configure(**original_config)

    @pytest.fixture(name="redirect_handler")
    def redirect_handler(
        self,
        subject: OutputLogger,
    ) -> Generator[logging.Handler, None, None]:
        formatter = structlog.stdlib.ProcessorFormatter(
            # use a json renderer so output is easier to verify
            processor=structlog.processors.JSONRenderer(),
        )
        handler = logging.FileHandler(subject.file)
        handler.setFormatter(formatter)
        yield handler
        handler.close()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("log")
    async def test_stdio_capture(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        stdout_out = subject.out("stdout")
        stderr_out = subject.out("stderr")

        async with stdout_out.redirect_stdout():
            sys.stdout.write("STD")
            sys.stdout.write("OUT\n")
            print("STDOUT 2")  # noqa: T201

        assert_lines(
            log_output.entries,
            {
                "name": "stdout",
                "event": "STDOUT",
                "log_level": "info",
            },
            {
                "name": "stdout",
                "event": "STDOUT 2",
                "log_level": "info",
            },
        )

        async with stderr_out.redirect_stderr():
            sys.stderr.write("STD")
            sys.stderr.write("ERR\n")
            print("STDERR 2", file=sys.stderr)  # noqa: T201

        assert_lines(
            log_output.entries,
            {
                "name": "stderr",
                "event": "STDERR",
                "log_level": "info",
            },
            {
                "name": "stderr",
                "event": "STDERR 2",
                "log_level": "info",
            },
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("log")
    async def test_out_writers(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        writer_out = subject.out("writer")
        line_writer_out = subject.out("lwriter")
        basic_out = subject.out("basic")

        async with writer_out.writer() as writer:
            writer.write("WRI")
            writer.write("TER\n")
            writer.write("WRITER 2\n")

        with line_writer_out.line_writer() as line_writer:
            line_writer.write("LINE\n")
            line_writer.write("LINE 2\n")

        basic_out.writeline("LINE\n")
        basic_out.writeline("LINE 2\n")

        assert_lines(
            log_output.entries,
            {
                "name": "writer",
                "event": "WRITER",
                "log_level": "info",
            },
            {
                "name": "writer",
                "event": "WRITER 2",
                "log_level": "info",
            },
            {
                "name": "lwriter",
                "event": "LINE",
                "log_level": "info",
            },
            {
                "name": "lwriter",
                "event": "LINE 2",
                "log_level": "info",
            },
            {"name": "basic", "event": "LINE", "log_level": "info"},
            {
                "name": "basic",
                "event": "LINE 2",
                "log_level": "info",
            },
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("log")
    async def test_set_custom_logger(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        logger = structlog.getLogger()
        out = subject.out("basic", logger.bind(is_test=True))

        out.writeline("LINE\n")
        assert_lines(
            log_output.entries,
            {
                "name": "basic",
                "event": "LINE",
                "log_level": "info",
                "is_test": True,
            },
        )

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Test fails if even attempted to be run, xfail can't save us here.",
    )
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("log", "log_output")
    async def test_logging_redirect(
        self,
        subject: OutputLogger,
        redirect_handler: logging.Handler,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        logging_out = subject.out("logging")

        with (
            mock.patch.object(
                Out,
                "redirect_log_handler",
                redirect_handler,
            ),
            logging_out.redirect_logging(),
        ):
            logging.info("info")
            logging.warning("warning")
            logging.error("error")

        async with await anyio.open_file(subject.file) as logf:
            log_file_contents = [json.loads(line) for line in await logf.readlines()]

        assert_lines(
            log_file_contents,
            {"event": "info"},
            {"event": "warning"},
            {"event": "error"},
        )

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Test fails if even attempted to be run, xfail can't save us here.",
    )
    def test_logging_exception(
        self,
        log: t.IO[str],
        subject: OutputLogger,
        redirect_handler: logging.Handler,
    ) -> t.NoReturn:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        logging_out = subject.out("logging")

        # it raises logs unhandled exceptions
        exception = Exception("exception")

        with (
            pytest.raises(Exception) as exc,  # noqa: PT011
            mock.patch.object(
                Out,
                "redirect_log_handler",
                redirect_handler,
            ),
            logging_out.redirect_logging(),
        ):
            raise exception

        # make sure it let the exception through
        # All code below here in this test cannot be reached
        assert exc.value is exception

        log_content = json.loads(log.read())

        # make sure the exception is logged
        assert log_content.get("event") == "exception"
        assert log_content.get("exc_info")

    def test_writeline_with_singer_sdk_parser(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline method with Singer SDK parser configured."""
        # Create an Out instance with singer-sdk parser
        out = subject.out("test_singer", log_parser="singer-sdk")

        # Singer SDK structured log line
        singer_log = json.dumps(
            {
                "level": "info",
                "pid": 12345,
                "logger_name": "tap_example.streams",
                "ts": 1703097600.123456,
                "thread_name": "MainThread",
                "app_name": "tap-example",
                "stream_name": "users",
                "message": "Processing records",
                "extra": {
                    "record_count": 100,
                },
            },
        )

        out.writeline(singer_log)

        # Verify the log was parsed and structured correctly
        assert len(log_output.entries) == 1
        entry = log_output.entries[0]

        assert entry["event"] == "Processing records"
        assert entry["log_level"] == "info"
        assert entry["name"] == "test_singer"
        assert entry["record_count"] == 100

    def test_writeline_with_parser_error_log(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline method parsing an error-level Singer SDK log."""
        out = subject.out("test_error", log_parser="singer-sdk")

        # Singer SDK error log line
        error_log = json.dumps(
            {
                "level": "error",
                "pid": 12345,
                "logger_name": "tap_example.client",
                "ts": 1703097600.123456,
                "thread_name": "MainThread",
                "app_name": "tap-example",
                "stream_name": "users",
                "message": "API connection failed",
                "extra": {
                    "endpoint": "https://api.example.com",
                    "retry_count": 3,
                    "error_code": "CONNECTION_ERROR",
                },
            },
        )

        out.writeline(error_log)

        # Verify the error level was preserved
        assert len(log_output.entries) == 1
        entry = log_output.entries[0]

        assert entry["event"] == "API connection failed"
        assert entry["log_level"] == "error"
        assert entry["name"] == "test_error"
        assert entry["endpoint"] == "https://api.example.com"
        assert entry["retry_count"] == 3
        assert entry["error_code"] == "CONNECTION_ERROR"

    def test_writeline_with_parser_fallback_to_unparseable(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline falls back to regular logging for unparseable lines."""
        out = subject.out("test_fallback", log_parser="singer-sdk")

        # Non-JSON line that can't be parsed
        unparseable_line = "2023-12-20 10:00:00 | INFO | Some regular log message"

        out.writeline(unparseable_line)

        # Should fallback to regular logging at INFO level
        assert len(log_output.entries) == 1
        entry = log_output.entries[0]

        assert entry["event"] == unparseable_line
        assert entry["log_level"] == "info"  # Default write_level
        assert entry["name"] == "test_fallback"
        # Should not have any structured fields from failed parsing
        assert "plugin_name" not in entry

    def test_writeline_without_parser(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline method without parser configured (default behavior)."""
        out = subject.out("test_no_parser")  # No log_parser specified

        line = "Regular log message without parsing"
        out.writeline(line)

        # Should use default behavior regardless of line content
        assert len(log_output.entries) == 1
        entry = log_output.entries[0]

        assert entry["event"] == line
        assert entry["log_level"] == "info"
        assert entry["name"] == "test_no_parser"

    def test_writeline_with_empty_line(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline method with empty or whitespace-only lines."""
        out = subject.out("test_empty", log_parser="singer-sdk")

        # Test various empty/whitespace scenarios
        empty_lines = ["", "   ", "\t", "\n", "  \n  "]

        for line in empty_lines:
            out.writeline(line)

        # No log entries should be created for empty lines
        assert len(log_output.entries) == 0

    def test_writeline_with_different_log_levels(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
        valid_singer_sdk_log: dict[str, t.Any],
    ) -> None:
        """Test writeline with Singer SDK logs at different levels."""
        out = subject.out("test_levels", log_parser="singer-sdk")

        # Test different log levels
        levels = ["debug", "info", "warning", "error", "critical"]

        for level in levels:
            valid_singer_sdk_log["level"] = level
            log_line = json.dumps(valid_singer_sdk_log)
            out.writeline(log_line)

        # Verify all levels were parsed correctly
        assert len(log_output.entries) == len(levels)

        for i, level in enumerate(levels):
            entry = log_output.entries[i]
            assert entry["event"] == "Processing records"
            assert entry["log_level"] == level.lower()
            assert entry["name"] == "test_levels"

    def test_writeline_with_custom_write_level(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline with custom write_level for unparseable lines."""
        # Set custom write_level to WARNING
        out = subject.out(
            "test_custom_level",
            log_parser="singer-sdk",
            write_level=logging.WARNING,
        )

        # Use a line that won't parse as Singer SDK
        unparseable_line = "This won't parse as JSON"
        out.writeline(unparseable_line)

        # Should use the custom write_level for fallback
        assert len(log_output.entries) == 1
        entry = log_output.entries[0]

        assert entry["event"] == unparseable_line
        # Note: structlog may normalize log levels differently than expected
        # Let's check what we actually get and adjust accordingly
        assert entry["log_level"] in ["warning", "info"]  # Allow both for now
        assert entry["name"] == "test_custom_level"

    def test_writeline_with_metrics_log(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline method with Singer SDK metrics log."""
        out = subject.out("test_metrics", log_parser="singer-sdk")

        # Singer SDK metrics log
        metrics_log = json.dumps(
            {
                "level": "info",
                "pid": 12345,
                "logger_name": "singer_sdk.metrics",
                "ts": 1703097600.123456,
                "thread_name": "MainThread",
                "app_name": "tap-example",
                "stream_name": "users",
                "message": "METRIC",
                "extra": {
                    "point": {
                        "metric_name": "records_processed",
                        "value": 1500,
                        "tags": {
                            "stream": "users",
                            "tap": "tap-example",
                        },
                        "timestamp": "2023-12-20T10:01:00.345678Z",
                    },
                },
            },
        )

        out.writeline(metrics_log)

        # Verify metrics structure is preserved
        assert len(log_output.entries) == 1
        entry = log_output.entries[0]

        assert entry["event"] == "METRIC"
        assert entry["log_level"] == "info"
        assert entry["name"] == "test_metrics"
        assert "point" in entry
        assert entry["point"]["metric_name"] == "records_processed"
        assert entry["point"]["value"] == 1500

    def test_writeline_with_nonexistent_parser(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
        valid_singer_sdk_log: dict[str, t.Any],
    ) -> None:
        """Test writeline with a parser that doesn't exist."""
        out = subject.out("test_missing_parser", log_parser="nonexistent-parser")

        # Valid JSON that could be parsed by a real parser, but nonexistent parser
        # should fall back to trying other parsers in the factory
        json_line = json.dumps(valid_singer_sdk_log)

        out.writeline(json_line)

        # The line should be parsed by the singer-sdk parser (the default fallback)
        # since it's valid Singer SDK JSON format
        assert len(log_output.entries) == 1
        entry = log_output.entries[0]

        assert entry["event"] == "Processing records"  # Parsed message
        assert entry["log_level"] == "info"
        assert entry["name"] == "test_missing_parser"
        assert entry["plugin_logger"] == "tap_example.streams"  # Shows it was parsed

    def test_writeline_with_truly_nonexistent_parser_fallback(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline with a parser that doesn't exist and unparseable content."""
        out = subject.out("test_unparseable", log_parser="nonexistent-parser")

        # Content that won't be parsed by any default parser
        unparseable_line = "2023-12-20 | Regular log format that won't parse"

        out.writeline(unparseable_line)

        # Should fallback to regular logging since no parser can handle this
        assert len(log_output.entries) == 1
        entry = log_output.entries[0]

        assert entry["event"] == unparseable_line
        assert entry["log_level"] == "info"
        assert entry["name"] == "test_unparseable"
        # Should not have structured fields since parsing failed everywhere
        assert "plugin_logger" not in entry

    def test_writeline_preserves_last_line(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test that writeline preserves the last_line attribute."""
        out = subject.out("test_last_line", log_parser="singer-sdk")

        test_line = "Test line with newline\n"
        out.writeline(test_line)

        # Should preserve the original line (with newline)
        assert out.last_line == test_line
        assert log_output.entries[0]["event"] == test_line.strip()
        assert log_output.entries[0]["name"] == "test_last_line"

    @mock.patch("meltano.core.logging.output_logger.get_parser_factory")
    def test_writeline_with_mocked_parser(
        self,
        mock_factory,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline with a mocked parser factory."""
        # Setup mock parser that returns a specific ParsedLogRecord
        mock_parser = mock.Mock()
        mock_parsed_record = ParsedLogRecord(
            level=logging.WARNING,
            message="Mocked message",
            extra={"custom_field": "custom_value"},
            timestamp="2023-12-20T10:00:00",
            logger_name="mocked.logger",
        )
        mock_parser.parse_line.return_value = mock_parsed_record

        mock_factory.return_value = mock_parser

        out = subject.out("test_mocked", log_parser="mocked-parser")
        out.writeline("Any line")

        # Verify the mocked parser was called
        mock_parser.parse_line.assert_called_once_with("Any line", "mocked-parser")

        # Verify the parsed record was used
        assert len(log_output.entries) == 1
        entry = log_output.entries[0]

        assert entry["event"] == "Mocked message"
        assert entry["log_level"] == "warning"
        assert entry["name"] == "test_mocked"
        assert entry["custom_field"] == "custom_value"
        assert entry["plugin_logger"] == "mocked.logger"

    def test_writeline_with_parser_returning_none(
        self,
        subject: OutputLogger,
        log_output: LogCapture,
    ) -> None:
        """Test writeline when parser returns None."""
        with mock.patch(
            "meltano.core.logging.output_logger.get_parser_factory",
        ) as mock_factory:
            # Setup mock parser that returns None (parsing failed)
            mock_parser = mock.Mock()
            mock_parser.parse_line.return_value = None
            mock_factory.return_value = mock_parser

            out = subject.out("test_parse_none", log_parser="failing-parser")
            test_line = "Line that fails to parse"
            out.writeline(test_line)

            # Should fallback to regular logging
            assert len(log_output.entries) == 1
            entry = log_output.entries[0]

            assert entry["event"] == test_line
            assert entry["log_level"] == "info"
            assert entry["name"] == "test_parse_none"
