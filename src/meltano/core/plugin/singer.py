import logging
import os
import json
from typing import Dict

from . import Plugin, PluginType
from .error import TapDiscoveryError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.utils import file_has_data
from meltano.core.behavior.hookable import Hookable


def plugin_factory(plugin_type: PluginType, canonical: Dict):
    plugin_class = {
        PluginType.EXTRACTORS: SingerTap,
        PluginType.LOADERS: SingerTarget
    }

    # this will parse the discovery file and create an instance of the
    # corresponding `plugin_class` for all the plugins.
    return plugin_class[plugin_type](**canonical)


class SingerTap(Plugin, Hookable):
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

    @Hookable.hook("after_install")
    def install_config_stub(self, project):
        plugin_dir = project.plugin_dir(self)
        os.makedirs(plugin_dir, exist_ok=True)

        # TODO: refactor as explicit stubs
        with open(plugin_dir.joinpath(self.config_files["config"]), "w") as config:
            json.dump(self.config, config)

    @Hookable.hook("after_install")
    def run_discovery(self, project):
        invoker = PluginInvoker(project, self)

        with project.plugin_dir(self, self.config_files["catalog"]).open(
            "w"
        ) as catalog:
            result = invoker.invoke("--discover", stdout=catalog)
            exit_code = result.wait()

        if exit_code != 0:
            logging.error(
                f"Command {invoker.exec_path()} {invoker.exec_args()} returned {exit_code}"
            )
            raise TapDiscoveryError()


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
