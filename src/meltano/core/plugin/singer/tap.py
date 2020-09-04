import json
import logging
import subprocess
from typing import Dict
from jsonschema import Draft4Validator

from meltano.core.setting_definition import SettingDefinition
from meltano.core.behavior.hookable import hook
from meltano.core.plugin.error import PluginExecutionError, PluginLacksCapabilityError
from meltano.core.plugin_invoker import InvokerError
from meltano.core.utils import file_has_data, truthy, flatten

from . import SingerPlugin, PluginType
from .catalog import (
    MetadataExecutor,
    MetadataRule,
    SchemaExecutor,
    SchemaRule,
    property_breadcrumb,
    select_metadata_rules,
)

logger = logging.getLogger(__name__)


def config_metadata_rules(config):
    flat_config = flatten(config, "dot")

    rules = []
    for key, value in flat_config.items():
        # <tap_stream_id>.<key>
        # <tap_stream_id>.<prop>.<key>
        # <tap_stream_id>.<prop>.<subprop>.<key>
        # <tap_stream_id>.properties.<prop>.<key>
        # <tap_stream_id>.properties.<prop>.properties.<subprop>.<key>
        tap_stream_id, *props, key = key.split(".")

        rules.append(
            MetadataRule(
                tap_stream_id=tap_stream_id,
                breadcrumb=property_breadcrumb(props),
                key=key,
                value=value,
            )
        )

    return rules


def config_schema_rules(config):
    return [
        SchemaRule(
            tap_stream_id=tap_stream_id,
            breadcrumb=["properties", prop],
            payload=payload,
        )
        for tap_stream_id, stream_config in config.items()
        for prop, payload in stream_config.items()
    ]


def select_filter_metadata_rules(tap_stream_ids):
    if not tap_stream_ids:
        return []

    metadata_rules = select_metadata_rules(
        [f"{tap_stream_id}." for tap_stream_id in tap_stream_ids]
    )

    has_include_rules = any(rule.value for rule in metadata_rules)
    if has_include_rules:
        metadata_rules = [
            # First deselect all stream nodes, without touching their property nodes
            *select_metadata_rules(["!*."]),
            # Then (de)select only the specified stream nodes
            *metadata_rules,
        ]

    return metadata_rules


class SingerTap(SingerPlugin):
    __plugin_type__ = PluginType.EXTRACTORS

    @property
    def extra_settings(self):
        return [
            SettingDefinition(name="_select", kind="array", value=["*.*"]),
            SettingDefinition(
                name="_metadata",
                aliases=["metadata"],
                kind="object",
                value={},
                value_processor="nest_object",
            ),
            SettingDefinition(
                name="_schema", kind="object", value={}, value_processor="nest_object"
            ),
            SettingDefinition(name="_select_filter", kind="array", value=[]),
        ]

    def exec_args(self, plugin_invoker):
        """
        Return the arguments list with the complete runtime paths.
        """
        args = ["--config", plugin_invoker.files["config"]]

        catalog_path = plugin_invoker.files["catalog"]
        if file_has_data(catalog_path):
            if "catalog" in plugin_invoker.capabilities:
                args += ["--catalog", catalog_path]
            elif "properties" in plugin_invoker.capabilities:
                args += ["--properties", catalog_path]
            else:
                logger.warn(
                    "A catalog file was found, but it will be ignored as the extractor does not advertise the `catalog` or `properties` capability"
                )

        state_path = plugin_invoker.files["state"]
        if file_has_data(state_path):
            if "state" in plugin_invoker.capabilities:
                args += ["--state", state_path]
            else:
                logger.warn(
                    "A state file was found, but it will be ignored as the extractor does not advertise the `state` capability"
                )

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

    @hook("before_invoke", can_fail=PluginExecutionError)
    def run_discovery_hook(self, plugin_invoker, exec_args=[]):
        if "--discover" in exec_args or "--help" in exec_args:
            return

        try:
            self.run_discovery(plugin_invoker, exec_args)
        except PluginLacksCapabilityError:
            pass

    def run_discovery(self, plugin_invoker, exec_args=[]):
        if not "discover" in plugin_invoker.capabilities:
            raise PluginLacksCapabilityError(
                f"Extractor '{self.name}' does not support catalog discovery (the `discover` capability is not advertised)"
            )

        properties_file = plugin_invoker.files["catalog"]

        try:
            with properties_file.open("w") as catalog:
                result = plugin_invoker.invoke(
                    "--discover",
                    stdout=catalog,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                )
                stdout, stderr = result.communicate()
                exit_code = result.returncode
        except Exception:
            properties_file.unlink()
            raise

        if exit_code != 0:
            properties_file.unlink()
            raise PluginExecutionError(
                f"Catalog discovery failed: command {plugin_invoker.exec_args('--discover')} returned {exit_code}: {stderr.rstrip()}"
            )

        # test for the schema to be a valid catalog
        try:
            with properties_file.open("r") as catalog:
                catalog_json = json.load(catalog)
                schema_valid = Draft4Validator.check_schema(catalog_json)
        except Exception as err:
            properties_file.unlink()
            raise PluginExecutionError(
                f"Catalog discovery failed: invalid catalog output by --discover: {err}"
            ) from err

    @hook("before_invoke", can_fail=PluginExecutionError)
    def apply_catalog_rules_hook(self, plugin_invoker, exec_args=[]):
        if "--discover" in exec_args or "--help" in exec_args:
            return

        try:
            self.apply_catalog_rules(plugin_invoker, exec_args)
        except PluginLacksCapabilityError:
            pass

    def apply_catalog_rules(self, plugin_invoker, exec_args=[]):
        if (
            not "catalog" in plugin_invoker.capabilities
            and not "properties" in plugin_invoker.capabilities
        ):
            raise PluginLacksCapabilityError(
                f"Extractor '{self.name}' does not support entity selection or catalog metadata and schema rules"
            )

        properties_file = plugin_invoker.files["catalog"]

        try:
            with properties_file.open() as catalog:
                schema = json.load(catalog)

            config = plugin_invoker.plugin_config_extras

            schema_rules = config_schema_rules(config["_schema"])
            SchemaExecutor(schema_rules).visit(schema)

            metadata_rules = [
                *select_metadata_rules(["!*.*"]),
                *select_metadata_rules(config["_select"]),
                *config_metadata_rules(config["_metadata"]),
                *select_filter_metadata_rules(config["_select_filter"]),
            ]
            MetadataExecutor(metadata_rules).visit(schema)

            with properties_file.open("w") as catalog:
                json.dump(schema, catalog, indent=2)
        except FileNotFoundError as err:
            raise PluginExecutionError(
                f"Applying catalog rules failed: catalog file is missing."
            ) from err
        except Exception as err:
            properties_file.unlink()
            raise PluginExecutionError(
                f"Applying catalog rules failed: catalog file is invalid: {err}"
            ) from err
