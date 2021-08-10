from typing import Dict
from uuid import uuid4

from meltano.core.behavior.hookable import hook
from meltano.core.db import project_engine
from meltano.core.setting_definition import SettingDefinition

from . import PluginType, SingerPlugin


class SingerTarget(SingerPlugin):
    __plugin_type__ = PluginType.LOADERS

    EXTRA_SETTINGS = [
        SettingDefinition(name="_dialect", value="$MELTANO_LOADER_NAMESPACE"),
        SettingDefinition(name="_target_schema", value="$MELTANO_LOAD_SCHEMA"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._target_instance_uuid: str = None

    def exec_args(self, plugin_invoker):
        args = ["--config", plugin_invoker.files["config"]]

        return args

    @property
    def config_files(self):
        return {"config": f"target.{self.target_instance_uuid}.config.json"}

    @property
    def target_uuid(self):
        if not self._target_instance_uuid:
            self._target_instance_uuid=str(uuid4())
        return self._target_instance_uuid

    @property
    def output_files(self):
        return {"state": "new_state.json"}
