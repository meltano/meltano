import asyncio
import logging
import os
import re
import sys


LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
CURRENT_LEVEL = os.getenv("MELTANO_LOG_LEVEL", "info")
FORMAT = "[%(asctime)s|%(levelname).1s|%(threadName)10s|%(name)s] %(message)s"


def current_log_level():
    return LEVELS[CURRENT_LEVEL]


def setup_logging(log_level=CURRENT_LEVEL):
    # setting that for any subprocess started by this process
    os.environ["MELTANO_LOG_LEVEL"] = log_level

    logging.basicConfig(stream=sys.stderr, format=FORMAT, level=LEVELS[log_level])


def remove_ansi_escape_sequences(line):
    """
    Remove ANSI escape sequences that are used for adding colors in
     terminals, so that only the text is logged in a file
    """
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", line)


async def capture_subprocess_output(stream_captured, output_stream):
    """
    Capture in real time the output stream of a suprocess that is run async.
    The stream has been set to asyncio.subprocess.PIPE and is provided using
     stream_captured to this function.
    As new lines are captured for stream_captured, they are written to output_stream.
    This async function should be run with await asyncio.wait() while waiting
     for the subprocess to end.
    """
    while not stream_captured.at_eof():
        line = await stream_captured.readline()
        if not line:
            continue

        output_stream.write(line.decode())
