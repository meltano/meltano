from __future__ import annotations

import logging
import logging.handlers
import threading
import typing as t

from meltano.core.logging.server import LoggingServer, MsgpackSocketHandler

if t.TYPE_CHECKING:
    import pytest


class TestLoggingServer:
    def test_server_thread_is_daemon(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that the server thread is a daemon thread."""
        client_logger = logging.getLogger("client_logger")  # noqa: TID251
        # Remove all existing handlers from the client logger
        with (
            LoggingServer(logger_name="server_logger"),
            caplog.at_level(logging.INFO, "server_logger"),
        ):
            client_handler = MsgpackSocketHandler(
                host="localhost",
                port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
            )
            client_logger.addHandler(client_handler)
            client_logger.info("test")
            client_handler.close()

        record = caplog.records[0]
        assert record.msg == "test"
        assert record.threadName == threading.current_thread().name
        assert record.name == "client_logger"
