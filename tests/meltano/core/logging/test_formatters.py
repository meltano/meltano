from __future__ import annotations

import datetime
import json
import logging
import os
import platform
import re
import sys
import typing as t
import zoneinfo
from types import TracebackType

import pytest
import structlog.exceptions
import time_machine

from meltano.core.logging import formatters

if t.TYPE_CHECKING:
    from pathlib import Path

ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")
ExcInfo: t.TypeAlias = tuple[type[BaseException], BaseException, TracebackType]
OptExcInfo: t.TypeAlias = ExcInfo | tuple[None, None, None]


@pytest.fixture
def exc_info() -> OptExcInfo:
    """Fake a valid exc_info."""
    my_var = "my_value"  # noqa: F841
    try:
        raise ValueError("Not a real error")  # noqa: EM101, TRY003, TRY301
    except ValueError:
        return sys.exc_info()


@pytest.fixture
def deep_exc_info() -> OptExcInfo | None:
    """Create a deeper call stack for testing max_frames."""

    def level_5():
        local_var_5 = "level_5_value"  # noqa: F841
        raise ValueError("Deep stack error")  # noqa: EM101, TRY003

    def level_4():
        local_var_4 = "level_4_value"  # noqa: F841
        level_5()

    def level_3():
        local_var_3 = "level_3_value"  # noqa: F841
        level_4()

    def level_2():
        local_var_2 = "level_2_value"  # noqa: F841
        level_3()

    def level_1():
        local_var_1 = "level_1_value"  # noqa: F841
        level_2()

    try:
        level_1()
    except ValueError:
        return sys.exc_info()


