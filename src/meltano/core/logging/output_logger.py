import asyncio
import logging
import os
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout, suppress
from typing import IO, Optional

import click
from async_generator import asynccontextmanager

from .utils import capture_subprocess_output, remove_ansi_escape_sequences


class OutputLogger:
    def __init__(self, file):
        self.file = file
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.outs = {}
        self._max_name_length = None
        self._max_subtask_name_length = None

    def out(
        self, name: str, subtask_name: Optional[str] = "main", stream=None, color=None
    ) -> "Out":
        """Obtain an Out instance for use as a logger or use for output capture.

        Args:
            name: name of this Out instance and to use in the name field.
            subtask_name: subtask name to use for the subtask field.
            stream: stream you wish to write too.
            color: colorize/format output to provided color.

        Returns:
            An Out instance that will log anything written in to a
            file as well as to the provided stream.
        """
        if stream in (None, sys.stderr):
            stream = self.stderr
        elif stream is sys.stdout:
            stream = self.stdout

        out = Out(
            self,
            name,
            file=self.file,
            stream=stream,
            color=color,
            subtask_name=subtask_name,
        )
        self.outs[name] = out
        self._max_name_length = None
        self._max_subtask_name_length = None

        return out

    @property
    def max_name_length(self) -> int:
        """Return the current max length of the name field."""
        if self._max_name_length is None:
            name_lengths = (len(name) for name in self.outs.keys())
            self._max_name_length = max(name_lengths, default=0)

        return self._max_name_length

    @property
    def max_subtask_name_length(self) -> int:
        """Return the current max length of the subtask field."""
        if self._max_subtask_name_length is None:
            name_lengths = (
                len(out.subtask_name) for out in self.outs.values() if out.subtask_name
            )
            self._max_subtask_name_length = max(name_lengths, default=0)

        return self._max_subtask_name_length


class LineWriter:
    NEWLINE = "\n"

    def __init__(self, out):
        self.__out = out
        self.__skip_next_newline = False

    def __getattr__(self, name):
        return getattr(self.__out, name)

    def write(self, line):
        # Pre 3.7, `logging.StreamHandler.emit` will
        # write the message and terminator separately
        if self.__skip_next_newline:
            self.__skip_next_newline = False
            if line == self.NEWLINE:
                return

        if not line.endswith(self.NEWLINE):
            line = line + self.NEWLINE
            self.__skip_next_newline = True

        self.__out.writeline(line)


class FileDescriptorWriter:
    def __init__(self, out, fd):
        self.__out = out
        self.__writer = os.fdopen(fd, "w")

    def __getattr__(self, name):
        return getattr(self.__writer, name)

    def isatty(self):
        return self.__out.isatty()


class Out:  # noqa: WPS230
    """
    Simple Out class to log anything written in a stream to a file
     and then also write it to the stream.
    """

    def __init__(
        self,
        output_logger: OutputLogger,
        name: str,
        file: IO,
        stream: IO,
        color: Optional[str] = "white",
        subtask_name: Optional[str] = "",
    ):
        """Log anything written in a stream to a file and then also write it to the stream.

        Args:
            output_logger: the OutputLogger to use.
            name: name of this Out instance and to use in the name field.
            file: file object to write to.
            stream: stream object to write to.
            color: colorize/format output to provided color.
            subtask_name: subtask name to use for the subtask field.
        """
        self.output_logger = output_logger
        self.name = name
        self.subtask_name = subtask_name
        self.color = color

        self.file = file
        self.stream = stream

        self.last_line = ""

        self._prefix = None
        self._subtask_field = ""
        self._max_name_length = None
        self._max_subtask_name_length = None

    @property
    def prefix(self):
        max_name_length = self.output_logger.max_name_length
        if self._prefix is None or self._max_name_length != max_name_length:
            self._max_name_length = max_name_length

            padding = max(max_name_length, 6)
            padded_name = self.name.ljust(padding)
            self._prefix = click.style(f"{padded_name} | ", fg=self.color)

        return self._prefix

    @property
    def subtask_field(self) -> str:
        """Return the formatted subtask_field."""
        max_subtask_name_length = self.output_logger.max_subtask_name_length
        if (  # noqa: WPS337 - conflicts with black
            self._subtask_field is None
            or self._max_subtask_name_length != max_subtask_name_length
        ):
            padding = max(max_subtask_name_length, 6)
            padded_subtask_name = self.subtask_name.ljust(padding)
            self._subtask_field = click.style(f"{padded_subtask_name} | ")

        return self._subtask_field

    @contextmanager
    def line_writer(self):
        yield LineWriter(self)

    @contextmanager
    def redirect_logging(self, format=None, ignore_errors=()):
        logger = logging.getLogger()
        original_log_handlers = logger.handlers

        line_writer = LineWriter(self)
        handler = logging.StreamHandler(line_writer)

        if not format:
            if logger.getEffectiveLevel() == logging.DEBUG:
                format = "%(levelname)s %(message)s"
            else:
                format = "%(message)s"

        formatter = logging.Formatter(fmt=format)
        handler.setFormatter(formatter)

        logger.handlers = [handler]

        try:
            yield
        except (KeyboardInterrupt, asyncio.CancelledError, *ignore_errors):
            raise
        except Exception as err:
            logger.error(str(err), exc_info=True)
            raise
        finally:
            logger.handlers = original_log_handlers

    @asynccontextmanager
    async def writer(self):
        read_fd, write_fd = os.pipe()

        reader = asyncio.ensure_future(self._read_from_fd(read_fd))
        writer = FileDescriptorWriter(self, write_fd)

        try:
            yield writer
        finally:
            writer.close()

            with suppress(asyncio.CancelledError):
                await reader

    @asynccontextmanager
    async def redirect_stdout(self):
        async with self.writer() as stdout:
            with redirect_stdout(stdout):
                yield

    @asynccontextmanager
    async def redirect_stderr(self):
        async with self.writer() as stderr:
            with redirect_stderr(stderr):
                yield

    def writeline(self, line):
        self.last_line = line

        click.echo(self.prefix + self.subtask_field + line, nl=False, file=self)
        self.flush()

    def write(self, data):
        self.stream.write(data)
        self.file.write(remove_ansi_escape_sequences(data))
        # always flush the file to keep it up to date with the stream
        self.file.flush()

    def flush(self):
        self.stream.flush()
        self.file.flush()

    def isatty(self):
        # Explicitly claim we're connected to a TTY to stop Click
        # from stripping ANSI codes
        return self.stream.isatty()

    async def _read_from_fd(self, read_fd):
        # Since we're redirecting our own stdout and stderr output,
        # the line length limit can be arbitrarily large.
        line_length_limit = 1024 * 1024 * 1024  # 1 GiB

        reader = asyncio.StreamReader(limit=line_length_limit)
        read_protocol = asyncio.StreamReaderProtocol(reader)

        loop = asyncio.get_event_loop()
        read_transport, _ = await loop.connect_read_pipe(
            lambda: read_protocol, os.fdopen(read_fd)
        )

        await capture_subprocess_output(reader, self)
