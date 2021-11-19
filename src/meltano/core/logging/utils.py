import asyncio
import logging
import os
from contextlib import suppress
from logging import config as logging_config
from typing import Dict, Optional

import structlog
import yaml
from meltano.core.logging.formatters import LEVELED_TIMESTAMPED_PRE_CHAIN, TIMESTAMPER
from meltano.core.project_settings_service import ProjectSettingsService

try:
    from typing import Protocol  # noqa:  WPS433
except ImportError:
    from typing_extensions import Protocol  # noqa:  WPS433,WPS440


LEVELS = {
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


def parse_log_level(log_level: Dict[str, int]) -> int:
    """Parse a level descriptor into an logging level."""
    return LEVELS.get(log_level, LEVELS[DEFAULT_LEVEL])


def read_config(config_file: Optional[str] = None) -> dict:
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
         dict: logging config suitable for use with logging.config.dictConfig
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
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
        },
    }


def setup_logging(project=None, log_level=DEFAULT_LEVEL):
    # Mimick Python 3.8's `force=True` kwarg to override any
    # existing logger handlers
    # See https://github.com/python/cpython/commit/cf67d6a934b51b1f97e72945b596477b271f70b8
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
        h.close()

    log_level = DEFAULT_LEVEL.upper()
    log_config = None

    if project:
        settings_service = ProjectSettingsService(project)
        log_config = settings_service.get("cli.log_config")
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


class SubprocessOutputWriter(Protocol):
    """SubprocessOutputWriter is a basic interface definition suitable for use with capture_subprocess_output."""

    def writelines(self, lines: str):
        """Any type with a writelines method accepting a string could be used as an output writer."""
        pass


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
    reader: Optional[asyncio.StreamReader], *line_writers: SubprocessOutputWriter
):
    """Capture in real time the output stream of a suprocess that is run async.

    The stream has been set to asyncio.subprocess.PIPE and is provided using
    reader to this function.

    As new lines are captured for reader, they are written to output_stream.
    This async function should be run with await asyncio.wait() while waiting
    for the subprocess to end.
    """
    while not reader.at_eof():
        line = await reader.readline()
        if not line:
            continue

        for writer in line_writers:
            if not await _write_line_writer(writer, line):
                # If the destination stream is closed, we can stop capturing output.
                return
