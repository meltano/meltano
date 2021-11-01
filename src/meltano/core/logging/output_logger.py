import asyncio
import logging
import os
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout, suppress
from typing import IO, Optional

import structlog
from async_generator import asynccontextmanager

from .formatters import LEVELED_TIMESTAMPED_PRE_CHAIN
from .utils import capture_subprocess_output


class OutputLogger:
    def __init__(self, file):
        self.file = file
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.outs = {}

    def out(
        self, name: str, subtask_name: Optional[str] = "main", logger=None
    ) -> "Out":
        """Obtain an Out instance for use as a logger or use for output capture.

        Args:
            name: name of this Out instance and to use in the name field.
            subtask_name: subtask name to use for the subtask field.
            logger: logger to temporarily add a handler too.

        Returns:
            An Out instance that will log anything written in to a
            file by injecting a log handler, as well as to the provided logger.
        """
        if not logger:
            logger = structlog.stdlib.get_logger()

        out = Out(
            self,
            name,
            logger=logger,
            file=self.file,
            subtask_name=subtask_name,
        )
        self.outs[name] = out
        return out


class LineWriter:
    def __init__(self, out):
        self.__out = out

    def __getattr__(self, name):
        return getattr(self.__out, name)

    def write(self, line):
        self.__out.writeline(line.rstrip())


class FileDescriptorWriter:
    def __init__(self, out, fd):
        self.__out = out
        self.__writer = os.fdopen(fd, "w")

    def __getattr__(self, name):
        return getattr(self.__writer, name)

    def isatty(self):
        return self.__out.isatty()


class Out:  # noqa: WPS230
    """Simple Out class to log anything written in a stream."""

    def __init__(
        self,
        output_logger: OutputLogger,
        name: str,
        logger: structlog.stdlib.BoundLogger,
        file: IO,
        subtask_name: Optional[str] = "",
    ):
        """Log anything written in a stream.

        Args:
            output_logger: the OutputLogger to use.
            name: name of this Out instance and to use in the name field.
            logger: logger to temporarily add a handler too.
            file: file object to write to.
            subtask_name: subtask name to use for the subtask field.
        """
        self.output_logger = output_logger
        self.name = name
        self.logger = logger

        self.subtask_name = subtask_name

        self.file = file

    @contextmanager
    def line_writer(self):
        yield LineWriter(self)

    @contextmanager
    def redirect_logging(self, ignore_errors=()):
        """Redirect log entries to a temporarily added file handler."""
        logger = logging.getLogger()
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=False),
            foreign_pre_chain=LEVELED_TIMESTAMPED_PRE_CHAIN,
        )
        handler = logging.FileHandler(self.file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        try:
            yield
        except (KeyboardInterrupt, asyncio.CancelledError, *ignore_errors):
            raise
        except Exception as err:
            logger.error(str(err), exc_info=True)
            raise
        finally:
            logger.removeHandler(handler)

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

    def writeline(self, line: str) -> None:
        """Write a line to the underlying structured logger, cleaning up any dangling control chars."""
        self.logger.info(line.rstrip(), name=self.name, subtask=self.subtask_name)

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
