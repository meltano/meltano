"""A simple TCP socket-based log receiver."""

from __future__ import annotations

import contextlib
import logging
import logging.handlers
import pickle
import socketserver
import struct
import threading
import typing as t

import structlog

if t.TYPE_CHECKING:
    import types

logger = structlog.stdlib.get_logger(__name__)


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    server: LogRecordSocketReceiver

    def handle(self) -> None:
        """Handle multiple requests.

        Each request expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk += self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data: bytes) -> dict[str, t.Any]:  # noqa: N802
        """Unpickle the data.

        Args:
            data: The data to unpickle.

        Returns:
            The unpickled data.
        """
        return pickle.loads(data)  # noqa: S301

    def handleLogRecord(self, record: logging.LogRecord) -> None:  # noqa: N802
        """Handle the log record.

        Args:
            record: The log record to handle.
        """
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        name = self.server.logger_name or record.name
        logger = logging.getLogger(name)  # noqa: TID251
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """Simple TCP socket-based logging receiver suitable for testing.

    Usage:

      version: 1
      disable_existing_loggers: false
      formatters:
      default:
        format: "%(message)s" # irrelevant since we send pickled records
      handlers:
        meltano:
          class: logging.handlers.SocketHandler
          host: localhost
          port: 9020
          formatter: default
      root:
        level: INFO
        handlers: [ meltano ]
    """

    allow_reuse_address = True

    def __init__(
        self,
        host: str = "localhost",
        port: int = logging.handlers.DEFAULT_TCP_LOGGING_PORT,
        handler: type[socketserver.BaseRequestHandler] = LogRecordStreamHandler,
    ):
        """Initialize the server.

        Args:
            host: The host to listen on.
            port: The port to listen on.
            handler: The handler to use.
        """
        super().__init__((host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logger_name: str | None = None

    def serve_until_stopped(self) -> None:
        """Serve until stopped."""
        import select

        abort = 0
        while not abort:
            rd, _wr, _ex = select.select([self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


class LoggingServer(contextlib.AbstractContextManager):
    """A context manager that starts and stops the logging server."""

    def __init__(self, logger_name: str | None = None) -> None:
        """Initialize the logging server."""
        self.tcpserver = LogRecordSocketReceiver()
        self.tcpserver.logger_name = logger_name
        self.server_thread = threading.Thread(target=self._start, daemon=True)

    def _start(self) -> None:
        """Start the logging server."""
        self.tcpserver.serve_until_stopped()

    def __enter__(self) -> None:
        """Start the logging server context manager."""
        # 2. start the server in a separate thread
        self.server_thread.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Stop the logging server."""
        self.tcpserver.abort = 1
        self.server_thread.join()


def is_logging_server_available(
    host: str = "localhost",
    port: int = logging.handlers.DEFAULT_TCP_LOGGING_PORT,
    timeout: float = 0.1,
) -> bool:
    """Check if a logging server is available at the given host and port.

    Args:
        host: The host to check.
        port: The port to check.
        timeout: Connection timeout in seconds.

    Returns:
        True if server is available, False otherwise.
    """
    import socket

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False
