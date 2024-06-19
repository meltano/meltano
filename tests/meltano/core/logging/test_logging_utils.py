from __future__ import annotations

import asyncio
import datetime
import logging
import sys

import pytest
import time_machine

from meltano.core.logging.utils import (
    LogFormat,
    capture_subprocess_output,
    default_config,
)

if sys.version_info >= (3, 9):
    import zoneinfo
else:
    from backports import zoneinfo


class AsyncReader(asyncio.StreamReader):
    def __init__(self, lines: list[bytes]):
        self.lines = lines

    def at_eof(self) -> bool:
        return not self.lines

    async def readline(self) -> bytes:
        return self.lines.pop(0) if self.lines else b""


@pytest.mark.asyncio()
async def test_capture_subprocess_output() -> None:
    input_lines = [b"LINE\n", b"LINE 2\n", b"\xed\n"]
    output_lines = []

    class LineWriter:
        def writeline(self, line: str) -> None:
            output_lines.append(line)

    reader = AsyncReader(input_lines)

    await capture_subprocess_output(reader, LineWriter())
    assert output_lines == ["LINE\n", "LINE 2\n", "�\n"]


@pytest.mark.parametrize(
    ("log_format", "expected"),
    (
        pytest.param(
            LogFormat.colored,
            "\x1b[2m2021-01-01T00:00:00Z\x1b[0m [\x1b[32m\x1b[1minfo     \x1b[0m] \x1b[1mtest                          \x1b[0m",  # noqa: E501
            id="colored",
        ),
        pytest.param(
            LogFormat.uncolored,
            "2021-01-01T00:00:00Z [info     ] test",
            id="uncolored",
        ),
        pytest.param(
            LogFormat.json,
            '{"event": "test", "level": "info", "timestamp": "2021-01-01T00:00:00Z"}',
            id="json",
        ),
        pytest.param(
            LogFormat.key_value,
            "timestamp='2021-01-01T00:00:00Z' level='info' event='test' logger=None",
            id="key_value",
        ),
        pytest.param(
            "_unknown_",
            "[2021-01-01 00:00:00,000] [95803|MainThread|test_logger] [INFO] test",
            id="unknown",
        ),
    ),
)
def test_default_logging_config_format(
    log_format: LogFormat,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    config = default_config("info", log_format=log_format)
    assert log_format in config["formatters"]
    assert config["handlers"]["console"]["formatter"] == log_format
    assert config["loggers"][""]["level"] == "INFO"

    # Create a logger that uses the config
    formatter_config = config["formatters"][log_format]
    formatter_class = formatter_config.pop("()")
    formatter = formatter_class(**formatter_config)

    # Mock current time and process ID
    with time_machine.travel(
        datetime.datetime(2021, 1, 1, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("UTC")),
        tick=False,
    ), monkeypatch.context() as m:
        m.setattr("os.getpid", lambda: 95803)
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )

        # Test the formatted message
        formatted = formatter.format(record)
        assert formatted == expected
