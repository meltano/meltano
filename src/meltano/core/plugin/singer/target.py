from typing import Dict

from meltano.core.behavior.hookable import hook
from meltano.core.db import project_engine
from meltano.core.setting_definition import SettingDefinition
from . import SingerPlugin, PluginType


class SingerTarget(SingerPlugin):
    __plugin_type__ = PluginType.LOADERS

    @property
    def extra_settings(self):
        return [
            SettingDefinition(name="_dialect", value="$MELTANO_LOADER_NAMESPACE"),
            SettingDefinition(name="_target_schema", value="$MELTANO_LOAD_SCHEMA"),
        ]

    def exec_args(self, plugin_invoker):
        args = ["--config", plugin_invoker.files["config"]]

        return args

    @property
    def config_files(self):
        return {"config": "target.config.json"}

    @property
    def output_files(self):
        return {"state": "new_state.json"}
