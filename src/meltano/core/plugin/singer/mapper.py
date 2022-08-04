"""This module contains the SingerMapper class as well as a supporting methods."""

from __future__ import annotations

import json

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
        SettingDefinition(
            name="_mappings", kind=SettingKind.ARRAY, aliases=["mappings"], value={}
        ),
        SettingDefinition(
            name="_mapping_name",
            kind=SettingKind.STRING,
            aliases=["mapping_name"],
            value=None,
        ),
    ]

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

        config_payload: dict = {}
        with open(config_path, "w") as config_file:
            config_payload = self._get_mapping_config(invoker.plugin.extra_config)
            json.dump(config_payload, config_file, indent=2)

        logger.debug(
            "Created configuration",
            config_path=config_path,
            plugin_name=invoker.plugin.name,
            mapping_name=invoker.plugin_config_extras["_mapping_name"],
            mapping_config=config_payload,
        )

    @staticmethod
    def _get_mapping_config(extra_config: dict) -> dict | None:
        for mapping in extra_config.get("_mappings", []):
            if mapping.get("name") == extra_config.get("_mapping_name"):
                return mapping["config"]
