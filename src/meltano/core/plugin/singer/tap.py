import json
import logging
import subprocess
import shutil
from typing import Dict
from jsonschema import Draft4Validator
from pathlib import Path
from hashlib import sha1

from meltano.core.setting_definition import SettingDefinition
from meltano.core.behavior.hookable import hook
from meltano.core.plugin.error import PluginExecutionError, PluginLacksCapabilityError
from meltano.core.plugin_invoker import InvokerError
from meltano.core.job import Payload, JobFinder
from meltano.core.utils import file_has_data, truthy, flatten, merge

from . import SingerPlugin, PluginType
from .catalog import (
    MetadataExecutor,
    MetadataRule,
    SchemaExecutor,
    SchemaRule,
    property_breadcrumb,
    select_metadata_rules,
    select_filter_metadata_rules,
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


class SingerTap(SingerPlugin):
    __plugin_type__ = PluginType.EXTRACTORS

    @property
    def extra_settings(self):
        return [
            SettingDefinition(name="_catalog"),
            SettingDefinition(name="_state"),
            SettingDefinition(
                name="_load_schema", value="$MELTANO_EXTRACTOR_NAMESPACE"
            ),
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
            "catalog_cache_key": "tap.properties.cache_key",
            "state": "state.json",
        }

    @property
    def output_files(self):
        return {"output": "tap.out"}

    @hook("before_invoke")
    def look_up_state_hook(self, plugin_invoker, exec_args=[]):
        if "--discover" in exec_args or "--help" in exec_args:
            return

        try:
            self.look_up_state(plugin_invoker, exec_args)
        except PluginLacksCapabilityError:
            pass

    def look_up_state(self, plugin_invoker, exec_args=[]):
        if "state" not in plugin_invoker.capabilities:
            raise PluginLacksCapabilityError(
                f"Extractor '{self.name}' does not support incremental state"
            )

        state_path = plugin_invoker.files["state"]

        try:
            # Delete state left over from different pipeline run for same extractor
            state_path.unlink()
        except FileNotFoundError:
            pass

        elt_context = plugin_invoker.context
        if not elt_context or not elt_context.job:
            # Running outside pipeline context: incremental state could not be loaded
            return

        if elt_context.full_refresh:
            logger.info(
                "Performing full refresh, ignoring state left behind by any previous runs."
            )
            return

        custom_state_filename = plugin_invoker.plugin_config_extras["_state"]
        if custom_state_filename:
            custom_state_path = plugin_invoker.project.root.joinpath(
                custom_state_filename
            )

            try:
                shutil.copy(custom_state_path, state_path)
                logger.info(f"Found state in {custom_state_filename}")
            except FileNotFoundError as err:
                raise PluginExecutionError(
                    f"Could not find state file {custom_state_path}"
                ) from err

            return

        # the `state.json` is stored in the database
        state = {}
        incomplete_since = None
        finder = JobFinder(elt_context.job.job_id)

        state_job = finder.latest_with_payload(elt_context.session, flags=Payload.STATE)
        if state_job:
            logger.info(f"Found state from {state_job.started_at}.")
            incomplete_since = state_job.ended_at
            if "singer_state" in state_job.payload:
                merge(state_job.payload["singer_state"], state)

        incomplete_state_jobs = finder.with_payload(
            elt_context.session, flags=Payload.INCOMPLETE_STATE, since=incomplete_since
        )
        for state_job in incomplete_state_jobs:
            logger.info(
                f"Found and merged incomplete state from {state_job.started_at}."
            )
            if "singer_state" in state_job.payload:
                merge(state_job.payload["singer_state"], state)

        if state:
            with state_path.open("w") as state_file:
                json.dump(state, state_file, indent=2)
        else:
            logger.warning("No state was found, complete import.")

    @hook("before_invoke")
    def discover_catalog_hook(self, plugin_invoker, exec_args=[]):
        if "--discover" in exec_args or "--help" in exec_args:
            return

        try:
            self.discover_catalog(plugin_invoker, exec_args)
        except PluginLacksCapabilityError:
            pass

    def discover_catalog(self, plugin_invoker, exec_args=[]):
        catalog_path = plugin_invoker.files["catalog"]
        catalog_cache_key_path = plugin_invoker.files["catalog_cache_key"]

        if catalog_path.exists():
            try:
                cached_key = catalog_cache_key_path.read_text()
                new_cache_key = self.catalog_cache_key(plugin_invoker)

                if cached_key == new_cache_key:
                    logger.debug(f"Using cached catalog file")
                    return
            except FileNotFoundError:
                pass

            logging.debug("Cached catalog is outdated, running discovery...")

        # We're gonna generate a new catalog, so delete the cache key.
        try:
            catalog_cache_key_path.unlink()
        except FileNotFoundError:
            pass

        custom_catalog_filename = plugin_invoker.plugin_config_extras["_catalog"]
        if custom_catalog_filename:
            custom_catalog_path = plugin_invoker.project.root.joinpath(
                custom_catalog_filename
            )

            try:
                shutil.copy(custom_catalog_path, catalog_path)
                logger.info(f"Found catalog in {custom_catalog_path}")
            except FileNotFoundError as err:
                raise PluginExecutionError(
                    f"Could not find catalog file {custom_catalog_path}"
                ) from err
        else:
            self.run_discovery(plugin_invoker, catalog_path)

        # test for the result to be a valid catalog
        try:
            with catalog_path.open("r") as catalog_file:
                catalog = json.load(catalog_file)
                schema_valid = Draft4Validator.check_schema(catalog)
        except Exception as err:
            catalog_path.unlink()
            raise PluginExecutionError(
                f"Catalog discovery failed: invalid catalog: {err}"
            ) from err

    def run_discovery(self, plugin_invoker, catalog_path):
        if not "discover" in plugin_invoker.capabilities:
            raise PluginLacksCapabilityError(
                f"Extractor '{self.name}' does not support catalog discovery (the `discover` capability is not advertised)"
            )

        try:
            with catalog_path.open("w") as catalog:
                result = plugin_invoker.invoke(
                    "--discover",
                    stdout=catalog,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                )
                stdout, stderr = result.communicate()
                exit_code = result.returncode
        except Exception:
            catalog_path.unlink()
            raise

        if exit_code != 0:
            catalog_path.unlink()
            raise PluginExecutionError(
                f"Catalog discovery failed: command {plugin_invoker.exec_args('--discover')} returned {exit_code}: {stderr.rstrip()}"
            )

    @hook("before_invoke")
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

        config = plugin_invoker.plugin_config_extras

        schema_rules = []
        metadata_rules = []

        # If a custom catalog is provided, don't apply catalog rules
        if not config["_catalog"]:
            schema_rules.extend(config_schema_rules(config["_schema"]))

            metadata_rules.extend(select_metadata_rules(["!*.*"]))
            metadata_rules.extend(select_metadata_rules(config["_select"]))
            metadata_rules.extend(config_metadata_rules(config["_metadata"]))

        # Always apply select filters (`meltano elt` `--select` and `--exclude` options)
        metadata_rules.extend(select_filter_metadata_rules(config["_select_filter"]))

        if not schema_rules and not metadata_rules:
            return

        catalog_path = plugin_invoker.files["catalog"]
        catalog_cache_key_path = plugin_invoker.files["catalog_cache_key"]

        try:
            with catalog_path.open() as catalog_file:
                catalog = json.load(catalog_file)

            if schema_rules:
                SchemaExecutor(schema_rules).visit(catalog)

            if metadata_rules:
                MetadataExecutor(metadata_rules).visit(catalog)

            with catalog_path.open("w") as catalog_file:
                json.dump(catalog, catalog_file, indent=2)

            cache_key = self.catalog_cache_key(plugin_invoker)
            if cache_key:
                catalog_cache_key_path.write_text(cache_key)
            else:
                try:
                    catalog_cache_key_path.unlink()
                except FileNotFoundError:
                    pass
        except FileNotFoundError as err:
            raise PluginExecutionError(
                f"Applying catalog rules failed: catalog file is missing."
            ) from err
        except Exception as err:
            catalog_path.unlink()
            raise PluginExecutionError(
                f"Applying catalog rules failed: catalog file is invalid: {err}"
            ) from err

    def catalog_cache_key(self, plugin_invoker):
        # If the extractor is installed as editable, don't cache because
        # the result of discovery could change at any time.
        if plugin_invoker.plugin_def.pip_url.startswith("-e"):
            return None

        extras = plugin_invoker.plugin_config_extras

        # If a custom catalog is provided, there's no need to cache
        if extras["_catalog"]:
            return None

        # The catalog should be regenerated, and the catalog cache invalidated,
        # if any settings changed that could affect discovery, or if schema or
        # metadata rules changed.
        # Changes to selection rules and selection filter rules are ignored,
        # since "selected" metadata is reset using the `!*.*` selection rule anyway.
        key_dict = {
            **plugin_invoker.plugin_config,
            "_schema": extras["_schema"],
            "_metadata": extras["_metadata"],
        }

        key_json = json.dumps(key_dict)

        return sha1(key_json.encode()).hexdigest()
