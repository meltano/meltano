"""Defines PluginTestService."""

import json
import logging
from subprocess import PIPE, STDOUT
from typing import Union

from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker

SUPPORTED_TYPES = PluginType.EXTRACTORS

logger = logging.getLogger(__name__)


class PluginTestService:
    """Handle plugin test operations."""

    def __init__(self, plugin_invoker: PluginInvoker):
        """Construct a PluginTestService instance."""
        self.plugin_invoker = plugin_invoker

    def validate(self) -> Union[bool, str]:
        """Validate plugin configuration."""
        plugin = self.plugin_invoker.plugin
        if plugin.type not in SUPPORTED_TYPES:
            return False, f"Operation not supported for {plugin.type}"

        process = None
        try:
            process = self.plugin_invoker.invoke(
                stdout=PIPE, stderr=STDOUT, universal_newlines=True
            )
        except Exception as exc:
            return False, str(exc)

        while process.poll() is None:
            line = process.stdout.readline().strip()
            if line:
                logger.debug(line)

            try:
                message = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue

            if message["type"] == "RECORD":
                process.terminate()
                return True, None

        return False, "No RECORD message received"
