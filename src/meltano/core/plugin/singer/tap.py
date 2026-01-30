"""This module contains the SingerTap class as well as a supporting methods."""

from __future__ import annotations

import asyncio
import asyncio.subprocess
import json
import logging
import shutil
import sys
import typing as t
from contextlib import suppress
from functools import lru_cache, reduce
from hashlib import sha1
from io import StringIO
from itertools import takewhile

import structlog

from meltano.core.behavior.hookable import hook
from meltano.core.logging import capture_subprocess_output
from meltano.core.logging.output_logger import OutputLogger
from meltano.core.plugin.error import PluginExecutionError, PluginLacksCapabilityError
from meltano.core.setting_definition import SettingDefinition, SettingKind, json_dumps
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

if t.TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.orm import Session

    from meltano.core.plugin_invoker import PluginInvoker
    from meltano.core.project import Project

    from .catalog import CatalogDict

logger = structlog.stdlib.get_logger(__name__)


async def _stream_redirect(
    stream: asyncio.StreamReader | None,
    *file_like_objs: t.IO,
    write_str: bool = False,
) -> None:
    """Redirect stream to a file like obj.

    Args:
        stream: the stream to redirect
        file_like_objs: the objects to redirect the stream to
        write_str: if True, stream is written as str
    """
    encoding = sys.getdefaultencoding()
    while stream and not stream.at_eof():
        data = await stream.readline()
        for file_like_obj in file_like_objs:
            file_like_obj.write(data.decode(encoding) if write_str else data)


def config_metadata_rules(config: dict[str, t.Any]) -> list[MetadataRule]:
    """Get metadata rules from config.

    Args:
        config: configuration dict

    Returns:
        a list of MetadataRule
    """
    flat_config: dict[str, t.Any] = flatten(config, "dot")

    rules: list[MetadataRule] = []
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
            ),
        )

    return rules


def config_schema_rules(config: dict[str, t.Any]) -> list[SchemaRule]:
    """Get schema rules from config.

    Args:
        config: configuration dict

    Returns:
        a list of SchemaRule
    """
    return [
        SchemaRule(
            tap_stream_id=tap_stream_id,
            breadcrumb=property_breadcrumb([prop]),
            payload=payload,
        )
        for tap_stream_id, stream_config in config.items()
        for prop, payload in stream_config.items()
    ]


