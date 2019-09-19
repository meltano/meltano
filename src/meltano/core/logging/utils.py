import asyncio
import logging
import re
import sys


def setup_logging(log_level=logging.INFO):
    logging.basicConfig(
        stream=sys.stderr,
        format="[%(threadName)10s][%(levelname)s][%(asctime)s] %(message)s",
        level=log_level,
    )


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
