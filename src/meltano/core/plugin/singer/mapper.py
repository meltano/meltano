"""SingerMapper and supporting classes.

This module contains the SingerMapper class as well as a supporting methods.
"""
import json

import structlog
from meltano.core.behavior.hookable import hook
from meltano.core.plugin_invoker import PluginInvoker

from ...setting_definition import SettingDefinition
from . import PluginType, SingerPlugin

logger = structlog.stdlib.get_logger(__name__)


class SingerMapper(SingerPlugin):
    """A SingerMapper is a singer spec compliant stream mapper."""

    __plugin_type__ = PluginType.MAPPERS

    EXTRA_SETTINGS = [SettingDefinition(name="_mappings")]

    def exec_args(self, plugin_invoker: PluginInvoker):
        """Return the arguments to be passed to the plugin's executable."""
        return ["--config", plugin_invoker.files["config"]]

    @property
    def config_files(self):
        """Return the configuration files required by the plugin."""
        return {"config": f"mapper.{self.instance_uuid}.config.json"}

    @hook("before_configure")
    async def before_configure(self, invoker: PluginInvoker, session):
        """Create configuration file."""
        config_path = invoker.files["config"]
        with open(config_path, "w") as config_file:
            config = invoker.plugin_config_override
            json.dump(config, config_file, indent=2)

        logger.debug(
            "Created configuration",
            config_path=config_path,
            plugin_name=invoker.plugin.name,
        )
