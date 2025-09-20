from __future__ import annotations

import json
import logging
import logging.handlers
import tempfile
import time
from pathlib import Path
from unittest import mock

import pytest

from meltano.core.logging.server import LoggingServer, is_logging_server_available
from meltano.core.plugin.singer.base import SingerPlugin


class TestSingerLoggingServerIntegration:
    """Test integration between Singer plugins and the logging server."""

    def test_is_logging_server_available_when_running(self) -> None:
        """Test server detection when logging server is running."""
        with LoggingServer():
            assert is_logging_server_available()

    def test_is_logging_server_available_when_not_running(self) -> None:
        """Test server detection when logging server is not running."""
        assert not is_logging_server_available()

    @pytest.mark.asyncio
    async def test_singer_sdk_logging_config_without_server(self) -> None:
        """Test Singer SDK logging config generation without logging server."""
        plugin = SingerPlugin("test_tap", "tap")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "singer_sdk_logging.json"

            # Mock plugin invoker with files
            mock_invoker = mock.MagicMock()
            mock_invoker.files = {
                "singer_sdk_logging": config_file,
                "pipelinewise_singer_logging": temp_path / "pipelinewise_logging.conf",
            }

            # Mock server availability to return False
            with mock.patch(
                "meltano.core.plugin.singer.base.is_logging_server_available",
                return_value=False,
            ):
                await plugin.setup_logging_hook(mock_invoker)

            # Check generated config
            config = json.loads(config_file.read_text())

            assert config["handlers"]["console"]["class"] == "logging.StreamHandler"
            assert "meltano_server" not in config["handlers"]
            assert config["root"]["handlers"] == ["console"]

    @pytest.mark.asyncio
    async def test_singer_sdk_logging_config_with_server(self) -> None:
        """Test Singer SDK logging config generation with logging server."""
        plugin = SingerPlugin("test_tap", "tap")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "singer_sdk_logging.json"

            # Mock plugin invoker with files
            mock_invoker = mock.MagicMock()
            mock_invoker.files = {
                "singer_sdk_logging": config_file,
                "pipelinewise_singer_logging": temp_path / "pipelinewise_logging.conf",
            }

            # Mock server availability to return True
            with mock.patch(
                "meltano.core.plugin.singer.base.is_logging_server_available",
                return_value=True,
            ):
                await plugin.setup_logging_hook(mock_invoker)

            # Check generated config
            config = json.loads(config_file.read_text())

            assert config["handlers"]["console"]["class"] == "logging.StreamHandler"
            assert (
                config["handlers"]["meltano_server"]["class"]
                == "logging.handlers.SocketHandler"
            )
            assert config["handlers"]["meltano_server"]["host"] == "localhost"
            assert (
                config["handlers"]["meltano_server"]["port"]
                == logging.handlers.DEFAULT_TCP_LOGGING_PORT
            )
            assert set(config["root"]["handlers"]) == {"console", "meltano_server"}

    @pytest.mark.asyncio
    async def test_pipelinewise_logging_config_without_server(self) -> None:
        """Test Pipelinewise logging config generation without logging server."""
        plugin = SingerPlugin("test_tap", "tap")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "pipelinewise_logging.conf"

            # Mock plugin invoker with files
            mock_invoker = mock.MagicMock()
            mock_invoker.files = {
                "singer_sdk_logging": temp_path / "singer_sdk_logging.json",
                "pipelinewise_singer_logging": config_file,
            }

            # Mock server availability to return False
            with mock.patch(
                "meltano.core.plugin.singer.base.is_logging_server_available",
                return_value=False,
            ):
                await plugin.setup_logging_hook(mock_invoker)

            # Check generated config
            config_content = config_file.read_text()

            assert "keys=console" in config_content
            assert "handlers=console" in config_content
            assert "[handler_console]" in config_content
            assert "[handler_meltano_server]" not in config_content

    @pytest.mark.asyncio
    async def test_pipelinewise_logging_config_with_server(self) -> None:
        """Test Pipelinewise logging config generation with logging server."""
        plugin = SingerPlugin("test_tap", "tap")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_file = temp_path / "pipelinewise_logging.conf"

            # Mock plugin invoker with files
            mock_invoker = mock.MagicMock()
            mock_invoker.files = {
                "singer_sdk_logging": temp_path / "singer_sdk_logging.json",
                "pipelinewise_singer_logging": config_file,
            }

            # Mock server availability to return True
            with mock.patch(
                "meltano.core.plugin.singer.base.is_logging_server_available",
                return_value=True,
            ):
                await plugin.setup_logging_hook(mock_invoker)

            # Check generated config
            config_content = config_file.read_text()

            assert "keys=console,meltano_server" in config_content
            assert "handlers=console,meltano_server" in config_content
            assert "[handler_console]" in config_content
            assert "[handler_meltano_server]" in config_content
            assert "class=logging.handlers.SocketHandler" in config_content

    @pytest.mark.asyncio
    async def test_log_level_preservation_in_singer_config(self) -> None:
        """Test that log levels are correctly preserved in Singer config files."""
        plugin = SingerPlugin("test_tap", "tap")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sdk_config_file = temp_path / "singer_sdk_logging.json"
            pipelinewise_config_file = temp_path / "pipelinewise_logging.conf"

            # Mock plugin invoker with files
            mock_invoker = mock.MagicMock()
            mock_invoker.files = {
                "singer_sdk_logging": sdk_config_file,
                "pipelinewise_singer_logging": pipelinewise_config_file,
            }

            # Test with different log levels
            for test_level in [
                logging.DEBUG,
                logging.INFO,
                logging.WARNING,
                logging.ERROR,
            ]:
                level_name = logging.getLevelName(test_level)

                with mock.patch("logging.getLogger") as mock_get_logger:
                    mock_root_logger = mock.MagicMock()
                    mock_root_logger.getEffectiveLevel.return_value = test_level
                    mock_get_logger.return_value = mock_root_logger

                    with mock.patch(
                        "meltano.core.plugin.singer.base.is_logging_server_available",
                        return_value=True,
                    ):
                        await plugin.setup_logging_hook(mock_invoker)

                    # Check Singer SDK config
                    sdk_config = json.loads(sdk_config_file.read_text())
                    assert sdk_config["handlers"]["console"]["level"] == level_name
                    assert (
                        sdk_config["handlers"]["meltano_server"]["level"] == level_name
                    )

                    # Check Pipelinewise config
                    pipelinewise_content = pipelinewise_config_file.read_text()
                    assert f"level={level_name}" in pipelinewise_content

    def test_logging_server_integration_end_to_end(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test end-to-end logging from plugin to server."""
        with (
            LoggingServer(logger_name="server_logger"),
            caplog.at_level(logging.DEBUG, "server_logger"),
        ):
            # Create a client logger that uses SocketHandler
            # (simulating a Singer plugin)
            client_logger = logging.getLogger("test_singer_plugin")  # noqa: TID251
            client_handler = logging.handlers.SocketHandler(
                host="localhost",
                port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
            )
            client_logger.addHandler(client_handler)
            client_logger.setLevel(logging.DEBUG)

            # Send logs at different levels
            client_logger.debug("Debug message from Singer plugin")
            client_logger.info("Info message from Singer plugin")
            client_logger.warning("Warning message from Singer plugin")
            client_logger.error("Error message from Singer plugin")
            client_logger.critical("Critical message from Singer plugin")

            # Ensure all messages are flushed before closing
            client_handler.flush()
            client_handler.close()

            # Give the server time to process all messages
            time.sleep(0.2)

        # Verify log levels were preserved
        records = caplog.records

        # Filter out any non-test records (like faker logs)
        test_records = [r for r in records if r.name == "test_singer_plugin"]

        # We should have at least 5 records (one for each message level)
        # and at most 10 records (if all messages are duplicated via server)
        assert 5 <= len(test_records) <= 10, (
            f"Expected 5-10 records, got {len(test_records)}"
        )

        # Check that we have at least one of each log level
        level_names = [record.levelname for record in test_records]
        assert "DEBUG" in level_names, "Missing DEBUG level"
        assert "INFO" in level_names, "Missing INFO level"
        assert "WARNING" in level_names, "Missing WARNING level"
        assert "ERROR" in level_names, "Missing ERROR level"
        assert "CRITICAL" in level_names, "Missing CRITICAL level"

        # Verify logger name is preserved
        assert all(record.name == "test_singer_plugin" for record in test_records)
