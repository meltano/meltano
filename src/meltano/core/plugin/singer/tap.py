import json
import logging
from typing import Dict
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.utils import file_has_data
from meltano.core.behavior.hookable import hook
from meltano.core.plugin.error import PluginExecutionError

from . import SingerPlugin, PluginType
from .catalog import visit, SelectExecutor


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
    def run_discovery(self, plugin_invoker, exec_args=[]):
        if not self._extras.get("autodiscover", True):
            return

        if "--discover" in exec_args:
            return

        properties_file = plugin_invoker.files["catalog"]

        with properties_file.open("w") as catalog:
            result = plugin_invoker.invoke("--discover", stdout=catalog)
            exit_code = result.wait()

        if exit_code != 0:
            properties_file.unlink()
            raise PluginExecutionError(
                f"Command {plugin_invoker.exec_path()} {plugin_invoker.exec_args()} returned {exit_code}"
            )

    @hook("before_invoke")
    def apply_select(self, plugin_invoker, exec_args=[]):
        if "--discover" in exec_args:
            return

        properties_file = plugin_invoker.files["catalog"]

        try:
            with properties_file.open() as catalog:
                schema = json.load(catalog)

            reset_executor = SelectExecutor(["!*.*"])
            select_executor = SelectExecutor(self.select)
            visit(schema, reset_executor)
            visit(schema, select_executor)

            with properties_file.open("w") as catalog:
                json.dump(schema, catalog)
        except FileNotFoundError:
            raise PluginExecutionError(
                f"Could not select stream, catalog file is missing."
            )
        except Exception as err:
            properties_file.unlink()
            raise PluginExecutionError(
                f"Could not select stream, catalog file is invalid: {properties_file}"
            ) from err
