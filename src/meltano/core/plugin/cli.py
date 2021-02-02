"""A module for the CliPlugin type."""

from meltano.core.plugin import BasePlugin, PluginType


class CliPlugin(BasePlugin):
    """A plugin type for arbitrary pip executables."""

    __plugin_type__ = PluginType.CLIS
