"""SingerMapper and supporting classes.

This module contains the SingerMapper class as well as a supporting methods.
"""
import json
from typing import Optional

import structlog
from meltano.core.behavior.hookable import hook
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.setting_definition import SettingDefinition, SettingKind

from . import PluginType, SingerPlugin

logger = structlog.stdlib.get_logger(__name__)


class SingerMapper(SingerPlugin):
    """A SingerMapper is a singer spec compliant stream mapper."""

    __plugin_type__ = PluginType.MAPPERS

    EXTRA_SETTINGS = [
        SettingDefinition(name="_mappings", kind=SettingKind.OBJECT, aliases=["mappings"], value={}),
        SettingDefinition(
            name="_mapping_name", kind=SettingKind.STRING, aliases=["mapping_name"], value=None
        ),
    ]

    def is_installable(self):
        return self.pip_url is not None

    def is_invokable(self):
        return False

    def exec_args(self, plugin_invoker: PluginInvoker):
        """Return the arguments to be passed to the plugin's executable."""
        return ["--config", plugin_invoker.files["config"]]

    @property
    def config_files(self):
        """Return the configuration files required by the plugin."""
        return {"config": f"mapper.{self.instance_uuid}.config.json"}


class SingerMapping(SingerMapper):
    """A SingerMapping is the invocable version a singer spec compliant stream mapper."""

    __plugin_type__ = PluginType.MAPPINGS

    @hook("before_configure")
    async def before_configure(self, invoker: PluginInvoker, session):
        """Create configuration file."""
        config_path = invoker.files["config"]
        with open(config_path, "w") as config_file:
            config = invoker.plugin_config_override or invoker.plugin.config
            json.dump(config, config_file, indent=2)

        logger.debug(
            "Created configuration",
            config_path=config_path,
            plugin_name=invoker.plugin.name,
        )

    def is_installable(self):
        return False

    def is_invokable(self):
        return self.pip_url is not None or self.executable is not None