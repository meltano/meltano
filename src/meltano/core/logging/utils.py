"""Various utilities for configuring logging in a meltano project."""

from __future__ import annotations

import asyncio
import logging
import os
import typing as t
from logging import config as logging_config

import structlog
import yaml

from meltano.core.logging.formatters import (
    LEVELED_TIMESTAMPED_PRE_CHAIN,
    TIMESTAMPER,
    rich_exception_formatter_factory,
)
from meltano.core.utils import get_no_color_flag

if t.TYPE_CHECKING:
    from meltano.core.project import Project

LEVELS: dict[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
DEFAULT_LEVEL = "info"
FORMAT = (
    "[%(asctime)s] [%(process)d|%(threadName)10s|%(name)s] [%(levelname)s] %(message)s"
)


def parse_log_level(log_level: str) -> int:
    """Parse a level descriptor into an logging level.

    Args:
        log_level: level descriptor.

    Returns:
        int: actual logging level.
    """
    return LEVELS.get(log_level, LEVELS[DEFAULT_LEVEL])


def read_config(config_file: os.PathLike | None = None) -> dict | None:
    """Read a logging config yaml from disk.

    Args:
        config_file: path to the config file to read.

    Returns:
        dict: parsed yaml config
    """
    if config_file and os.path.exists(config_file):  # noqa: PTH110
        with open(config_file) as cf:  # noqa: PTH123
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
                "level": logging.ERROR,
            },
            "urllib3": {
                "level": logging.INFO,
            },
            "asyncio": {
                "level": logging.INFO,
            },
            # Azure HTTP logs at info level are too noisy; see
            # https://github.com/meltano/meltano/issues/7723
            "azure.core.pipeline.policies.http_logging_policy": {
                "level": logging.WARNING,
            },
        },
    }


def setup_logging(
    project: Project | None = None,
    log_level: str = DEFAULT_LEVEL,
    log_config: os.PathLike | None = None,
) -> None:
    """Configure logging for a meltano project.

    Args:
        project: the meltano project
        log_level: set log levels to provided level.
        log_config: a logging config suitable for use with `logging.config.dictConfig`.
    """
    logging.basicConfig(force=True)
    log_level = log_level.upper()

    if project:
        log_config = log_config or project.settings.get("cli.log_config")
        log_level = project.settings.get("cli.log_level")

    config = read_config(log_config) or default_config(log_level)
    logging_config.dictConfig(config)
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            TIMESTAMPER,
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def change_console_log_level(log_level: int = logging.DEBUG) -> None:
    """Change the log level for the root logger, but only on the 'console' handler.

    Most useful when you want change the log level on the fly for console
    output, but want to respect other aspects of any potential `logging.yaml`
    sourced configs. Note that if a `logging.yaml` config without a 'console'
    handler is used, this will not override the log level.

    Args:
        log_level: set log levels to provided level.
    """
    root_logger = logging.getLogger()  # noqa: TID251
    root_logger.setLevel(log_level)
    for handler in root_logger.handlers:
        if handler.name == "console":
            handler.setLevel(log_level)


class SubprocessOutputWriter(t.Protocol):
    """A basic interface suitable for use with `capture_subprocess_output`."""

    def writeline(self, line: str) -> None:
        """Write the provided line to an output.

        Args:
            line: String to write
        """


async def _write_line_writer(writer: SubprocessOutputWriter, line: bytes) -> bool:
    # StreamWriters like a subprocess's stdin need special consideration
    if isinstance(writer, asyncio.StreamWriter):
        try:
            writer.write(line)
            await writer.drain()
        except (BrokenPipeError, ConnectionResetError):
            await writer.wait_closed()
            return False
    else:
        writer.writeline(line.decode(errors="replace"))

    return True


async def capture_subprocess_output(
    reader: asyncio.StreamReader | None,
    *line_writers: SubprocessOutputWriter,
) -> None:
    """Capture in real time the output stream of a subprocess that is run async.

    The stream has been set to asyncio.subprocess.PIPE and is provided using
    reader to this function.

    As new lines are captured for reader, they are written to output_stream.
    This async function should be run with await asyncio.wait() while waiting
    for the subprocess to end.

    Args:
        reader: `asyncio.StreamReader` object that is the output stream of the
            subprocess.
        line_writers: A `StreamWriter`, or object has a compatible writelines method.
    """
    while reader and not reader.at_eof():
        line = await reader.readline()
        if not line:
            continue

        for writer in line_writers:
            if not await _write_line_writer(writer, line):
                # If the destination stream is closed, we can stop capturing output.
                return
