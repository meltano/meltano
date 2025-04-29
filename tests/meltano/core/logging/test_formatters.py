from __future__ import annotations

import json
import logging
import os
import re
import sys
import typing as t
from types import TracebackType

import pytest
import structlog.exceptions

from meltano.core.logging import formatters

if sys.version_info < (3, 11):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias  # noqa: ICN003

if t.TYPE_CHECKING:
    from pathlib import Path

ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")
ExcInfo: TypeAlias = t.Union[
    tuple[type[BaseException], BaseException, TracebackType], tuple[None, None, None]
]


@pytest.fixture
def exc_info() -> ExcInfo:
    """Fake a valid exc_info."""
    my_var = "my_value"  # noqa: F841
    try:
        raise ValueError("Not a real error")  # noqa: EM101
    except ValueError:
        return sys.exc_info()


class TestLogFormatters:
    """Test the log formatters."""

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Setup the test."""
        monkeypatch.delenv("FORCE_COLOR", raising=False)

    @pytest.fixture
    def record(self):
        return logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/path/to/my_module.py",
            lineno=1,
            msg="test",
            args=None,
            exc_info=None,
            func="my_func",
        )

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

    def test_json_formatter_locals(self, record_with_exception) -> None:
        formatter = formatters.json_formatter(show_locals=True)
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)
        assert "locals" in message_dict["exception"][0]["frames"][0]

        formatter = formatters.json_formatter(show_locals=False)
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)
        assert "locals" not in message_dict["exception"][0]["frames"][0]

    def test_plain_formatter(self, record) -> None:
        formatter = formatters.plain_formatter(fmt="%(levelname)s %(name)s")
        formatter.logger = logging.getLogger("test")  # noqa: TID251
        formatter.logger.setLevel(logging.INFO)
        output = formatter.format(record)
        assert output == "INFO test"

    def test_plain_formatter_drop_event(self, record) -> None:
        formatter = formatters.plain_formatter(fmt="%(levelname)s %(name)s")
        formatter.logger = logging.getLogger("test")  # noqa: TID251
        formatter.logger.setLevel(logging.WARNING)

        with pytest.raises(structlog.exceptions.DropEvent):
            formatter.format(record)
