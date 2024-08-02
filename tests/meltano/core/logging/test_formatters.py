from __future__ import annotations

import logging
import re
import typing as t
from types import TracebackType

import pytest

from meltano.core.logging.formatters import console_log_formatter

if t.TYPE_CHECKING:
    from pathlib import Path

ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")


class FakeCode:
    """A fake code object that can be used to test log formatters."""

    def __init__(self, co_filename, co_name) -> None:
        self.co_filename = co_filename
        self.co_name = co_name


class FakeFrame:
    """A fake traceback frame that can be used to test log formatters."""

    def __init__(self, f_code, f_globals, f_locals=None) -> None:
        self.f_code = f_code
        self.f_globals = f_globals
        self.f_locals = f_locals or {}


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
    @pytest.fixture()
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

    @pytest.fixture()
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
        formatter = console_log_formatter(colors=True)
        assert ANSI_RE.match(formatter.format(record))

    def test_console_log_formatter_no_colors(self, record) -> None:
        formatter = console_log_formatter(colors=False)
        assert not ANSI_RE.match(formatter.format(record))

    def test_console_log_formatter_no_locals(self, record_with_exception) -> None:
        formatter = console_log_formatter(show_locals=False)
        output = formatter.format(record_with_exception)
        assert "locals" not in output
        assert "my_var = 'my_value'" not in output

    def test_console_log_formatter_show_locals(self, record_with_exception) -> None:
        formatter = console_log_formatter(show_locals=True)
        output = formatter.format(record_with_exception)
        assert "locals" in output
        assert "my_var = 'my_value'" in output
