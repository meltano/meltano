from __future__ import annotations

import logging
import re

import pytest

from meltano.core.logging.formatters import console_log_formatter

ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")


class TestLogFormatters:
    @pytest.fixture
    def record(self):
        return logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test",
            lineno=1,
            msg="test",
            args=[],
            exc_info=None,
        )

    def test_console_log_formatter_colors(self, record):
        formatter = console_log_formatter(colors=True)
        assert ANSI_RE.match(formatter.format(record))

    def test_console_log_formatter_no_colors(self, record):
        formatter = console_log_formatter(colors=False)
        assert not ANSI_RE.match(formatter.format(record))
