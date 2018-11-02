import logging
import os
import json
from typing import Dict

from . import Plugin, PluginType
from .error import TapDiscoveryError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.utils import file_has_data
from meltano.core.behavior.hookable import HookObject, hook


def plugin_factory(plugin_type: PluginType, canonical: Dict):
    plugin_class = {PluginType.EXTRACTORS: SingerTap, PluginType.LOADERS: SingerTarget}

    # this will parse the discovery file and create an instance of the
    # corresponding `plugin_class` for all the plugins.
    return plugin_class[plugin_type](**canonical)


class SingerPlugin(Plugin, HookObject):
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    @hook("before_install")
    def install_config_stub(self, project):
        plugin_dir = project.plugin_dir(self)
        os.makedirs(plugin_dir, exist_ok=True)

        # TODO: refactor as explicit stubs
        with open(plugin_dir.joinpath(self.config_files["config"]), "w") as config:
            json.dump(self.config, config)


class SingerTap(SingerPlugin):
    __plugin_type__ = PluginType.EXTRACTORS

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

    @hook("before_invoke")
    def run_discovery(self, plugin_invoker, exec_args):
        if not self._extras.get("autodiscover", True):
            return

        if "--discover" in exec_args:
            return

        properties_file = plugin_invoker.files["catalog"]

        with properties_file.open("w") as catalog:
            result = plugin_invoker.invoke("--discover", stdout=catalog)
            exit_code = result.wait()

        if exit_code != 0:
            logging.error(
                f"Command {plugin_invoker.exec_path()} {plugin_invoker.exec_args()} returned {exit_code}"
            )
            return

        try:
            with properties_file.open() as catalog:
                schema = json.load(catalog)

            for stream in schema["streams"]:
                stream_metadata = next(
                    metadata
                    for metadata in stream["metadata"]
                    if len(metadata["breadcrumb"]) == 0
                )
                stream_metadata["metadata"].update({"selected": True})

            with properties_file.open("w") as catalog:
                json.dump(schema, catalog)
        except Exception as err:
            logging.error(
                f"Could not select stream, catalog file is invalid: {properties_file}"
            )


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
