"""Defines PluginTestService."""

import json
import logging
from abc import ABC, abstractmethod
from subprocess import PIPE, STDOUT
from typing import Union

from meltano.core.plugin.base import PluginType
from meltano.core.plugin.error import PluginNotSupportedError
from meltano.core.plugin_invoker import PluginInvoker

logger = logging.getLogger(__name__)


class PluginTestServiceFactory:
    """Factory class to resolve a plugin test service."""

    def __init__(self, plugin_invoker: PluginInvoker):
        """Construct a PluginTestServiceFactory instance."""
        self.plugin_invoker = plugin_invoker

    def get_test_service(self):
        """Resolve a test service instance for a plugin type."""
        test_services = {PluginType.EXTRACTORS: ExtractorTestService}

        try:
            return test_services[self.plugin_invoker.plugin.type](self.plugin_invoker)
        except KeyError as err:
            raise PluginNotSupportedError(self.plugin_invoker.plugin) from err


class PluginTestService(ABC):
    """Abstract base class for plugin test operations."""

    def __init__(self, plugin_invoker: PluginInvoker):
        """Construct a PluginTestService instance."""
        self.plugin_invoker = plugin_invoker

    @abstractmethod
    def validate(self) -> Union[bool, str]:
        """Abstract method to validate plugin configuration."""
        pass


class ExtractorTestService(PluginTestService):
    """Handle extractor test operations."""

    def validate(self) -> Union[bool, str]:
        """Validate extractor configuration."""
        process = None
        try:
            process = self.plugin_invoker.invoke(
                stdout=PIPE, stderr=STDOUT, universal_newlines=True
            )
        except Exception as exc:
            return False, str(exc)

        last_line = None
        while process.poll() is None:
            line = process.stdout.readline().strip()
            if line:
                logger.debug(line)
                last_line = line

            try:
                message = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue

            if message["type"] == "RECORD":
                process.terminate()
                return True, None

        return False, last_line if process.returncode else "No RECORD message received"
