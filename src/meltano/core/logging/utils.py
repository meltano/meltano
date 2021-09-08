import asyncio
import logging
import os
import re
import sys
from contextlib import suppress
from typing import Optional

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


def parse_log_level(log_level):
    return LEVELS.get(log_level, LEVELS[DEFAULT_LEVEL])


def setup_logging(project=None, log_level=DEFAULT_LEVEL):
    # Mimick Python 3.8's `force=True` kwarg to override any
    # existing logger handlers
    # See https://github.com/python/cpython/commit/cf67d6a934b51b1f97e72945b596477b271f70b8
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
        h.close()

    if project:
        settings_service = ProjectSettingsService(project)
        log_level = settings_service.get("cli.log_level")

    logging.basicConfig(
        stream=sys.stderr, format=FORMAT, level=parse_log_level(log_level)
    )


def remove_ansi_escape_sequences(line):
    """
    Remove ANSI escape sequences that are used for adding colors in
     terminals, so that only the text is logged in a file
    """
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", line)


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
