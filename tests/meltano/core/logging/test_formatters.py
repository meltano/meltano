from __future__ import annotations

import logging
import re
from pathlib import Path
from types import TracebackType
from typing import cast

import pytest

from meltano.core.logging.formatters import console_log_formatter

ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")


class FakeCode:
    """A fake code object that can be used to test log formatters."""

    def __init__(self, co_filename, co_name):
        self.co_filename = co_filename
        self.co_name = co_name


class FakeFrame:
    """A fake traceback frame that can be used to test log formatters."""

    def __init__(self, f_code, f_globals, f_locals=None):
        self.f_code = f_code
        self.f_globals = f_globals
        self.f_locals = f_locals or {}


class FakeTraceback:
    """A fake traceback that can be used to test log formatters."""

    def __init__(self, frames, line_nums):
        if len(frames) != len(line_nums):
            raise ValueError("Ya messed up!")
        self._frames = frames
        self._line_nums = line_nums
        self.tb_frame = frames[0]
        self.tb_lineno = line_nums[0]

    @property
    def tb_next(self):
        if len(self._frames) > 1:
            return FakeTraceback(self._frames[1:], self._line_nums[1:])


class FakeException(Exception):
    def __init__(self, *args, **kwargs):
        self._tb = None
        super().__init__(*args, **kwargs)

    @property
    def __traceback__(self):
        return self._tb

    @__traceback__.setter
    def __traceback__(self, value):
        self._tb = value

    def with_traceback(self, value):
        self._tb = value
        return self


class TestLogFormatters:
    @pytest.fixture
    def record(self):
        return logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test",
            lineno=1,
            msg="test",
            args=None,
            exc_info=None,
        )

    @pytest.fixture
    def record_with_exception(self, tmp_path: Path):
        path = tmp_path / "my_module.py"
        path.write_text("cause_an_error()\n")

        tb = cast(
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

    def test_console_log_formatter_colors(self, record):
        formatter = console_log_formatter(colors=True)
        assert ANSI_RE.match(formatter.format(record))

    def test_console_log_formatter_no_colors(self, record):
        formatter = console_log_formatter(colors=False)
        assert not ANSI_RE.match(formatter.format(record))

    def test_console_log_formatter_no_locals(self, record_with_exception):
        formatter = console_log_formatter(show_locals=False)
        output = formatter.format(record_with_exception)
        assert "locals" not in output
        assert "my_var = 'my_value'" not in output

    def test_console_log_formatter_show_locals(self, record_with_exception):
        formatter = console_log_formatter(show_locals=True)
        output = formatter.format(record_with_exception)
        assert "locals" in output
        assert "my_var = 'my_value'" in output
