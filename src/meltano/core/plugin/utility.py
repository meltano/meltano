"""A module for the UtilityPlugin type."""

from meltano.core.plugin import BasePlugin, PluginType


class UtilityPlugin(BasePlugin):
    """A plugin type for arbitrary pip executables."""

    __plugin_type__ = PluginType.UTILITIES
