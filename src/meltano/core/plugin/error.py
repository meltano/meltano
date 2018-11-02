from . import Plugin
from meltano.core.error import PluginInstallWarning


class PluginMissingError(Exception):
    """
    Base exception when a plugin seems to be missing.
    """

    def __init__(self, plugin_or_name):
        if isinstance(plugin_or_name, Plugin):
            self.plugin_name = plugin_or_name.name
        else:
            self.plugin_name = plugin_or_name


class TapDiscoveryError(PluginInstallWarning):
    def __str__(self):
        return (
            "Running --discover on the tap failed, "
            "no catalog will be provided."
            "Some taps requires a valid catalog file "
            "with some selected streams."
        )
