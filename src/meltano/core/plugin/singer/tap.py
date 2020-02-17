import json
import logging
import subprocess
from typing import Dict
from jsonschema import Draft4Validator

from meltano.core.utils import file_has_data
from meltano.core.behavior.hookable import hook
from meltano.core.plugin.error import PluginExecutionError, PluginLacksCapabilityError

from . import SingerPlugin, PluginType
from .catalog import SelectExecutor


class SingerTap(SingerPlugin):
    __plugin_type__ = PluginType.EXTRACTORS

    def exec_args(self, plugin_invoker):
        """
        Return the arguments list with the complete runtime paths.
        """
        args = ["--config", plugin_invoker.files["config"]]

        catalog_path = plugin_invoker.files["catalog"]
        if file_has_data(catalog_path):
            if "catalog" in plugin_invoker.capabilities:
                args += ["--catalog", catalog_path]
            if "properties" in plugin_invoker.capabilities:
                args += ["--properties", catalog_path]

        state_path = plugin_invoker.files["state"]
        if "state" in plugin_invoker.capabilities and file_has_data(state_path):
            args += ["--state", state_path]

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

    @hook("before_invoke", can_fail=True)
    def run_discovery_hook(self, plugin_invoker, exec_args=[]):
        if "--discover" in exec_args:
            return

        try:
            self.run_discovery(plugin_invoker, exec_args)
        except PluginLacksCapabilityError:
            return

    def run_discovery(self, plugin_invoker, exec_args=[]):
        if not "discover" in plugin_invoker.capabilities:
            raise PluginLacksCapabilityError(
                f"Extractor '{self.name}' does not support schema discovery"
            )

        properties_file = plugin_invoker.files["catalog"]

        with properties_file.open("w") as catalog:
            result = plugin_invoker.invoke(
                "--discover",
                stdout=catalog,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            stdout, stderr = result.communicate()
            exit_code = result.returncode

        if exit_code != 0:
            properties_file.unlink()
            raise PluginExecutionError(
                f"Schema discovery failed: command {plugin_invoker.exec_args('--discover')} returned {exit_code}: {stderr.rstrip()}"
            )

        # test for the schema to be a valid catalog
        try:
            with properties_file.open("r") as catalog:
                schema_valid = Draft4Validator.check_schema(json.load(catalog))
        except Exception as err:
            properties_file.unlink()
            raise PluginExecutionError(
                "Schema discovery failed: invalid catalog output by --discovery."
            ) from err

    @hook("before_invoke", can_fail=True)
    def apply_select_hook(self, plugin_invoker, exec_args=[]):
        if "--discover" in exec_args:
            return

        try:
            self.apply_select(plugin_invoker, exec_args)
        except PluginLacksCapabilityError:
            return

    def apply_select(self, plugin_invoker, exec_args=[]):
        if (
            not "catalog" in plugin_invoker.capabilities
            and not "properties" in plugin_invoker.capabilities
        ):
            raise PluginLacksCapabilityError(
                f"Extractor '{self.name}' does not support selection"
            )

        properties_file = plugin_invoker.files["catalog"]

        try:
            with properties_file.open() as catalog:
                schema = json.load(catalog)

            reset_executor = SelectExecutor(["!*.*"])
            select_executor = SelectExecutor(plugin_invoker.select)

            reset_executor.visit(schema)
            select_executor.visit(schema)

            with properties_file.open("w") as catalog:
                json.dump(schema, catalog)
        except FileNotFoundError as err:
            raise PluginExecutionError(
                f"Selection failed: catalog file is missing."
            ) from err
        except Exception as err:
            properties_file.unlink()
            raise PluginExecutionError(
                f"Selection failed: catalog file is invalid: {properties_file}"
            ) from err
