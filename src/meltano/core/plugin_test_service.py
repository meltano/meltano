"""Defines PluginTestService."""

from __future__ import annotations

import asyncio
import json
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
        test_services = {PluginType.EXTRACTORS: ExtractorTestService}

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
    async def validate(self) -> tuple[bool, str | None]:
        """Abstract method to validate plugin configuration."""


class ExtractorTestService(PluginTestService):
    """Handle extractor test operations."""

    async def validate(self) -> tuple[bool, str | None]:
        """Validate extractor configuration.

        Returns:
            The validation result and supporting context message (if applicable).
        """
        process = None
        project_settings = self.plugin_invoker.project.settings
        plugin_settings = self.plugin_invoker.settings_service

        plugin_buffer_size = plugin_settings.get("_buffer_size") or 0
        project_buffer_size = project_settings.get("elt.buffer_size")

        try:
            process = await self.plugin_invoker.invoke_async(
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                limit=max(plugin_buffer_size, project_buffer_size),
            )
        except Exception as exc:
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

        return (
            record_message_received,
            last_line if returncode else "No RECORD or BATCH message received",
        )
