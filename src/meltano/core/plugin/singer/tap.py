"""This module contains the SingerTap class as well as a supporting methods."""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
import sys
from asyncio.streams import StreamReader
from hashlib import sha1
from io import StringIO
from pathlib import Path

import structlog
from jsonschema import Draft4Validator

from meltano.core.behavior.hookable import hook
from meltano.core.plugin.error import PluginExecutionError, PluginLacksCapabilityError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.state_service import SINGER_STATE_KEY, StateService
from meltano.core.utils import file_has_data, flatten

from . import PluginType, SingerPlugin
from .catalog import (
    MetadataExecutor,
    MetadataRule,
    SchemaExecutor,
    SchemaRule,
    property_breadcrumb,
    select_filter_metadata_rules,
    select_metadata_rules,
)

logger = structlog.getLogger(__name__)


async def _stream_redirect(
    stream: asyncio.StreamReader, *file_like_objs, write_str=False
):
    """Redirect stream to a file like obj.

    Args:
        stream: the stream to redirect
        file_like_objs: the objects to redirect the stream to
        write_str: if True, stream is written as str
    """
    encoding = sys.getdefaultencoding()
    while not stream.at_eof():
        data = await stream.readline()
        for file_like_obj in file_like_objs:
            file_like_obj.write(data.decode(encoding) if write_str else data)


def _debug_logging_handler(
    name: str, plugin_invoker: PluginInvoker, stderr: StreamReader, *other_dsts
) -> asyncio.Task:
    """Route debug log lines to stderr or an OutputLogger if one is present in our invocation context.

    Args:
        name: name of the plugin
        plugin_invoker: the PluginInvoker to route log lines for
        stderr: stderr StreamReader to route to
        other_dsts: other destinations that the stream should be routed too along with logging output

    Returns:
        asyncio.Task which performs the routing of log lines
    """
    if not plugin_invoker.context or not plugin_invoker.context.base_output_logger:
        return asyncio.ensure_future(
            _stream_redirect(
                stderr, *(sys.stderr, *other_dsts), write_str=True  # noqa: WPS517
            )
        )

    out = plugin_invoker.context.base_output_logger.out(
        name, logger.bind(type="discovery", stdio="stderr")
    )
    with out.line_writer() as outerr:
        return asyncio.ensure_future(
            _stream_redirect(
                stderr, *(outerr, *other_dsts), write_str=True  # noqa: WPS517
            )
        )


def config_metadata_rules(config):
    """Get metadata rules from config.

    Args:
        config: configuration dict

    Returns:
        a list of MetadataRule
    """
    flat_config = flatten(config, "dot")

    rules = []
    for key, value in flat_config.items():
        # <tap_stream_id>.<key>
        # <tap_stream_id>.<prop>.<key>
        # <tap_stream_id>.<prop>.<subprop>.<key>
        # <tap_stream_id>.properties.<prop>.<key>
        # <tap_stream_id>.properties.<prop>.properties.<subprop>.<key>
        tap_stream_id, *props, rule_key = key.split(".")

        rules.append(
            MetadataRule(
                tap_stream_id=tap_stream_id,
                breadcrumb=property_breadcrumb(props),
                key=rule_key,
                value=value,
            )
        )

    return rules


