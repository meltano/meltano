"""This module contains the SingerMapper class as well as a supporting methods."""

from __future__ import annotations

import json
import typing as t

import structlog

from meltano.core.behavior.hookable import hook
from meltano.core.setting_definition import SettingDefinition, SettingKind

from . import PluginType, SingerPlugin

if t.TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.orm import Session

    from meltano.core.plugin_invoker import PluginInvoker

logger = structlog.stdlib.get_logger(__name__)


class SingerMapper(SingerPlugin):
    """A SingerMapper is a singer spec compliant stream mapper."""

    __plugin_type__ = PluginType.MAPPERS

    EXTRA_SETTINGS: t.ClassVar[list[SettingDefinition]] = [
        SettingDefinition(
            name="_mappings",
            kind=SettingKind.ARRAY,
            aliases=["mappings"],
            value={},
        ),
        SettingDefinition(
            name="_mapping_name",
            kind=SettingKind.STRING,
            aliases=["mapping_name"],
            value=None,
        ),
    ]

    def exec_args(self, plugin_invoker: PluginInvoker) -> list[str | Path]:
        """Return the arguments to be passed to the plugin's executable."""
        return ["--config", plugin_invoker.files["config"]]

    @property
    def config_files(self) -> dict[str, str]:
        """Return the configuration files required by the plugin."""
        return {"config": f"mapper.{self.instance_uuid}.config.json"}

    @hook("before_configure")
    async def before_configure(
        self,
        invoker: PluginInvoker,
        session: Session,  # noqa: ARG002
    ) -> None:
        """Create configuration file."""
        config_path = invoker.files["config"]

        config_payload: dict = {}
        with config_path.open("w") as config_file:
            config_payload = {
                **invoker.plugin_config_processed,
                **self._get_mapping_config(invoker.plugin.extra_config),
            }
            json.dump(config_payload, config_file, indent=2)

        logger.debug(
            "Created configuration",
            config_path=config_path,
            plugin_name=invoker.plugin.name,
            mapping_name=invoker.plugin_config_extras["_mapping_name"],
            mapping_config=config_payload,
        )

    @staticmethod
    def _get_mapping_config(extra_config: dict) -> dict:
        return next(
            (
                mapping.get("config", {})
                for mapping in extra_config.get("_mappings", [])
                if mapping.get("name") == extra_config.get("_mapping_name")
            ),
            {},
        )
