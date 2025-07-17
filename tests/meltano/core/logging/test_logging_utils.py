from __future__ import annotations

import asyncio
import datetime
import logging
import zoneinfo
from pathlib import Path

import pytest
import time_machine

from meltano.core.logging.utils import (
    LogFormat,
    capture_subprocess_output,
    default_config,
    setup_logging,
)


class AsyncReader(asyncio.StreamReader):
    def __init__(self, lines: list[bytes]):
        self.lines = lines

    def at_eof(self) -> bool:
        return not self.lines

    async def readline(self) -> bytes:
        return self.lines.pop(0) if self.lines else b""


@pytest.mark.asyncio
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
            LogFormat.plain,
            "test",
            id="plain",
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
    formatter.logger = logging.getLogger("test")  # noqa: TID251
    formatter.logger.setLevel(logging.DEBUG)

    # Mock current time and process ID
    with (
        time_machine.travel(
            datetime.datetime(2021, 1, 1, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("UTC")),
            tick=False,
        ),
        monkeypatch.context() as m,
    ):
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


def test_setup_logging_yml_extension_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that setup_logging supports both .yaml and .yml extensions via fallback."""
    from unittest.mock import patch

    import yaml

    log_config_dict = {
        "version": 1,
        "formatters": {"simple": {"format": "%(levelname)s - %(message)s"}},
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "simple"}
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }

    yaml_path = tmp_path / "logging.yaml"
    yml_path = tmp_path / "logging.yml"
    original_cwd = Path.cwd()

    # Save original logging state
    original_handlers = logging.root.handlers[:]
    original_level = logging.root.level

    logged_messages = []

    def capture_log_call(*args, **kwargs):
        logged_messages.append(str(args[0]) if args else str(kwargs))

    def test_fallback(config_file: str, expected_fallback: Path):
        """Test logging config fallback from one extension to another."""
        monkeypatch.chdir(tmp_path)

        try:
            with patch("meltano.core.logging.utils.logger.info", capture_log_call):
                setup_logging(log_config=config_file)
                root_logger = logging.getLogger()  # noqa: TID251
                assert len(root_logger.handlers) > 0
                handler = root_logger.handlers[0]
                assert hasattr(handler, "formatter")

                expected_message = (
                    f"Using logging config from {expected_fallback.name} "
                    f"(fallback from {config_file})"
                )
                assert any(expected_message in msg for msg in logged_messages), (
                    f"Expected fallback message '{expected_message}' not found in "
                    f"logs: {logged_messages}"
                )
        finally:
            monkeypatch.chdir(original_cwd)
            logged_messages.clear()
            # Clean up logging handlers
            logging.root.handlers = []

    try:
        # Test .yaml -> .yml fallback
        yml_path.write_text(yaml.dump(log_config_dict))
        test_fallback("logging.yaml", yml_path)

        # Test .yml -> .yaml fallback
        yml_path.unlink()
        yaml_path.write_text(yaml.dump(log_config_dict))
        test_fallback("logging.yml", yaml_path)

        # Test case-insensitive extension (.YAML -> .yml)
        yaml_path.unlink()
        yml_path.write_text(yaml.dump(log_config_dict))
        test_fallback("logging.YAML", yml_path)
    finally:
        # Restore original logging state
        logging.root.handlers = original_handlers
        logging.root.setLevel(original_level)
