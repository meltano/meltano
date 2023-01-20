"""Compile a Meltano manifest."""

from __future__ import annotations

import io
import json
import re
import sys
from collections import defaultdict
from collections.abc import Iterable
from contextlib import redirect_stdout
from functools import reduce
from operator import getitem
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Mapping, MutableMapping, cast

import structlog
import yaml

# TODO: Remove the `type: ignore` once
# https://github.com/python-jsonschema/check-jsonschema/pull/228 has been merged
from check_jsonschema.cli import ParseResult as check_jsonschema_options  # type: ignore
from check_jsonschema.cli import build_checker as build_jsonschema_checker
from typing_extensions import TypeAlias

from meltano import __file__ as package_root_path
from meltano.core.environment import Environment
from meltano.core.manifest.jsonschema import meltano_config_env_locations
from meltano.core.plugin.base import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_lock_service import PluginLock
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import (
    EnvVarMissingBehavior,
    MergeStrategy,
    deep_merge,
    default_deep_merge_strategies,
    expand_env_vars,
    get_no_color_flag,
)

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

# NOTE: We do not use `Project(...).meltano.canonical` for 3 reasons:
# - It will make it difficult to refactor the rest of the Meltano core to be
#   based on the manifest if the manifest itself depends on the rest of Meltano
#   core.
# - The canonical representation has changes to the file that we don't want,
#   e.g. turning strings into datetime objects.
# - The canonical representation uses Ruamel, which is known to have poor
#   performance in some cases. No need to eat that cost here, since we don't
#   care about comment preservation in the manifest.

logger = structlog.getLogger(__name__)

JSON_LOCATION_PATTERN = re.compile(r"\.|(\[\])")
MANIFEST_SCHEMA_PATH = Path(package_root_path).parent / "schema" / "meltano.schema.json"

Trie: TypeAlias = Dict[str, "Trie"]  # type: ignore
PluginsByType: TypeAlias = Mapping[str, List[Mapping[str, Any]]]
PluginsByNameByType: TypeAlias = Mapping[str, Mapping[str, Mapping[str, Any]]]


# FIXME: We may want to switch over to ruamel for this
class YamlLimitedSafeLoader(type):
    """Meta YAML loader that skips the resolution of the specified YAML tags."""

    def __new__(
        cls, name, bases, namespace, do_not_resolve: Iterable[str]
    ) -> YamlLimitedSafeLoader:
        """Generate a new instance of this metaclass.

        Args:
            name: The name of the new class.
            bases: The base classes of the new class. The first base class will
                always be `yaml.SafeLoader`. These will come afterwards.
            namespace: The namespace of the new class.
            do_not_resolve: The YAML tags whose resolution should be skipped
                during parsing. They will be left as raw strings.

        Returns:
            The new class object, which is a subclass of `yaml.SafeLoader`
            which skips the resolution of the specified YAML tags.
        """
        do_not_resolve = set(do_not_resolve)
        implicit_resolvers = {
            key: [(tag, regex) for tag, regex in mappings if tag not in do_not_resolve]
            for key, mappings in yaml.SafeLoader.yaml_implicit_resolvers.items()
        }
        return super().__new__(
            cls,
            name,
            (yaml.SafeLoader, *bases),
            {**namespace, "yaml_implicit_resolvers": implicit_resolvers},
        )


class YamlNoTimestampSafeLoader(
    metaclass=YamlLimitedSafeLoader, do_not_resolve={"tag:yaml.org,2002:timestamp"}
):
    """A safe YAML loader that leaves timestamps as strings."""


def env_aware_merge_mappings(
    data: MutableMapping[str, Any],
    key: str,
    value: Any,
    _: tuple[Any, ...] | None = None,
) -> None:
    """Merge behavior for `deep_merge` that expands env vars when the key is "env".

    Args:
        data: The dictionary being merged into.
        key: The key for the dictionary being merged into.
        value: The value being merged into the dictionary.
        _: Merge strategies - unused argument.

    Returns:
        `NotImplemented` if the key is not "env"; `None` otherwise.
    """
    if key != "env":
        return NotImplemented  # type: ignore
    data[key] = {
        **expand_env_vars(data[key], value, if_missing=EnvVarMissingBehavior.ignore),
        **expand_env_vars(value, data[key], if_missing=EnvVarMissingBehavior.ignore),
    }


