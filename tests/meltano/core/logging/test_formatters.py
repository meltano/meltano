from __future__ import annotations

import json
import logging
import re
import typing as t
from types import TracebackType

import pytest

from meltano.core.logging import formatters

if t.TYPE_CHECKING:
    from pathlib import Path

ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")


class FakeCode:
    """A fake code object that can be used to test log formatters."""

    def __init__(self, co_filename, co_name) -> None:
        self.co_filename = co_filename
        self.co_name = co_name

    def co_positions(self):
        yield 0, 10, 0, 40


class FakeFrame:
    """A fake traceback frame that can be used to test log formatters."""

    def __init__(self, f_code, f_globals, f_locals=None) -> None:
        self.f_code = f_code
        self.f_globals = f_globals
        self.f_locals = f_locals or {}
        self.f_lasti = 0


class FakeTraceback:  # pragma: no cover
    """A fake traceback that can be used to test log formatters."""

    def __init__(self, frames, line_nums) -> None:
        if len(frames) != len(line_nums):
            raise ValueError("Ya messed up!")  # noqa: EM101
        self._frames = frames
        self._line_nums = line_nums
        self.tb_frame = frames[0]
        self.tb_lineno = line_nums[0]

    @property
    def tb_next(self):
        if len(self._frames) > 1:  # noqa: RET503
            return FakeTraceback(self._frames[1:], self._line_nums[1:])


class TestLogFormatters:
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
    def record_with_exception(self, tmp_path: Path):
        path = tmp_path / "my_module.py"
        path.write_text("cause_an_error()\n")

        tb = t.cast(
            TracebackType,
            FakeTraceback(
                [
                    FakeFrame(
                        FakeCode(str(path), "test"),
                        {"__name__": "__main__"},
                        {"my_var": "my_value"},
                    ),
                ],
                [1],
            ),
        )

        return logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test",
            lineno=1,
            msg="test",
            args=None,
            exc_info=(
                Exception,
                Exception("test"),
                tb,
            ),
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

    def test_json_formatter_callsite_parameters(self, record):
        formatter = formatters.json_formatter(callsite_parameters=True)
        output = formatter.format(record)
        message_dict = json.loads(output)
        assert message_dict["pathname"] == "/path/to/my_module.py"
        assert message_dict["lineno"] == 1
        assert message_dict["func_name"] == "my_func"

    def test_json_formatter_exception(self, record_with_exception) -> None:
        formatter = formatters.json_formatter()
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)

        assert "exception" in message_dict

        exception_list = message_dict["exception"]
        assert isinstance(exception_list, list)
        assert len(exception_list) == 1
        assert exception_list[0]["exc_type"] == "Exception"
        assert exception_list[0]["exc_value"] == "test"

        formatter = formatters.json_formatter(dict_tracebacks=False)
        output = formatter.format(record_with_exception)
        message_dict = json.loads(output)

        assert "exception" not in message_dict
