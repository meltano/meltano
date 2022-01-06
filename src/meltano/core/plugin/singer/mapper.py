"""SingerMapper and supporting classes.

This module contains the SingerMapper class as well as a supporting methods.
"""
from meltano.core.plugin_invoker import PluginInvoker

from . import PluginType, SingerPlugin


class SingerMapper(SingerPlugin):
    """A SingerMapper is a singer spec compliant stream mapper."""

    __plugin_type__ = PluginType.MAPPERS

    def exec_args(self, plugin_invoker: PluginInvoker):
        """Return the arguments to be passed to the plugin's executable."""
        return ["--config", plugin_invoker.files["config"]]

    @property
    def config_files(self):
        """Return the configuration files required by the plugin."""
        return {"config": f"mapper.{self.instance_uuid}.config.json"}
