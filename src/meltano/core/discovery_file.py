"""Legacy discovery file object."""

from __future__ import annotations

from meltano.core.behavior.canonical import Canonical
from meltano.core.plugin import PluginDefinition, PluginType


class DiscoveryFile(Canonical):
    """A discovery file object."""

    def __init__(self, version=1, **plugins):
        """Create a new DiscoveryFile.

        Args:
            version: The version of the discovery file.
            plugins: The plugins to add to the discovery file.
        """
        super().__init__(version=int(version))

        for ptype in PluginType:
            self[ptype] = []

        for plugin_type, raw_plugins in plugins.items():
            for raw_plugin in raw_plugins:
                plugin_def = PluginDefinition(
                    plugin_type,
                    raw_plugin.pop("name"),
                    raw_plugin.pop("namespace"),
                    **raw_plugin,
                )
                self[plugin_type].append(plugin_def)

    @classmethod
    def file_version(cls, attrs):
        """Return version of discovery file represented by attrs dictionary.

        Args:
            attrs: The attributes of the discovery file.

        Returns:
            The version of the discovery file.
        """
        return int(attrs.get("version", 1))
