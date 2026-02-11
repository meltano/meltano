"""Output Logger."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import typing as t
from contextlib import (
    asynccontextmanager,
    contextmanager,
    redirect_stderr,
    redirect_stdout,
    suppress,
)

import structlog

from meltano.core.runner import RunnerError

from .formatters import get_default_foreign_pre_chain
from .parsers import get_parser_factory
from .renderers import MeltanoConsoleRenderer
from .utils import capture_subprocess_output

StrPath: t.TypeAlias = str | os.PathLike[str]


class OutputLogger:
    """Output Logger."""

    def __init__(self, file: StrPath) -> None:
        """Instantiate an Output Logger.

        Args:
            file: A file to output to.
        """
        self.file = file
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.outs: dict[str, Out] = {}

    def out(
        self,
        name: str,
        logger=None,  # noqa: ANN001
        write_level: int = logging.INFO,
        log_parser: str | None = None,
    ) -> Out:
        """Obtain an Out instance for use as a logger or use for output capture.

        Args:
            name: name of this Out instance and to use in the name field.
            logger: logger to temporarily add a handler too.
            write_level: log level passed to underlying logger.log calls.
            log_parser: name of the log parser to use for structured parsing.

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
            log_parser=log_parser,
        )
        self.outs[name] = out
        return out


class LineWriter:
    """Line Writer."""

    def __init__(self, out: Out) -> None:
        """Instantiate a Line Writer.

        Args:
            out: The location to write to.
        """
        self.__out = out

    def __getattr__(self, name):  # noqa: ANN001, ANN204
        """Get attribute.

        Args:
            name: The attribute name.

        Returns:
            The specified attributes value.
        """
        return getattr(self.__out, name)

    def write(self, line) -> None:  # noqa: ANN001
        """Write a line.

        Args:
            line: A line to write.
        """
        self.__out.writeline(line.rstrip())

    def set_log_parser(self, *, log_parser: str | None) -> None:
        """Set the log parser.

        Args:
            log_parser: The log parser to use.
        """
        self.__out.log_parser = log_parser


class FileDescriptorWriter:
    """File Descriptor Writer."""

    def __init__(self, out, fd) -> None:  # noqa: ANN001
        """Instantiate File Descriptor Writer.

        Args:
            out: Output location.
            fd: A file descriptor.
        """
        self.__out = out
        self.__writer = os.fdopen(fd, "w")

    def __getattr__(self, name):  # noqa: ANN001, ANN204
        """Get attribute.

        Args:
            name: The attribute name.

        Returns:
            The specified attributes value.
        """
        return getattr(self.__writer, name)

    def isatty(self):  # noqa: ANN201
        """Is out location a tty.

        Returns:
            True if output location is a tty.
        """
        return self.__out.isatty()


class Out:
    """Simple Out class to log anything written in a stream."""

    def __init__(
        self,
        output_logger: OutputLogger,
        name: str,
        logger: structlog.stdlib.BoundLogger,
        write_level: int,
        file: StrPath,
        log_parser: str | None = None,
    ):
        """Log anything written in a stream.

        Args:
            output_logger: the OutputLogger to use.
            name: name of this Out instance and to use in the name field.
            logger: logger to temporarily add a handler too.
            write_level: log level passed to logger.log calls.
            file: file to associate with the FileHandler to log to.
            log_parser: name of the log parser to use for structured parsing.
        """
        self.output_logger = output_logger
        self.logger = logger
        self.name = name
        self.write_level = write_level
        self.file = file
        self.log_parser = log_parser

        self.last_line = ""
        self._parser_factory = get_parser_factory()

    @property
    def redirect_log_handler(self) -> logging.Handler:
        """Configure a logging.Handler suitable for redirecting logs too.

        Returns:
            logging.FileHandler using an uncolorized console formatter
        """
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=MeltanoConsoleRenderer(
                colors=False,
                exception_formatter=structlog.dev.plain_traceback,
            ),
            foreign_pre_chain=get_default_foreign_pre_chain(),
        )
        handler = logging.FileHandler(self.file, delay=True)
        handler.setFormatter(formatter)
        return handler

    @contextmanager
    def line_writer(self):  # noqa: ANN201
        """Yield a line writer instance.

        Yields:
            A line writer instance
        """
        yield LineWriter(self)

    @contextmanager
    def redirect_logging(self, ignore_errors=()):  # noqa: ANN001, ANN201
        """Redirect log entries to a temporarily added file handler.

        Args:
            ignore_errors: A tuple of Error classes to ignore.

        Yields:
            With the side-effect of redirecting logging.
        """
        logger = logging.getLogger()  # noqa: TID251
        logger.addHandler(self.redirect_log_handler)
        ignored_errors = (
            KeyboardInterrupt,
            asyncio.CancelledError,
            *ignore_errors,
        )
        try:
            yield
        except ignored_errors:
            raise
        except RunnerError as err:
            logger.error(str(err))  # noqa: TRY400
            raise
        except Exception as err:
            logger.error(str(err), exc_info=True)  # noqa: G201
            raise
        finally:
            logger.removeHandler(self.redirect_log_handler)

    @asynccontextmanager
    async def writer(self):  # noqa: ANN201
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
    async def redirect_stdout(self):  # noqa: ANN201
        """Redirect STDOUT.

        Yields:
            A writer with redirected output.
        """
        async with self.writer() as stdout:
            with redirect_stdout(stdout):
                yield

    @asynccontextmanager
    async def redirect_stderr(self):  # noqa: ANN201
        """Redirect STDERR.

        Yields:
            A writer with redirected output.
        """
        async with self.writer() as stderr:
            with redirect_stderr(stderr):
                yield

    def writeline(self, line: str) -> None:
        """Write a line to the underlying structured logger.

        Attempts to parse structured logs if a parser is configured,
        otherwise falls back to simple line logging.

        Args:
            line: A line to write.
        """
        self.last_line = line
        line = line.rstrip()

        if not line:
            return

        # Try to parse the line if we have a parser configured
        if self.log_parser and (
            parsed_record := self._parser_factory.parse_line(
                line,
                self.log_parser,
            )
        ):
            # Use the parsed record's level and extra fields
            extra = {"name": self.name, **parsed_record.extra}

            # If we have a logger name from the parsed record, include it
            if parsed_record.logger_name:
                extra["plugin_logger"] = parsed_record.logger_name

            # Log with the parsed level and structured data
            self.logger.log(
                parsed_record.level,
                parsed_record.message,
                plugin_exception=parsed_record.exception,
                **extra,
            )
            return

        # Fallback to original behavior for unparseable lines
        self.logger.log(self.write_level, line, name=self.name)

    async def _read_from_fd(self, read_fd) -> None:  # noqa: ANN001
        # Since we're redirecting our own stdout and stderr output,
        # the line length limit can be arbitrarily large.
        line_length_limit = 1024 * 1024 * 1024  # 1 GiB

        reader = asyncio.StreamReader(limit=line_length_limit)
        read_protocol = asyncio.StreamReaderProtocol(reader)

        loop = asyncio.get_event_loop()
        await loop.connect_read_pipe(lambda: read_protocol, os.fdopen(read_fd))

        await capture_subprocess_output(reader, self)