class TestLogFormatters:
    """Test the log formatters."""

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Setup the test."""
        monkeypatch.delenv("FORCE_COLOR", raising=False)

    @pytest.fixture
    def isolated_logger(self):
        """A stdlib logger whose level is restored after the test.

        Some formatters consult the logger level (e.g. ``filter_by_level``), so
        the plain formatter tests need to set it. Stdlib loggers are global
        singletons, so the level is restored afterwards to avoid leaking state
        into other tests that share the ``test`` logger name.
        """
        logger = logging.getLogger("test")  # noqa: TID251
        original_level = logger.level
        try:
            yield logger
        finally:
            logger.setLevel(original_level)

    @pytest.fixture
    def record(self):
        rec = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/path/to/my_module.py",
            lineno=1,
            msg="test",
            args=None,
            exc_info=None,
            func="my_func",
        )
        rec.__dict__["extra_int"] = 1
        rec.__dict__["extra_str"] = "foo"
        return rec

    @pytest.fixture
    def record_with_exception(self, exc_info: ExcInfo, tmp_path: Path):
        path = tmp_path / "my_module.py"
        path.write_text("cause_an_error()\n")

        return logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test",
            lineno=1,
            msg="test",
            args=None,
            exc_info=exc_info,
        )

    @pytest.fixture
    def record_with_deep_exception(self, deep_exc_info: ExcInfo):
        return logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test",
            lineno=1,
            msg="deep stack test",
            args=None,
            exc_info=deep_exc_info,
        )

    def test_console_log_formatter_colors(self, record, monkeypatch) -> None:
        monkeypatch.delenv("NO_COLOR", raising=False)
        formatter = formatters.console_log_formatter(colors=True)
        assert ANSI_RE.match(formatter.format(record))

    def test_console_log_formatter_no_colors(self, record) -> None:
        formatter = formatters.console_log_formatter(colors=False)
        assert not ANSI_RE.match(formatter.format(record))

    def test_console_log_formatter_no_locals(self, record_with_exception) -> None:
        formatter = formatters.console_log_formatter(show_locals=False)
        output = formatter.format(record_with_exception)
        assert "locals" not in output
        assert "my_var = 'my_value'" not in output

    def test_console_log_formatter_show_locals(self, record_with_exception) -> None:
        formatter = formatters.console_log_formatter(show_locals=True)
        output = formatter.format(record_with_exception)
        assert "locals" in output
        assert "my_var = 'my_value'" in output

    def test_console_log_formatter_max_frames(self, record_with_deep_exception) -> None:
        # Test that max_frames limits the number of frames shown
        formatter_limited = formatters.console_log_formatter(max_frames=2)
        output_limited = formatter_limited.format(record_with_deep_exception)
        assert "frames hidden" in output_limited

        # Test that high max_frames shows all frames
        formatter_unlimited = formatters.console_log_formatter(max_frames=100)
        output_unlimited = formatter_unlimited.format(record_with_deep_exception)
        assert "frames hidden" not in output_unlimited
        assert output_unlimited.count("in level_") == 5

        # Test that max_frames=0 shows all frames (unlimited)
        formatter_zero = formatters.console_log_formatter(max_frames=0)
        output_zero = formatter_zero.format(record_with_deep_exception)
        assert "frames hidden" not in output_zero
        assert output_zero.count("in level_") == 5

    def test_console_log_formatter_include_keys(self, record) -> None:
        record.foo = "bar"
        record.baz = "qux"

        formatter = formatters.console_log_formatter()
        output = formatter.format(record)
        assert "foo=bar" not in output
        assert "baz=qux" not in output
        assert "extra_int=1" not in output
        assert "extra_str=foo" not in output

        formatter = formatters.console_log_formatter(include_keys=["foo", "extra_int"])
        output = formatter.format(record)
        assert "foo=bar" in output
        assert "baz=qux" not in output
        assert "extra_int=1" in output
        assert "extra_str=foo" not in output

        formatter = formatters.console_log_formatter(all_keys=True)
        output = formatter.format(record)
        assert "foo=bar" in output
        assert "baz=qux" in output
        assert "extra_int=1" in output
        assert "extra_str=foo" in output

    def test_key_value_formatter(self, record):
        formatter = formatters.key_value_formatter()
        output = formatter.format(record)
        assert "event='test' level='info'" in output
        assert "pathname='/path/to/my_module.py'" not in output

        formatter = formatters.key_value_formatter(callsite_parameters=True)
        output = formatter.format(record)
        assert "pathname='/path/to/my_module.py'" in output
        assert "lineno=1" in output
        assert "func_name='my_func'" in output
        assert f"process={os.getpid()}" in output

    def test_json_formatter_extra(self, record) -> None:
        formatter = formatters.json_formatter()
        output = formatter.format(record)
        message_dict = json.loads(output)
        assert message_dict["extra_int"] == 1
        assert message_dict["extra_str"] == "foo"

    def test_json_formatter_callsite_parameters(self, record):
        formatter = formatters.json_formatter(callsite_parameters=True)
        output = formatter.format(record)
        message_dict = json.loads(output)
        assert message_dict["pathname"] == "/path/to/my_module.py"
        assert message_dict["lineno"] == 1
        assert message_dict["func_name"] == "my_func"
        assert message_dict["process"] == os.getpid()

    def test_json_formatter_exception(self, record_with_exception) -> None:
        formatter = formatters.json_formatter()
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)

        assert "exception" in message_dict

        exception_list = message_dict["exception"]
        assert isinstance(exception_list, list)
        assert len(exception_list) == 1
        assert exception_list[0]["exc_type"] == "ValueError"
        assert exception_list[0]["exc_value"] == "Not a real error"

        formatter = formatters.json_formatter(dict_tracebacks=False)
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)

        assert "exception" not in message_dict

    @time_machine.travel(
        datetime.datetime(2025, 7, 5, 15, tzinfo=zoneinfo.ZoneInfo("America/New_York")),
        tick=False,
    )
    @pytest.mark.xfail(
        platform.system() == "Windows",
        reason="time-machine can't mock the timezone on Windows",
        strict=True,
    )
    def test_json_formatter_utc(
        self,
        record_with_exception,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        value_utc = "2025-07-05T19:00:00Z"
        value_local = "2025-07-05T15:00:00"

        monkeypatch.delenv("NO_UTC", raising=False)
        formatter = formatters.json_formatter()
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)
        assert "timestamp" in message_dict
        assert message_dict["timestamp"] == value_utc

        monkeypatch.setenv("NO_UTC", "1")
        formatter = formatters.json_formatter()
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)
        assert "timestamp" in message_dict
        assert message_dict["timestamp"] == value_local

        # Test with NO_UTC set to an unexpected value ("foobar")
        monkeypatch.setenv("NO_UTC", "foobar")
        formatter = formatters.json_formatter()
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)
        assert "timestamp" in message_dict
        # Should fallback to UTC, so endswith("Z") should be True
        assert message_dict["timestamp"] == value_utc

        # Test with NO_UTC set to "0"
        monkeypatch.setenv("NO_UTC", "0")
        formatter = formatters.json_formatter()
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)
        assert "timestamp" in message_dict
        # Should fallback to UTC, so endswith("Z") should be True
        assert message_dict["timestamp"] == value_utc

        # Test with NO_UTC set to ""
        monkeypatch.setenv("NO_UTC", "")
        formatter = formatters.json_formatter()
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)
        assert "timestamp" in message_dict
        assert message_dict["timestamp"] == value_utc

    def test_json_formatter_locals(self, record_with_exception) -> None:
        formatter = formatters.json_formatter(show_locals=True)
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)
        assert "locals" in message_dict["exception"][0]["frames"][0]

        formatter = formatters.json_formatter(show_locals=False)
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)
        assert "locals" not in message_dict["exception"][0]["frames"][0]

    def test_google_cloud_logging_formatter_severity_and_message(self, record) -> None:
        formatter = formatters.json_formatter(preset="google-cloud-logging")
        message_dict = json.loads(formatter.format(record))

        # GCL special fields are present...
        assert message_dict["severity"] == "INFO"
        assert message_dict["message"] == "test"
        assert "timestamp" in message_dict

        # ...and the structlog-native keys they replace are gone.
        assert "level" not in message_dict
        assert "event" not in message_dict

    def test_google_cloud_logging_formatter_severity_levels(self) -> None:
        formatter = formatters.json_formatter(preset="google-cloud-logging")
        for level, severity in (
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ):
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="/path/to/my_module.py",
                lineno=1,
                msg="test",
                args=None,
                exc_info=None,
            )
            message_dict = json.loads(formatter.format(record))
            assert message_dict["severity"] == severity
            assert "level" not in message_dict

    def test_google_cloud_logging_formatter_source_location(self, record) -> None:
        # Without callsite parameters there is no source location.
        formatter = formatters.json_formatter(preset="google-cloud-logging")
        message_dict = json.loads(formatter.format(record))
        assert "logging.googleapis.com/sourceLocation" not in message_dict

        # With callsite parameters the source location is populated.
        formatter = formatters.json_formatter(
            preset="google-cloud-logging",
            callsite_parameters=True,
        )
        message_dict = json.loads(formatter.format(record))
        assert isinstance(message_dict.get("process"), int)

        source_location = message_dict["logging.googleapis.com/sourceLocation"]
        assert source_location["file"] == "/path/to/my_module.py"
        assert source_location["line"] == "1"
        assert source_location["function"] == "my_func"

    def test_google_cloud_logging_formatter_exception(
        self,
        record_with_exception,
    ) -> None:
        formatter = formatters.json_formatter(preset="google-cloud-logging")
        message_dict = json.loads(formatter.format(record_with_exception))

        assert message_dict["severity"] == "ERROR"
        assert message_dict["message"] == "test"

        exception_list = message_dict["exception"]
        assert isinstance(exception_list, list)
        assert exception_list[0]["exc_type"] == "ValueError"
        assert exception_list[0]["exc_value"] == "Not a real error"

        formatter = formatters.json_formatter(
            preset="google-cloud-logging",
            dict_tracebacks=False,
        )
        message_dict = json.loads(formatter.format(record_with_exception))
        assert "exception" not in message_dict

    def test_google_cloud_logging_formatter_locals(
        self,
        record_with_exception,
    ) -> None:
        formatter = formatters.json_formatter(
            preset="google-cloud-logging",
            show_locals=True,
        )
        message_dict = json.loads(formatter.format(record_with_exception))
        assert "locals" in message_dict["exception"][0]["frames"][0]

        formatter = formatters.json_formatter(
            preset="google-cloud-logging",
            show_locals=False,
        )
        message_dict = json.loads(formatter.format(record_with_exception))
        assert "locals" not in message_dict["exception"][0]["frames"][0]

    def test_json_formatter_unknown_preset(self) -> None:
        with pytest.raises(ValueError, match="Unknown json_formatter preset"):
            formatters.json_formatter(preset="not-a-real-preset")

    def test_plain_formatter(self, record, isolated_logger) -> None:
        formatter = formatters.plain_formatter(fmt="%(levelname)s %(name)s")
        formatter.logger = isolated_logger
        formatter.logger.setLevel(logging.INFO)
        output = formatter.format(record)
        assert output == "INFO test"

    def test_plain_formatter_drop_event(self, record, isolated_logger) -> None:
        formatter = formatters.plain_formatter(fmt="%(levelname)s %(name)s")
        formatter.logger = isolated_logger
        formatter.logger.setLevel(logging.WARNING)

        with pytest.raises(structlog.exceptions.DropEvent):
            formatter.format(record)
