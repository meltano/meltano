"""Defines PluginTestService."""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod

from meltano.core.plugin.base import PluginType
from meltano.core.plugin.error import PluginNotSupportedError
from meltano.core.plugin_invoker import PluginInvoker

logger = logging.getLogger(__name__)


class PluginTestServiceFactory:
    """Factory class to resolve a plugin test service."""

    def __init__(self, plugin_invoker: PluginInvoker):
        """Construct a PluginTestServiceFactory instance.

        Args:
            plugin_invoker: The invocation instance of the plugin to test.
        """
        self.plugin_invoker = plugin_invoker

    def get_test_service(self):
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
    async def validate(self) -> tuple[bool, str]:
        """Abstract method to validate plugin configuration."""


class ExtractorTestService(PluginTestService):
    """Handle extractor test operations."""

    async def validate(self) -> tuple[bool, str]:
        """Validate extractor configuration.

        Returns:
            The validation result and supporting context message (if applicable).
        """
        process = None

        try:
            process = await self.plugin_invoker.invoke_async(
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
            )
        except Exception as exc:
            return False, str(exc)

        last_line = None
        while not process.stdout.at_eof():
            data = await process.stdout.readline()
            line = data.decode("ascii").strip()
            if line:
                logger.debug(line)
                last_line = line

            try:
                message_type = json.loads(line)["type"]
            except (json.decoder.JSONDecodeError, KeyError):
                continue

            if message_type == "RECORD":
                process.terminate()
                break

        returncode = await process.wait()

        # considered valid if subprocess is terminated (exit status < 0) on RECORD message received
        # see https://docs.python.org/3/library/subprocess.html#subprocess.CompletedProcess.returncode
        return (
            returncode < 0,
            last_line if returncode else "No RECORD message received",
        )
