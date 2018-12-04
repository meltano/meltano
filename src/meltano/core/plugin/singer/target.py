from typing import Dict

from . import SingerPlugin, PluginType


class SingerTarget(SingerPlugin):
    __plugin_type__ = PluginType.LOADERS

    def exec_args(self, files: Dict):
        args = ["--config", files["config"]]

        return args

    @property
    def config_files(self):
        return {"config": "target.config.json"}

    @property
    def output_files(self):
        return {"state": "new_state.json"}