class Manifest:
    """A complete unambiguous static representation of a Meltano project."""

    def __init__(self, project: Project, environment: Environment | None) -> None:
        """Initialize the manifest.

        This class does not write a manifest file. It merely generates the data
        that would go into one.

        The contents of the manifest can be access using the `data` attribute.
        This data is generated when it is first accessed. After that, a cached
        result is used.

        Args:
            project: The Meltano project which this manifest describes.
            environment: The Meltano environment which this manifest describes.
                If `None`, then all data under the `environments` key in the
                project files will be ignored by this manifest.
        """
        self.project = project
        self._meltano_file = self.project.meltanofile.read_text()
        self.environment = environment
        self.project_settings_service = ProjectSettingsService(project)
        self.project_plugins_service = ProjectPluginsService(project)
        with open(MANIFEST_SCHEMA_PATH) as manifest_schema_file:
            self.manifest_schema = json.load(manifest_schema_file)

    @staticmethod
    def _validate_against_manifest_schema(
        instance_name: str,
        intance_data: dict[str, Any],
    ) -> None:
        with NamedTemporaryFile(suffix=".json") as schema_instance_file:
            schema_instance_file.write(json.dumps(intance_data).encode())
            schema_instance_file.flush()
            with io.StringIO() as buf, redirect_stdout(buf):
                opts = check_jsonschema_options()
                opts.color = not get_no_color_flag()
                opts.set_schema(
                    schemafile=str(MANIFEST_SCHEMA_PATH),
                    builtin_schema=None,
                    check_metaschema=None,
                )
                opts.instancefiles = (schema_instance_file.name,)
                jsonschema_checker = build_jsonschema_checker(opts)
                results = jsonschema_checker._build_result()  # noqa: WPS437
                if results.validation_errors:
                    results.validation_errors = {
                        "meltano.yml": v for v in results.validation_errors.values()
                    }
                jsonschema_checker._reporter.report_result(results)  # noqa: WPS437
                buf.seek(0)
                jsonschema_checker_message = buf.read().strip()
            logger.warn(
                f"Failed to validate {instance_name} against Meltano manifest "
                f"schema ({MANIFEST_SCHEMA_PATH}):\n{jsonschema_checker_message}"
            )

    @cached_property
    def _project_files(self) -> dict[str, Any]:
        project_files = deep_merge(
            yaml.load(  # noqa: S506
                self._meltano_file,
                YamlNoTimestampSafeLoader,
            ),
            *(
                yaml.load(x.read_text(), YamlNoTimestampSafeLoader)  # noqa: S506
                for x in self.project.project_files.include_paths
            ),
        )
        self._validate_against_manifest_schema("project files", project_files)
        return project_files

    def _merge_plugin_lockfiles(
        self, plugins: dict[PluginType, list[ProjectPlugin]], manifest: dict[str, Any]
    ) -> None:
        locked_plugins = cast(
            dict[str, list[Mapping[str, Any]]],
            {
                plugin_type.value: [
                    PluginLock(self.project, plugin).load(create=True, loader=json.load)
                    for plugin in plugins
                ]
                for (plugin_type, plugins) in plugins.items()
            },
        )

        # Merge the locked plugins with the root-level plugins from `meltano.yml`:
        manifest["plugins"] = deep_merge(  # noqa: WPS204
            _plugins_by_name_by_type(manifest["plugins"]),
            _plugins_by_name_by_type(locked_plugins),
        )

    def _merge_env_vars(
        self, plugins: dict[PluginType, list[ProjectPlugin]], manifest: dict[str, Any]
    ) -> None:
        # Merge env vars derived from project settings:
        env_aware_merge_mappings(
            manifest,
            "env",
            self.project_settings_service.as_env(),
        )

        # Ensure the environment-level plugin config is mergable:
        environment = next(iter(manifest["environments"]))
        environment_plugins = environment.setdefault("config", {}).setdefault(
            "plugins", {}
        )
        environment["config"]["plugins"] = _plugins_by_name_by_type(environment_plugins)

        merge_strategies = (
            MergeStrategy(dict, env_aware_merge_mappings),
            *default_deep_merge_strategies,
        )

        # Env precedence hierarchy:
        # - environment plugin env  # highest
        # - root plugin env
        # - environment env
        # - root env                # Manifest only cares about this level and higher
        # - schedule env
        # - job env
        # - .env file
        # - terminal env            # lowest

        # NOTE: The schedule, job, .env, and terminal env are all injected into
        #       `os.environ`. Meltano should only ever read the schedule and
        #       job env fields within `meltano.yml` or a manifest file in order
        #       to inject it into `os.environ`.

        environment = next(iter(manifest["environments"]))

        # Merge 'environment level plugin env' into 'root level plugin env':
        manifest["plugins"] = deep_merge(
            manifest["plugins"],
            environment.get("config", {}).get("plugins", {}),
            strategies=merge_strategies,
        )

        # Merge env vars derived from plugin settings:
        for plugin_type in plugins:
            for plugin in plugins[plugin_type]:
                env_aware_merge_mappings(
                    manifest["plugins"][plugin_type][plugin.name],
                    "env",
                    PluginSettingsService(
                        project=self.project,
                        plugin=plugin,
                        plugins_service=self.project_plugins_service,
                    ).as_env(),
                )

        # Merge 'environment level env' into 'root level env':
        env_aware_merge_mappings(manifest, "env", environment["env"])

    @cached_property
    def data(self) -> dict[str, Any]:
        """Generate the manifest data.

        The data is generated when this property is first accessed, then cached
        in the instance for fast subsequent accesses. This cached result is
        mutable, because Python lacks a `frozendict` class in its standard
        library. Please do not alter it in-place.

        Returns:
            The manifest data.
        """
        # The manifest begins as the project files, i.e. `meltano.yml` + included files
        manifest = self._project_files

        # Remove all environments other than the one this manifest is for:
        if self.environment is None:
            # We use a mock environment here because the rest of the code
            # expects there to be exactly one environment. It is omitted from
            # the final output, and during processing it only affects things if
            # it has content, which this mock does not.
            manifest["environments"] = [{"name": "mock"}]  # noqa: WPS204
        else:
            manifest["environments"] = [
                x
                for x in manifest["environments"]
                if x["name"] == self.environment.name
            ]

        apply_scaffold(manifest, meltano_config_env_locations(self.manifest_schema))

        plugins = self.project_plugins_service.plugins_by_type()
        # NOTE: `self._merge_plugin_lockfiles` restructures the plugins into a
        #       map from plugin types to maps of plugin IDs to their values.
        #       This structure is easier to work with, but is reset to the
        #       proper structure below, before the manifest is returned.
        self._merge_plugin_lockfiles(plugins, manifest)

        self._merge_env_vars(plugins, manifest)

        # Make each plugin type a list again:
        manifest["plugins"] = {
            plugin_type: list(plugins.values())
            for plugin_type, plugins in manifest["plugins"].items()
        }

        # Everything from the selected environment has been merged into the
        # higher levels, so it can be deleted to avoid any ambiguity about
        # which fields within the manifest should be read.
        del manifest["environments"]

        self._validate_against_manifest_schema("newly compiled manifest", manifest)

        return manifest