def config_schema_rules(config):
    """Get schema rules from config.

    Args:
        config: configuration dict

    Returns:
        a list of SchemaRule
    """
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
    """A Plugin for Singer Taps."""

    __plugin_type__ = PluginType.EXTRACTORS

    EXTRA_SETTINGS = [
        SettingDefinition(name="_catalog"),
        SettingDefinition(name="_state"),
        SettingDefinition(name="_load_schema", value="$MELTANO_EXTRACTOR_NAMESPACE"),
        SettingDefinition(name="_select", kind=SettingKind.ARRAY, value=["*.*"]),
        SettingDefinition(
            name="_metadata",
            aliases=["metadata"],
            kind=SettingKind.OBJECT,
            value={},
            value_processor="nest_object",
        ),
        SettingDefinition(
            name="_schema",
            kind=SettingKind.OBJECT,
            value={},
            value_processor="nest_object",
        ),
        SettingDefinition(name="_select_filter", kind=SettingKind.ARRAY, value=[]),
    ]

    def exec_args(self, plugin_invoker):
        """Return the arguments list with the complete runtime paths.

        Args:
            plugin_invoker: the plugin invoker running

        Returns:
            the command line arguments to be passed to the tap
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
        """Get the configuration files for this tap."""
        return {  # noqa: DAR201
            "config": f"tap.{self.instance_uuid}.config.json",
            "catalog": "tap.properties.json",
            "catalog_cache_key": "tap.properties.cache_key",
            "state": "state.json",
        }

    @property
    def output_files(self):
        """Get the output files for this tap."""
        return {"output": "tap.out"}  # noqa: DAR201

    @hook("before_invoke")
    async def look_up_state_hook(
        self,
        plugin_invoker: PluginInvoker,
        exec_args: tuple[str, ...] = (),
    ):
        """Look up state before being invoked if in sync mode.

        Args:
            plugin_invoker: the plugin invoker running
            exec_args: the args being passed to the tap

        Returns:
            None
        """
        # Use state only in sync mode (i.e. no args)
        if exec_args:
            return

        try:
            await self.look_up_state(plugin_invoker)
        except PluginLacksCapabilityError:
            pass

    async def look_up_state(  # noqa: WPS231, WPS213
        self, plugin_invoker: PluginInvoker
    ):
        """Look up state, cleaning up and refreshing as needed.

        Args:
            plugin_invoker: the plugin invoker running

        Returns:
            None

        Raises:
            PluginExecutionError: if state could not be found for this plugin
            PluginLacksCapabilityError: if this plugin does not support incremental state
        """
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
        state = StateService(elt_context.session).get_state(elt_context.job.job_name)
        if state:
            if state.get(SINGER_STATE_KEY):
                with state_path.open("w") as state_file:
                    json.dump(state.get(SINGER_STATE_KEY), state_file, indent=2)
        else:
            logger.warning("No state was found, complete import.")

    @hook("before_invoke")
    async def discover_catalog_hook(
        self,
        plugin_invoker: PluginInvoker,
        exec_args: tuple[str, ...] = (),
    ):
        """Discover Singer catalog before invoking tap if in sync mode.

        Args:
            plugin_invoker: The invocation handler of the plugin instance.
            exec_args: List of subcommand/args that we where invoked with.

        Returns:
            None
        """
        # Discover only in sync mode (i.e. no args)
        if exec_args:
            return

        try:
            await self.discover_catalog(plugin_invoker)
        except PluginLacksCapabilityError:
            pass

    async def discover_catalog(self, plugin_invoker: PluginInvoker):  # noqa: WPS231
        """Perform catalog discovery.

        Args:
            plugin_invoker: The invocation handler of the plugin instance.

        Returns:
            None

        Raises:
            PluginExecutionError: if discovery could not be performed
        """
        catalog_path = plugin_invoker.files["catalog"]
        catalog_cache_key_path = plugin_invoker.files["catalog_cache_key"]
        if catalog_path.exists():
            try:
                cached_key = catalog_cache_key_path.read_text()
                new_cache_key = self.catalog_cache_key(plugin_invoker)

                if cached_key == new_cache_key:
                    logger.debug("Using cached catalog file")
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
            await self.run_discovery(plugin_invoker, catalog_path)

        # test for the result to be a valid catalog
        try:
            with catalog_path.open("r") as catalog_file:
                catalog = json.load(catalog_file)
                Draft4Validator.check_schema(catalog)
        except Exception as err:
            catalog_path.unlink()
            raise PluginExecutionError(
                f"Catalog discovery failed: invalid catalog: {err}"
            ) from err

    async def run_discovery(  # noqa: WPS238
        self, plugin_invoker: PluginInvoker, catalog_path: Path
    ):  # noqa: DAR401
        """Run tap in discovery mode and store the result.

        Args:
            plugin_invoker: The invocation handler of the plugin instance.
            catalog_path: Where discovery output should be written.

        Raises:
            PluginExecutionError: if state could not be found for this plugin
            PluginLacksCapabilityError: if this plugin does not support incremental state
            Exception: if any other exception occurs
        """
        if "discover" not in plugin_invoker.capabilities:
            raise PluginLacksCapabilityError(
                f"Extractor '{self.name}' does not support catalog discovery (the `discover` capability is not advertised)"
            )
        with StringIO("") as stderr_buff:
            try:
                with catalog_path.open(mode="wb") as catalog:
                    handle = await plugin_invoker.invoke_async(
                        "--discover",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        universal_newlines=False,
                    )

                    invoke_futures = [
                        asyncio.ensure_future(_stream_redirect(handle.stdout, catalog)),
                        asyncio.ensure_future(handle.wait()),
                    ]
                    if logger.isEnabledFor(logging.DEBUG) and handle.stderr:
                        invoke_futures.append(
                            _debug_logging_handler(
                                self.name,
                                plugin_invoker,
                                handle.stderr,
                                stderr_buff,
                            )
                        )
                    else:
                        invoke_futures.append(
                            asyncio.ensure_future(
                                _stream_redirect(
                                    handle.stderr, stderr_buff, write_str=True
                                )
                            )
                        )
                    done, _ = await asyncio.wait(
                        invoke_futures,
                        return_when=asyncio.ALL_COMPLETED,
                    )
                    failed = [
                        future for future in done if future.exception() is not None
                    ]
                    if failed:
                        failed_future = failed.pop()
                        raise failed_future.exception()
                exit_code = handle.returncode
            except Exception:
                catalog_path.unlink()
                raise

            if exit_code != 0:
                catalog_path.unlink()
                stderr_buff.seek(0)
                raise PluginExecutionError(
                    f"Catalog discovery failed: command {plugin_invoker.exec_args('--discover')} returned {exit_code} with stderr:\n {stderr_buff.read()}"
                )

    @hook("before_invoke")
    async def apply_catalog_rules_hook(
        self, plugin_invoker: PluginInvoker, exec_args: tuple[str, ...] = ()
    ):
        """Apply catalog rules before invoke if in sync mode.

        Args:
            plugin_invoker: the plugin invoker running
            exec_args: the argumnets to pass to the tap

        Returns:
            None
        """
        # Apply only in sync mode (i.e. no args)
        if exec_args:
            return

        try:
            self.apply_catalog_rules(plugin_invoker, exec_args)
        except PluginLacksCapabilityError:
            pass

    def apply_catalog_rules(  # noqa: WPS213,WPS231
        self,
        plugin_invoker: PluginInvoker,
        exec_args: tuple[str, ...] = (),
    ):
        """Apply Singer catalog and schema rules to discovered catalog.

        Args:
            plugin_invoker: the plugin invoker running
            exec_args: the argumnets to pass to the tap

        Returns:
            None

        Raises:
            PluginLacksCapabilityError: if plugin does not support entity selection
            PluginExecutionError: if catalog rules could not be applied
        """
        if (
            "catalog" not in plugin_invoker.capabilities
            and "properties" not in plugin_invoker.capabilities
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

            with catalog_path.open("w") as catalog_f:
                json.dump(catalog, catalog_f, indent=2)

            cache_key = self.catalog_cache_key(plugin_invoker)
            if cache_key:
                catalog_cache_key_path.write_text(cache_key)
            else:
                try:  # noqa: WPS505
                    catalog_cache_key_path.unlink()
                except FileNotFoundError:
                    pass
        except FileNotFoundError as err:
            raise PluginExecutionError(
                "Applying catalog rules failed: catalog file is missing."
            ) from err
        except Exception as err:
            catalog_path.unlink()
            raise PluginExecutionError(
                f"Applying catalog rules failed: catalog file is invalid: {err}"
            ) from err

    def catalog_cache_key(self, plugin_invoker):
        """Get a cache key for the catalog.

        Args:
            plugin_invoker: the plugin invoker running

        Returns:
            the cache key for the catalog, if plugin catalog can be cached
        """
        # Treat non-pip plugins as editable/dev-mode plugins and do not cache.
        if plugin_invoker.plugin.pip_url is None:
            return None

        # If the extractor is installed as editable, don't cache because
        # the result of discovery could change at any time.
        if plugin_invoker.plugin.pip_url.startswith("-e"):
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

        return sha1(key_json.encode()).hexdigest()  # noqa: S303 S324
