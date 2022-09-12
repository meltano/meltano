"""Output Logger."""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from contextlib import (
    asynccontextmanager,
    contextmanager,
    redirect_stderr,
    redirect_stdout,
    suppress,
)

import structlog

from .formatters import LEVELED_TIMESTAMPED_PRE_CHAIN
from .utils import capture_subprocess_output


class OutputLogger:
    """Output Logger."""

    def __init__(self, file):
        """Instantiate an Output Logger.

        Args:
            file: A file to output to.
        """
        self.file = file
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.outs = {}

    def out(
        self, name: str, logger=None, write_level: int | None = logging.INFO
    ) -> Out:
        """Obtain an Out instance for use as a logger or use for output capture.

        Args:
            name: name of this Out instance and to use in the name field.
            logger: logger to temporarily add a handler too.
            write_level: log level passed to underlying logger.log calls.

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
            write_level=write_level,
            file=self.file,
        )
        self.outs[name] = out
        return out


class LineWriter:
    """Line Writer."""

    def __init__(self, out):
        """Instantiate a Line Writer.

        Args:
            out: The location to write to.
        """
        self.__out = out

    def __getattr__(self, name):
        """Get attribute.

        Args:
            name: The attribute name.

        Returns:
            The specified attributes value.
        """
        return getattr(self.__out, name)

    def write(self, line):
        """Write a line.

        Args:
            line: A line to write.
        """
        self.__out.writeline(line.rstrip())


class FileDescriptorWriter:
    """File Descriptor Writer."""

    def __init__(self, out, fd):
        """Instantiate File Descriptor Writer.

        Args:
            out: Output location.
            fd: A file descriptor.
        """
        self.__out = out
        self.__writer = os.fdopen(fd, "w")

    def __getattr__(self, name):
        """Get attribute.

        Args:
            name: The attribute name.

        Returns:
            The specified attributes value.
        """
        return getattr(self.__writer, name)

    def isatty(self):
        """Is out location a tty.

        Returns:
            True if output location is a tty.
        """
        return self.__out.isatty()


class Out:  # noqa: WPS230
    """Simple Out class to log anything written in a stream."""

    def __init__(
        self,
        output_logger: OutputLogger,
        name: str,
        logger: structlog.stdlib.BoundLogger,
        write_level: int,
        file: str,
    ):
        """Log anything written in a stream.

        Args:
            output_logger: the OutputLogger to use.
            name: name of this Out instance and to use in the name field.
            logger: logger to temporarily add a handler too.
            write_level: log level passed to logger.log calls.
            file: file to associate with the FileHandler to log to.
        """
        self.output_logger = output_logger
        self.logger = logger
        self.name = name
        self.write_level = write_level
        self.file = file

        self.last_line = ""

    @property
    def redirect_log_handler(self) -> logging.Handler:
        """Configure a logging.Handler suitable for redirecting logs too.

        Returns:
            logging.FileHandler using an uncolorized console formatter
        """
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(
                colors=False, exception_formatter=structlog.dev.plain_traceback
            ),
            foreign_pre_chain=LEVELED_TIMESTAMPED_PRE_CHAIN,
        )
        handler = logging.FileHandler(self.file)
        handler.setFormatter(formatter)
        return handler

    @contextmanager
    def line_writer(self):
        """Yield a line writer instance.

        Yields:
            A line writer instance
        """
        yield LineWriter(self)

    @contextmanager
    def redirect_logging(self, ignore_errors=()):
        """Redirect log entries to a temporarily added file handler.

        Args:
            ignore_errors: A tuple of Error classes to ignore.

        Yields:
            With the side-effect of redirecting logging.
        """  # noqa: DAR401
        logger = logging.getLogger()
        logger.addHandler(self.redirect_log_handler)
        ignored_errors = (
            KeyboardInterrupt,
            asyncio.CancelledError,
            *ignore_errors,
        )
        try:
            yield
        except ignored_errors:  # noqa: WPS329
            raise
        except Exception as err:
            logger.error(str(err), exc_info=True)
            raise
        finally:
            logger.removeHandler(self.redirect_log_handler)

    @asynccontextmanager
    async def writer(self):
        """Yield a writer.

        Yields:
            A writer.
        """
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
        """Redirect STDOUT.

        Yields:
            A writer with redirected output.
        """
        async with self.writer() as stdout:
            with redirect_stdout(stdout):
                yield

    @asynccontextmanager
    async def redirect_stderr(self):
        """Redirect STDERR.

        Yields:
            A writer with redirected output.
        """
        async with self.writer() as stderr:
            with redirect_stderr(stderr):
                yield

    def writeline(self, line: str) -> None:
        """Write a line to the underlying structured logger, cleaning up any dangling control chars.

        Args:
            line: A line to write.
        """
        self.last_line = line
        self.logger.log(self.write_level, line.rstrip(), name=self.name)

    async def _read_from_fd(self, read_fd):
        # Since we're redirecting our own stdout and stderr output,
        # the line length limit can be arbitrarily large.
        line_length_limit = 1024 * 1024 * 1024  # 1 GiB

        reader = asyncio.StreamReader(limit=line_length_limit)
        read_protocol = asyncio.StreamReaderProtocol(reader)

        loop = asyncio.get_event_loop()
        await loop.connect_read_pipe(lambda: read_protocol, os.fdopen(read_fd))

        await capture_subprocess_output(reader, self)
