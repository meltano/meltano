from typing import Dict

from meltano.core.behavior.hookable import hook
from meltano.core.db import project_engine
from . import SingerPlugin, PluginType


class SingerTarget(SingerPlugin):
    __plugin_type__ = PluginType.LOADERS

    def exec_args(self, plugin_invoker):
        args = ["--config", plugin_invoker.files["config"]]

        return args

    @property
    def config_files(self):
        return {"config": "target.config.json"}

    @property
    def output_files(self):
        return {"state": "new_state.json"}