def _plugins_by_name_by_type(
    plugins_by_type: PluginsByType,
) -> PluginsByNameByType:
    return {
        plugin_type: {plugin["name"]: plugin for plugin in plugins}
        for plugin_type, plugins in plugins_by_type.items()
    }


def _locations_trie(paths: Iterable[Iterable[str]]) -> Trie:
    def defaultdict_defaultdict():
        return defaultdict(defaultdict_defaultdict)

    root = defaultdict_defaultdict()
    for path in paths:
        reduce(getitem, path, root)
    return json.loads(json.dumps(root))


def _apply_scaffold(trie: Trie, manifest_component: dict[str, Any] | list[Any]) -> None:
    for key, sub_trie in trie.items():
        if key == "[]":
            if not isinstance(manifest_component, list):
                raise TypeError(
                    "Expected list during manifest scaffolding, "
                    f"got {type(manifest_component)}"
                )
            for element in manifest_component:
                _apply_scaffold(sub_trie, element)
        elif isinstance(manifest_component, dict):
            _apply_scaffold(
                sub_trie,
                manifest_component.setdefault(key, [] if "[]" in sub_trie else {}),
            )
        else:
            raise TypeError(
                "Expected dict during manifest scaffolding, "
                f"got {type(manifest_component)}"
            )


def apply_scaffold(manifest: dict[str, Any], locations: Iterable[str]) -> None:
    """Update the provided manifest dict with dicts/lists at the provided locations.

    Args:
        manifest: The manifest dictionary to update in-place.
        locations: The locations (as jq filters) which will be added to the the
            manifest as necessary.
    """
    _apply_scaffold(
        _locations_trie(
            (x for x in JSON_LOCATION_PATTERN.split(location) if x)
            for location in locations
        ),
        manifest,
    )
