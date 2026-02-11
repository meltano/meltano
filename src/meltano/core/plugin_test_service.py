"""Defines PluginTestService."""

from __future__ import annotations

import asyncio
import asyncio.subprocess
import json
import json.decoder
import typing as t
from abc import ABC, abstractmethod

import structlog

from meltano.core.plugin.base import PluginType
from meltano.core.plugin.error import PluginNotSupportedError

if t.TYPE_CHECKING:
    from meltano.core.plugin_invoker import PluginInvoker

logger = structlog.stdlib.get_logger(__name__)


class PluginTestServiceFactory:
    """Factory class to resolve a plugin test service."""

    def __init__(self, plugin_invoker: PluginInvoker):
        """Construct a PluginTestServiceFactory instance.

        Args:
            plugin_invoker: The invocation instance of the plugin to test.
        """
        self.plugin_invoker = plugin_invoker

    def get_test_service(self):  # noqa: ANN201
        """Resolve a test service instance for a plugin type.

        Returns:
            The test service instance.

        Raises:
            PluginNotSupportedError: If the plugin type is not supported for testing.
        """
        test_services = {
            PluginType.EXTRACTORS: ExtractorTestService,
            PluginType.LOADERS: LoaderTestService,
        }

        try:
            return test_services[self.plugin_invoker.plugin.type](self.plugin_invoker)
        except KeyError as err:
            raise PluginNotSupportedError(self.plugin_invoker.plugin) from err


class PluginTestService(ABC):
    """Abstract base class for plugin test operations."""

    def __init__(self, plugin_invoker: PluginInvoker):
        """Construct a PluginTestService instance.

        Args:
            plugin_invoker: The invocation instance of the plugin to test
        """
        self.plugin_invoker = plugin_invoker

    @abstractmethod
    async def validate(self, **kwargs: t.Any) -> tuple[bool, str | None]:
        """Abstract method to validate plugin configuration."""


class ExtractorTestService(PluginTestService):
    """Handle extractor test operations."""

    async def validate(self, **kwargs: t.Any) -> tuple[bool, str | None]:
        """Validate extractor configuration.

        Returns:
            The validation result and supporting context message (if applicable).
        """
        process = None

        try:
            process = await self.plugin_invoker.invoke_async(
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                **kwargs,
            )
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

        record_message_received: bool = False
        last_line: str | None = None

        while process.stdout and not process.stdout.at_eof():
            data = await process.stdout.readline()
            line = data.decode("utf-8").strip()
            if line:
                logger.debug(line)
                last_line = line

            try:
                message_type = json.loads(line)["type"]
            except (json.decoder.JSONDecodeError, KeyError):
                continue

            record_message_received = message_type in {"RECORD", "BATCH"}
            if record_message_received:
                process.terminate()
                break

        returncode = await process.wait()
        logger.debug("Process return code: %s", returncode)

        user_message = (
            "No RECORD or BATCH message received. "
            "Verify that at least one stream is selected using "
            f"'meltano select {self.plugin_invoker.plugin.name} --list'."
        )

        return (record_message_received, last_line if returncode else user_message)


class LoaderTestService(PluginTestService):
    """Handle loader test operations."""

    async def validate(self, **kwargs: t.Any) -> tuple[bool, str | None]:
        """Validate loader configuration by sending test Singer messages.

        Returns:
            The validation result and supporting context message (if applicable).
        """
        # Warn users about potential side effects
        logger.warning(
            "Testing a loader will write test data to your target system. "
            "This test will create a table/collection called 'meltano_test_stream'. "
            "You may need to manually clean up this test data after the test "
            "completes.",
        )

        try:
            process = await self.plugin_invoker.invoke_async(
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                **kwargs,
            )
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

        # Generate test Singer messages
        test_stream_name = "meltano_test_stream"
        test_messages = self._generate_test_messages(test_stream_name)

        assert process.stdin is not None  # noqa: S101

        try:
            # Send test messages to the loader
            for message in test_messages:
                process.stdin.write((message + "\n").encode("utf-8"))
                await process.stdin.drain()

            # Close stdin to signal end of input
            process.stdin.close()
            await process.stdin.wait_closed()

            # Read output
            last_line: str | None = None
            error_occurred = False

            while process.stdout and not process.stdout.at_eof():
                data = await process.stdout.readline()
                if line := data.decode("utf-8").strip():
                    logger.debug(line)
                    last_line = line
                    # Check for error indicators
                    if "error" in line.lower() or "exception" in line.lower():
                        error_occurred = True

            returncode = await process.wait()
            logger.debug("Process return code: %s", returncode)

            if returncode == 0 and not error_occurred:
                logger.info(
                    "Test data was written to your target system. "
                    "You may want to clean up the 'meltano_test_stream' "
                    "table/collection.",
                )
                return (
                    True,
                    "Successfully processed test data for loader "
                    f"'{self.plugin_invoker.plugin.name}'.",
                )
            return (  # noqa: TRY300
                False,
                last_line or "Loader failed to process test data.",
            )

        except Exception as exc:  # noqa: BLE001
            return False, str(exc)
        finally:
            process.terminate()
            await process.wait()

    def _generate_test_messages(self, stream_name: str) -> list[str]:
        """Generate test Singer messages for loader validation.

        Args:
            stream_name: Name of the test stream.

        Returns:
            List of Singer message strings (SCHEMA, RECORD, STATE, optionally
                ACTIVATE_VERSION).
        """
        messages = []

        # SCHEMA message
        schema_message = {
            "type": "SCHEMA",
            "stream": stream_name,
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
            "key_properties": ["id"],
        }
        messages.append(json.dumps(schema_message))

        # RECORD message
        record_message = {
            "type": "RECORD",
            "stream": stream_name,
            "record": {
                "id": 1,
                "name": "Meltano Test Record",
                "created_at": "2025-09-29T00:00:00Z",
            },
        }
        messages.append(json.dumps(record_message))

        # STATE message
        state_message = {
            "type": "STATE",
            "value": {
                "bookmarks": {
                    stream_name: {
                        "last_record": 1,
                    },
                },
            },
        }
        messages.append(json.dumps(state_message))

        # ACTIVATE_VERSION message (if loader has activate-version capability)
        if "activate-version" in self.plugin_invoker.capabilities:
            activate_version_message = {
                "type": "ACTIVATE_VERSION",
                "stream": stream_name,
                "version": 1,
            }
            messages.append(json.dumps(activate_version_message))

        return messages