class SingerTap(SingerPlugin):
    """A Plugin for Singer Taps."""

    __plugin_type__ = PluginType.EXTRACTORS

    EXTRA_SETTINGS: t.ClassVar[list[SettingDefinition]] = [
        *SingerPlugin.EXTRA_SETTINGS,
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
        SettingDefinition(
            name="_use_cached_catalog",
            kind=SettingKind.BOOLEAN,
            value=True,
        ),
    ]

    def exec_args(self, plugin_invoker):  # noqa: ANN001, ANN201
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
                logger.warning(
                    "A catalog file was found, but it will be ignored as the "
                    "extractor does not advertise the `catalog` or "
                    "`properties` capability",
                )

        state_path = plugin_invoker.files["state"]
        if file_has_data(state_path):
            if "state" in plugin_invoker.capabilities:
                args += ["--state", state_path]
            else:
                logger.warning(
                    "A state file was found, but it will be ignored as the "
                    "extractor does not advertise the `state` capability",
                )

        return args

    @property
    def config_files(self):  # noqa: ANN201
        """Get the configuration files for this tap."""
        return {
            "config": f"tap.{self.instance_uuid}.config.json",
            "catalog": "tap.properties.json",
            "catalog_cache_key": "tap.properties.cache_key",
            "state": "state.json",
            "singer_sdk_logging": "tap.singer_sdk_logging.json",
            "pipelinewise_singer_logging": "tap.pipelinewise_logging.conf",
        }

    @property
    def output_files(self):  # noqa: ANN201
        """Get the output files for this tap."""
        return {"output": "tap.out"}

    @hook("before_invoke")
    async def look_up_state_hook(
        self,
        plugin_invoker: PluginInvoker,
        exec_args: tuple[str, ...] = (),
    ) -> None:
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

        with suppress(PluginLacksCapabilityError):
            await self.look_up_state(plugin_invoker)

    async def look_up_state(
        self,
        plugin_invoker: PluginInvoker,
    ) -> None:
        """Look up state, cleaning up and refreshing as needed.

        Args:
            plugin_invoker: the plugin invoker running

        Returns:
            None

        Raises:
            PluginExecutionError: if state could not be found for this plugin
            PluginLacksCapabilityError: if this plugin does not support
                incremental state
        """
        if "state" not in plugin_invoker.capabilities:
            msg = f"Extractor '{self.name}' does not support incremental state"
            raise PluginLacksCapabilityError(msg)

        state_path = plugin_invoker.files["state"]
        state_path.unlink(missing_ok=True)

        elt_context = plugin_invoker.context
        if not elt_context or not elt_context.job:
            # Running outside pipeline context: incremental state could not be loaded
            return

        if elt_context.full_refresh:
            logger.info(
                "Performing full refresh, ignoring state left behind by any "
                "previous runs.",
            )
            return

        if custom_state_filename := plugin_invoker.plugin_config_extras["_state"]:
            custom_state_path = plugin_invoker.project.root.joinpath(
                custom_state_filename,
            )

            try:
                shutil.copy(custom_state_path, state_path)
            except FileNotFoundError as err:
                msg = f"Could not find state file {custom_state_path}"
                raise PluginExecutionError(msg) from err

            logger.info("Found state in %s", custom_state_filename)
            return

        # the `state.json` is stored in a state backend
        if state := self.get_singer_state(
            project=elt_context.project,
            session=elt_context.session,  # type: ignore[arg-type]
            job_name=elt_context.job.job_name,
        ):
            with state_path.open("w") as state_file:
                json.dump(state, state_file, indent=2)
        else:
            logger.warning("No state was found, complete import.")

    def get_singer_state(
        self,
        *,
        project: Project,
        session: Session,
        job_name: str,
    ) -> dict | None:
        """Get the state for the given job.

        Args:
            project: the project
            session: the session
            job_name: the job name

        Returns:
            the state for the given job
        """
        state_service = StateService(project=project, session=session)
        try:
            state = state_service.get_state(job_name)
        except Exception as err:  # pragma: no cover
            logger.error(  # noqa: TRY400
                err.args[0],
                state_backend=state_service.state_store_manager.label,
            )
            msg = "Failed to retrieve state"
            raise PluginExecutionError(msg) from err

        return state.get(SINGER_STATE_KEY)

    @hook("before_invoke")
    async def discover_catalog_hook(
        self,
        plugin_invoker: PluginInvoker,
        exec_args: tuple[str, ...] = (),
    ) -> None:
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

        with suppress(PluginLacksCapabilityError):
            await self.discover_catalog(plugin_invoker)

    async def _get_catalog(self, plugin_invoker: PluginInvoker) -> Path:
        """Get the user-provided or discovered catalog file.

        Args:
            plugin_invoker: The invocation handler of the plugin instance.

        Returns:
            Path to the catalog file.

        Raises:
            PluginExecutionError: if discovery could not be performed
        """
        catalog_path = plugin_invoker.files["catalog"]
        catalog_cache_key_path = plugin_invoker.files["catalog_cache_key"]
        elt_context = plugin_invoker.context

        if custom_catalog_filename := plugin_invoker.plugin_config_extras["_catalog"]:
            custom_catalog_path = plugin_invoker.project.root / custom_catalog_filename
            try:
                shutil.copy(custom_catalog_path, catalog_path)
            except OSError as err:
                msg = f"Failed to copy catalog file: {err.strerror}"
                raise PluginExecutionError(msg) from err

            logger.info("Using custom catalog in %s", custom_catalog_path)
            return catalog_path

        use_cached_catalog = (
            not (elt_context and elt_context.should_refresh_catalog())
            and plugin_invoker.plugin_config_extras["_use_cached_catalog"]
        )

        if catalog_path.exists() and use_cached_catalog:
            with suppress(FileNotFoundError):
                cached_key = catalog_cache_key_path.read_text()
                new_cache_key = self.catalog_cache_key(plugin_invoker)

                if cached_key == new_cache_key:
                    logger.debug("Using cached catalog file")
                    return catalog_path
            logger.debug("Cached catalog is outdated, running discovery...")

        # We're gonna generate a new catalog, so delete the cache key.
        with suppress(FileNotFoundError):
            catalog_cache_key_path.unlink()

        await self.run_discovery(plugin_invoker, catalog_path)
        return catalog_path

    async def discover_catalog(self, plugin_invoker: PluginInvoker) -> None:
        """Perform catalog discovery.

        Args:
            plugin_invoker: The invocation handler of the plugin instance.

        Returns:
            None
        """
        catalog_path = await self._get_catalog(plugin_invoker)

        # test for the result to be a valid catalog
        try:
            with catalog_path.open() as catalog_file:
                json.load(catalog_file)
        except Exception as err:
            catalog_path.unlink()
            msg = f"Catalog discovery failed: {err}"
            if isinstance(err, json.JSONDecodeError):
                logger.error(  # noqa: TRY400
                    "Invalid JSON: %s [...]",
                    err.doc[max(err.pos - 9, 0) : err.pos + 10],
                )
                msg = "Invalid catalog"

            raise PluginExecutionError(msg) from err

    async def run_discovery(
        self,
        plugin_invoker: PluginInvoker,
        catalog_path: Path,
    ) -> None:
        """Run tap in discovery mode and store the result.

        Args:
            plugin_invoker: The invocation handler of the plugin instance.
            catalog_path: Where discovery output should be written.

        Raises:
            PluginExecutionError: if state could not be found for this plugin.
            PluginLacksCapabilityError: if this plugin does not support
                incremental state.
            Exception: if any other exception occurs.
        """
        if "discover" not in plugin_invoker.capabilities:
            raise PluginLacksCapabilityError(  # noqa: TRY003
                f"Extractor '{self.name}' does not support catalog discovery "  # noqa: EM102
                "(the `discover` capability is not advertised)",
            )
        logger.info("Running catalog discovery")
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
                    if (
                        plugin_invoker.stderr_logger.isEnabledFor(logging.DEBUG)
                        and handle.stderr is not None
                    ):
                        out = OutputLogger("discovery.log").out(
                            self.name,
                            plugin_invoker.stderr_logger.bind(type="discovery"),
                            log_parser=plugin_invoker.get_log_parser(),
                        )
                        future = capture_subprocess_output(handle.stderr, out)
                        invoke_futures.append(asyncio.ensure_future(future))
                    else:
                        invoke_futures.append(
                            asyncio.ensure_future(
                                _stream_redirect(
                                    handle.stderr,
                                    stderr_buff,
                                    write_str=True,
                                ),
                            ),
                        )
                    done, _ = await asyncio.wait(
                        invoke_futures,
                        return_when=asyncio.ALL_COMPLETED,
                    )
                    if failed := [
                        future for future in done if future.exception() is not None
                    ]:
                        failed_future = failed.pop()
                        raise failed_future.exception()  # type: ignore[misc]  # noqa: TRY301
                exit_code = handle.returncode
            except Exception:
                catalog_path.unlink()
                raise

            if exit_code != 0:
                catalog_path.unlink()
                stderr_buff.seek(0)
                raise PluginExecutionError(  # noqa: TRY003
                    "Catalog discovery failed: command "  # noqa: EM102
                    f"{plugin_invoker.exec_args('--discover')} returned "
                    f"{exit_code} with stderr:\n {stderr_buff.read()}",
                )

    @hook("before_invoke")
    async def apply_catalog_rules_hook(
        self,
        plugin_invoker: PluginInvoker,
        exec_args: tuple[str, ...] = (),
    ) -> None:
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

        with suppress(PluginLacksCapabilityError):
            await self.apply_catalog_rules(plugin_invoker, exec_args)

    async def apply_catalog_rules(
        self,
        plugin_invoker: PluginInvoker,
        exec_args: tuple[str, ...] = (),  # noqa: ARG002
    ) -> None:
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
            raise PluginLacksCapabilityError(  # noqa: TRY003
                f"Extractor '{self.name}' does not support entity selection "  # noqa: EM102
                "or catalog metadata and schema rules",
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

        # Always apply select filters (`meltano el` `--select` and `--exclude` options)
        metadata_rules.extend(select_filter_metadata_rules(config["_select_filter"]))

        if not schema_rules and not metadata_rules:
            return

        catalog_path = plugin_invoker.files["catalog"]
        catalog_cache_key_path = plugin_invoker.files["catalog_cache_key"]

        try:
            with catalog_path.open() as catalog_file:
                catalog = json.load(catalog_file)

            if schema_rules:
                SchemaExecutor(schema_rules).visit(catalog)  # type: ignore[attr-defined]

            if metadata_rules:
                self.warn_property_not_found(metadata_rules, catalog)
                MetadataExecutor(metadata_rules).visit(catalog)  # type: ignore[attr-defined]

            with catalog_path.open("w") as catalog_f:
                catalog_f.write(json_dumps(catalog, indent=2))

            if cache_key := self.catalog_cache_key(plugin_invoker):
                catalog_cache_key_path.write_text(cache_key)
            else:
                with suppress(FileNotFoundError):
                    catalog_cache_key_path.unlink()
        except FileNotFoundError as err:
            msg = "Applying catalog rules failed: catalog file is missing."
            raise PluginExecutionError(msg) from err
        except Exception as err:
            catalog_path.unlink()
            msg = f"Applying catalog rules failed: catalog file is invalid: {err}"
            raise PluginExecutionError(msg) from err

    def catalog_cache_key(self, plugin_invoker):  # noqa: ANN001, ANN201
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

        key_json = json_dumps(key_dict)

        return sha1(key_json.encode()).hexdigest()  # noqa: S324

    @staticmethod
    @lru_cache
    def _warn_missing_stream(stream_id: str) -> None:
        logger.warning(
            "Stream `%s` was not found in the catalog",
            stream_id,
        )

    @staticmethod
    @lru_cache
    def _warn_missing_property(stream_id: str, breadcrumb: tuple[str, ...]) -> None:
        logger.warning(
            "Property `%s` was not found in the schema of stream `%s`",
            ".".join(breadcrumb[1:]),
            stream_id,
        )

    def warn_property_not_found(
        self,
        rules: list[MetadataRule],
        catalog: CatalogDict,
    ) -> None:
        """Validate MetadataRules conforms to discovered Catalog.

        Validate MetadataRules against the tap's discovered Catalog & emit
        warnings for each rule that does not match any property in catalog.

        The method is intentionally written in a defensive manner so as not to
        raise exceptions. e.g.
            * use dict.get rather than []-accessor
            * filter list comprehensions to remove some elements that should
              not be used for validation

        Args:
            rules: List of `MetadataRule`
            catalog: Discovered Source Catalog
        """
        stream_dict = {
            stream.get("tap_stream_id"): stream
            for stream in catalog.get("streams", [])
            if isinstance(stream, dict)  # type: ignore[redundant-expr]
        }

        def is_not_star(x):  # noqa: ANN001, ANN202
            return "*" not in x

        def dict_get(dictionary, key):  # noqa: ANN001, ANN202
            return dictionary.get(key, {})

        for rule in rules:
            if isinstance(rule.tap_stream_id, list) or "*" in rule.tap_stream_id:
                continue
            if not (s := stream_dict.get(rule.tap_stream_id)):
                self._warn_missing_stream(rule.tap_stream_id)
                continue
            path = tuple(takewhile(is_not_star, rule.breadcrumb))
            if len(path) <= 1:
                continue
            if not reduce(dict_get, path, s.get("schema", {})):
                self._warn_missing_property(rule.tap_stream_id, tuple(rule.breadcrumb))
