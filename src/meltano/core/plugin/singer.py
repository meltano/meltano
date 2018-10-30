from typing import Dict

from . import Plugin, PluginType
from meltano.core.utils import file_has_data


def plugin_factory(plugin_type: PluginType, canonical: Dict):
    plugin_class = {
        PluginType.EXTRACTORS: SingerTap,
        PluginType.LOADERS: SingerTarget,
    }

    # this will parse the discovery file and create an instance of the
    # corresponding `plugin_class` for all the plugins.
    return plugin_class[plugin_type](**canonical)


class SingerTap(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(PluginType.EXTRACTORS, *args, **kwargs)

    def exec_args(self, files: Dict):
        """
        Return the arguments list with the complete runtime paths.
        """
        args = ["--config", files["config"]]

        if file_has_data(files["catalog"]):
            args += ["--catalog", files["catalog"]]

        if file_has_data(files["state"]):
            args += ["--state", files["state"]]

        return args

    @property
    def config_files(self):
        return {
            "config": "tap.config.json",
            "catalog": "tap.properties.json",
            "state": "state.json",
        }

    @property
    def output_files(self):
        return {"output": "tap.out"}


class SingerTarget(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(PluginType.LOADERS, *args, **kwargs)

    def exec_args(self, files: Dict):
        args = ["--config", files["config"]]

        return args

    @property
    def config_files(self):
        return {"config": "target.config.json"}

    @property
    def output_files(self):
        return {"state": "new_state.json"}
