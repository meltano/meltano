"""Various utilities for configuring logging in a meltano project."""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import suppress
from logging import config as logging_config

import structlog
import yaml

from meltano.core.logging.formatters import (
    LEVELED_TIMESTAMPED_PRE_CHAIN,
    TIMESTAMPER,
    rich_exception_formatter_factory,
)
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import get_no_color_flag

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import Protocol  # noqa: WPS433


LEVELS = {  # noqa: WPS407
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
DEFAULT_LEVEL = "info"
FORMAT = "[%(asctime)s] [%(process)d|%(threadName)10s|%(name)s] [%(levelname)s] %(message)s"  # noqa: WPS323


def parse_log_level(log_level: dict[str, int]) -> int:
    """Parse a level descriptor into an logging level.

    Args:
        log_level: level descriptor.

    Returns:
        int: actual logging level.
    """
    return LEVELS.get(log_level, LEVELS[DEFAULT_LEVEL])


def read_config(config_file: str | None = None) -> dict:
    """Read a logging config yaml from disk.

    Args:
        config_file: path to the config file to read.

    Returns:
        dict: parsed yaml config
    """
    if config_file and os.path.exists(config_file):
        with open(config_file) as cf:
            return yaml.safe_load(cf.read())
    else:
        return None


def default_config(log_level: str) -> dict:
    """Generate a default logging config.

    Args:
        log_level: set log levels to provided level.

    Returns:
         A logging config suitable for use with `logging.config.dictConfig`.
    """
    no_color = get_no_color_flag()

    if no_color:
        formatter = rich_exception_formatter_factory(no_color=True)
    else:
        formatter = rich_exception_formatter_factory(color_system="truecolor")

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(
                    colors=not no_color,
                    exception_formatter=formatter,
                ),
                "foreign_pre_chain": LEVELED_TIMESTAMPED_PRE_CHAIN,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level.upper(),
                "formatter": "colored",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": log_level.upper(),
                "propagate": True,
            },
            "snowplow_tracker.emitters": {
                "handlers": ["console"],
                "level": logging.ERROR,
            },
            "urllib3": {
                "handlers": ["console"],
                "level": logging.INFO,
                "propagate": False,
            },
            "asyncio": {
                "handlers": ["console"],
                "level": logging.INFO,
                "propagate": False,
            },
        },
    }


def setup_logging(  # noqa: WPS210
    project: Project = None,
    log_level: str = DEFAULT_LEVEL,
    log_config: dict | None = None,
) -> None:
    """Configure logging for a meltano project.

    Args:
        project: the meltano project
        log_level: set log levels to provided level.
        log_config: a logging config suitable for use with `logging.config.dictConfig`.
    """
    # Mimick Python 3.8's `force=True` kwarg to override any
    # existing logger handlers
    # See https://github.com/python/cpython/commit/cf67d6a934b51b1f97e72945b596477b271f70b8
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()

    log_level = log_level.upper()

    if project:
        settings_service = ProjectSettingsService(project)
        log_config = log_config or settings_service.get("cli.log_config")
        log_level = settings_service.get("cli.log_level")

    config = read_config(log_config) or default_config(log_level)
    logging_config.dictConfig(config)
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            TIMESTAMPER,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def change_console_log_level(log_level: int = logging.DEBUG) -> None:
    """Change the log level for the current root logger, but only on the 'console' handler.

    Most useful when you want change the log level on the fly for console output, but want to respect other aspects
    of any potential logging.yaml sourced configs. Note that if a logging.yaml config without a 'console' handler
    is used, this will not override the log level.

    Args:
        log_level: set log levels to provided level.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    for handler in root_logger.handlers:
        if handler.name == "console":
            handler.setLevel(log_level)


class SubprocessOutputWriter(Protocol):
    """SubprocessOutputWriter is a basic interface definition suitable for use with capture_subprocess_output."""

    def writelines(self, lines: str):
        """Any type with a writelines method accepting a string could be used as an output writer.

        Args:
            lines: string to write
        """


async def _write_line_writer(writer, line):
    # StreamWriters like a subprocess's stdin need special consideration
    if isinstance(writer, asyncio.StreamWriter):
        try:  # noqa: WPS229
            writer.write(line)
            await writer.drain()
        except (BrokenPipeError, ConnectionResetError):
            with suppress(AttributeError):  # `wait_closed` is Python 3.7+
                await writer.wait_closed()

            return False
    else:
        writer.writeline(line.decode())

    return True


async def capture_subprocess_output(
    reader: asyncio.StreamReader | None, *line_writers: SubprocessOutputWriter
) -> None:
    """Capture in real time the output stream of a suprocess that is run async.

    The stream has been set to asyncio.subprocess.PIPE and is provided using
    reader to this function.

    As new lines are captured for reader, they are written to output_stream.
    This async function should be run with await asyncio.wait() while waiting
    for the subprocess to end.

    Args:
        reader: asyncio.StreamReader object that is the output stream of the subprocess.
        line_writers: any object thats a StreamWriter or has a writelines method accepting a string.
    """
    while not reader.at_eof():
        line = await reader.readline()
        if not line:
            continue

        for writer in line_writers:
            if not await _write_line_writer(writer, line):
                # If the destination stream is closed, we can stop capturing output.
                return
