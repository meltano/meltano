"""Tracking plugin context for the Snowplow tracker."""
from __future__ import annotations

import uuid

from snowplow_tracker import SelfDescribingJson
from structlog.stdlib import get_logger

from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.utils import hash_sha256

logger = get_logger(__name__)

PLUGINS_CONTEXT_SCHEMA = "iglu:com.meltano/plugins_context/jsonschema"
PLUGINS_CONTEXT_SCHEMA_VERSION = "1-0-0"


def _from_plugin(plugin: ProjectPlugin, cmd: str) -> dict:
    return {
        "category": str(plugin.type),
        "name_hash": hash_sha256(plugin["info"].get("name")),
        # TODO: what if its "original" should be we hashing namespace and sending that as well?
        "variant_name_hash": hash_sha256(plugin["info"].get("variant")),
        "pip_url_hash": hash_sha256(plugin.formatted_pip_url),
        # TODO: this is not the right field, but parent "name" isn't available in the plugin context
        "parent_name_hash": hash_sha256(plugin.parent.executable),
        "command": cmd,
    }


# Proactively named to avoid name collisions more widely used "PluginContext"
class PluginsTrackingContext(SelfDescribingJson):
    """Tracking context for the Meltano plugins."""

    def __init__(self, plugins: list(tuple[ProjectPlugin, str])):
        """Initialize a meltano tracking plugin context.

        Args:
            plugins: The Meltano plugins and the requested command.
        """
        tracking_context = []
        for plugin, cmd in plugins:
            tracking_context.append(_from_plugin(plugin, cmd))

        super().__init__(
            f"{PLUGINS_CONTEXT_SCHEMA}/{PLUGINS_CONTEXT_SCHEMA_VERSION}",
            {"context_uuid": str(uuid.uuid4()), "plugins": tracking_context},
        )

    def append_plugin_context(self, plugin: ProjectPlugin, cmd: str):
        """Append a plugin context to the tracking context.

        Args:
            plugin: The Meltano plugin.
            cmd: The command that was executed.
        """
        self["plugins"].append({_from_plugin(plugin, cmd)})
