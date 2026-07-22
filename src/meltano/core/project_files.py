"""Module for handling multiple project .yml files."""

from __future__ import annotations

import contextlib
import os
import tempfile
import typing as t
from copy import copy

import structlog
from ruamel.yaml import CommentedMap, CommentedSeq, YAMLError

from meltano.core import yaml
from meltano.core.utils import deep_merge

if t.TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path

    # A path already proven (by `_validate_include_path`) to be a real file
    # within the project root, or the project's own `meltano.yml`. This is
    # the only place that boundary is enforced; `_write_file` trusts any
    # `InProjectPath` it receives instead of re-checking it.
    InProjectPath = t.NewType("InProjectPath", Path)
    FilesContent: t.TypeAlias = dict[InProjectPath, CommentedMap]

logger = structlog.stdlib.get_logger(__name__)

BLANK_SUBFILE = CommentedMap(
    [
        ("plugins", {}),
        ("schedules", []),
        ("jobs", []),
        ("environments", []),
    ],
)
MULTI_FILE_KEYS = {
    "plugins",
    "schedules",
    "environments",
    "jobs",
}


class InvalidIncludePathError(Exception):
    """Included file path matches a provided pattern but is not a valid config file."""


class ProjectFiles:
    """Interface for working with multiple project yaml files."""

    def __init__(self, root: Path, meltano_file_path: Path) -> None:
        """Instantiate ProjectFiles interface from project root and meltano.yml path.

        Args:
            root: The project root path.
            meltano_file_path: The path to the meltano.yml file.
        """
        self.root = root.resolve()
        # Trusted by construction: this is the project's own entry point,
        # not a path derived from an `include_paths` pattern. Still verified
        # here (rather than only asserted by the `InProjectPath` cast) so a
        # caller that constructs `ProjectFiles` with a `meltano_file_path`
        # outside `root` fails loudly instead of silently trusting it.
        resolved_meltano_file_path = meltano_file_path.resolve()
        try:
            resolved_meltano_file_path.relative_to(self.root)
        except ValueError as err:
            msg = (
                f"meltano_file_path '{meltano_file_path}' is not within "
                f"the project root '{self.root}'."
            )
            raise InvalidIncludePathError(msg) from err
        self._meltano_file_path = t.cast("InProjectPath", resolved_meltano_file_path)
        self._plugin_file_map: dict[tuple[str, ...], InProjectPath] = {}
        self._raw_contents_map: FilesContent = {}
        self._cached_loaded: CommentedMap | None = None

    @property
    def meltano(self) -> CommentedMap:
        """Return the contents of this project's `meltano.yml`.

        Returns:
            The contents of this projects `meltano.yml`.
        """
        return yaml.load(self._meltano_file_path)

    @property
    def include_paths(self) -> list[InProjectPath]:
        """List of paths derived from glob patterns defined in the meltanofile."""
        include_path_patterns = self.meltano.get("include_paths", [])
        return self._resolve_include_paths(include_path_patterns)

    def load(self) -> CommentedMap:
        """Load all project files into a single dict representation.

        Returns:
            A dict representation of all project files.
        """
        prev_raw_contents_map = self._raw_contents_map.copy()
        self._raw_contents_map.clear()
        self._raw_contents_map[self._meltano_file_path] = self.meltano
        included_file_contents = self._load_included_files()

        # If the exact same objects are loaded again, use the cached result:
        k = t.TypeVar("k")

        def id_vals(x: dict[k, t.Any]) -> dict[k, int]:
            return {k: id(v) for k, v in x.items()}

        if self._cached_loaded is None or id_vals(prev_raw_contents_map) != id_vals(
            self._raw_contents_map,
        ):
            self._cached_loaded = (
                deep_merge(self.meltano, *included_file_contents)
                if included_file_contents
                else copy(self.meltano)
            )

        return self._cached_loaded

    def update(self, meltano_config: CommentedMap) -> CommentedMap:
        """Update config by overriding current config with new, changed config.

        Note: `.update()` will write blank entities for those no longer in use
        (i.e. contained config on load, but not on save).

        Args:
            meltano_config: The new config to update with.

        Returns:
            The updated config dictionary.
        """
        file_dicts = self._split_config_dict(meltano_config)
        for file_path, contents in file_dicts.items():
            self._write_file(file_path, contents)

        unused_files = [fl for fl in self.include_paths if fl not in file_dicts]
        for unused_file_path in unused_files:
            self._write_file(unused_file_path, BLANK_SUBFILE)
        return meltano_config

    def _validate_include_path(self, file_path: Path) -> InProjectPath:
        """Validate that a glob match is a real file within the project root.

        This is the single point where paths derived from `include_paths`
        patterns are checked before being trusted for reading or writing;
        `_write_file` relies on every path it receives having passed here.

        Args:
            file_path: The path to validate.

        Returns:
            The same path, now known to be a real file within the project root.

        Raises:
            InvalidIncludePathError: If the included path is not a valid file, or
                if it resolves to a location outside the project root.
        """
        if not file_path.is_file():
            msg = f"Included path '{file_path}' is not a file."
            raise InvalidIncludePathError(msg)
        try:
            file_path.resolve(strict=True).relative_to(self.root)
        except ValueError as err:
            root = self.root
            msg = f"Included path '{file_path}' is outside the project root '{root}'."
            raise InvalidIncludePathError(msg) from err
        return t.cast("InProjectPath", file_path)

    def _resolve_include_paths(
        self,
        include_path_patterns: list[str],
    ) -> list[InProjectPath]:
        """Return a list of paths from a list of glob pattern strings.

        Not including `meltano.yml` (even if it is matched by a pattern).

        Args:
            include_path_patterns: List of glob pattern strings.

        Returns:
            List of paths matching the given glob patterns.

        Raises:
            InvalidIncludePathError: If a path is matched by a pattern but is
                not a valid file.
        """
        include_paths: list[InProjectPath] = []
        for pattern in include_path_patterns:
            for path in self.root.glob(pattern):
                if path == self._meltano_file_path:
                    continue
                try:
                    include_paths.append(self._validate_include_path(path))
                except InvalidIncludePathError as err:
                    logger.critical("Include path '%s' is invalid: \n %s", path, err)
                    raise

        # Deduplicate entries
        return list(dict.fromkeys(include_paths))

    def _add_to_index(self, key: tuple[str, ...], include_path: InProjectPath) -> None:
        """Add a new key:path to the `_plugin_file_map`.

        Args:
            key: The key to add.
            include_path: The path to add.

        Raises:
            Exception: If the plugin file is already in the index.
        """
        if key in self._plugin_file_map:
            key_path_string = ":".join(key)
            existing_key_file_path = self._plugin_file_map.get(key)
            logger.critical(
                "Plugin with path '%s' already added in file %s.",
                key_path_string,
                existing_key_file_path,
            )
            msg = "Duplicate plugin name found"
            raise Exception(msg)  # noqa: TRY002

        self._plugin_file_map[key] = include_path

    def _index_file(
        self,
        include_file_path: InProjectPath,
        include_file_contents: CommentedMap,
    ) -> None:
        """Populate map of plugins/schedules to their respective files.

        This allows us to know exactly which plugin is configured where when we come to
        update plugins.

        Args:
            include_file_path: The path to the included file.
            include_file_contents: The contents of the included file.
        """
        # index plugins
        all_plugins = include_file_contents.get("plugins", {})
        for plugin_type, plugins in all_plugins.items():
            for plugin in plugins:
                plugin_key = ("plugins", plugin_type, plugin["name"])
                self._add_to_index(key=plugin_key, include_path=include_file_path)
        # index schedules
        schedules = include_file_contents.get("schedules", [])
        for schedule in schedules:
            schedule_key = ("schedules", schedule["name"])
            self._add_to_index(key=schedule_key, include_path=include_file_path)
        # index environments
        environments = include_file_contents.get("environments", [])
        for environment in environments:
            environment_key = ("environments", environment["name"])
            self._add_to_index(key=environment_key, include_path=include_file_path)

        jobs = include_file_contents.get("jobs", [])
        for job in jobs:
            job_key = ("jobs", job["name"])
            self._add_to_index(key=job_key, include_path=include_file_path)

    def _load_included_files(self) -> list[CommentedMap]:
        """Read and index included files.

        Returns:
            A list representation of all included files.

        Raises:
            YAMLError: If a file is invalid YAML.
        """
        self._plugin_file_map.clear()
        included_file_contents = []
        for path in self.include_paths:
            try:
                contents: CommentedMap = yaml.load(path)
            except YAMLError as exc:  # noqa: PERF203
                logger.critical("Error while parsing YAML file: %s \n %s", path, exc)
                raise
            else:
                self._raw_contents_map[path] = contents
                # TODO: validate dict schema
                # https://gitlab.com/meltano/meltano/-/issues/3029
                self._index_file(include_file_path=path, include_file_contents=contents)
                included_file_contents.append(contents)
        return included_file_contents

    def _add_mapping_entry(
        self,
        file_dicts: FilesContent,
        file: InProjectPath,
        key: str,
        value: Mapping[str, t.Any],
    ) -> None:
        file_dict = file_dicts.setdefault(file, CommentedMap())
        entries = file_dict.setdefault(key, CommentedSeq())
        if value["name"] not in {scd["name"] for scd in entries}:
            entries.append(value)

    def _add_sequence_entry(
        self,
        file_dicts: FilesContent,
        key: str,
        elements: Iterable[Mapping[str, t.Any]],
    ) -> None:
        for elem in elements:
            file_key = (key, elem["name"])
            file = self._plugin_file_map.get(file_key, self._meltano_file_path)
            self._add_mapping_entry(file_dicts, file, key, elem)

    def _add_plugin(
        self,
        file_dicts: FilesContent,
        file: InProjectPath,
        plugin_type: str,
        plugin: dict,
    ) -> None:
        file_dict = file_dicts.setdefault(file, CommentedMap())
        plugins_dict = file_dict.setdefault("plugins", CommentedMap())
        plugins = plugins_dict.setdefault(plugin_type, CommentedSeq())
        if plugin["name"] not in {plg["name"] for plg in plugins}:
            plugins.append(plugin)

    def _add_plugins(self, file_dicts: FilesContent, all_plugins: dict) -> None:
        for plugin_type, plugins in all_plugins.items():
            plugin_type = str(plugin_type)
            for plugin in plugins:
                key = ("plugins", plugin_type, plugin.get("name"))
                file = self._plugin_file_map.get(key, self._meltano_file_path)
                self._add_plugin(file_dicts, file, plugin_type, plugin)

    def _split_config_dict(self, config: CommentedMap) -> FilesContent:
        file_dicts: FilesContent = {}

        # Fill in the top-level entries
        for key, value in config.items():
            if key == "plugins":
                self._add_plugins(file_dicts, value)
            elif key in MULTI_FILE_KEYS:
                self._add_sequence_entry(file_dicts, key, value)
            else:
                file = self._meltano_file_path
                file_dict = file_dicts.setdefault(file, CommentedMap())
                file_dict[key] = value

        # Make sure that the top-level keys are in the same order as the original files
        sorted_file_dicts = self._restore_file_key_order(file_dicts)

        # Ensure meltano.yml is always present, even if empty
        if self._meltano_file_path not in sorted_file_dicts:
            sorted_file_dicts[self._meltano_file_path] = CommentedMap()

        # Copy comments from the original config to the new config
        config.copy_attributes(sorted_file_dicts[self._meltano_file_path])
        self._copy_yaml_attributes(sorted_file_dicts)
        return sorted_file_dicts

    def _restore_file_key_order(self, file_dicts: FilesContent) -> FilesContent:
        """Restore the order of the keys in the meltano project files.

        Args:
            file_dicts: The dictionary mapping included files to their contents.

        Returns:
            The file contents mapping with order preserved from the original files.
        """
        sorted_file_dicts: FilesContent = {}

        for file, contents in self._raw_contents_map.items():
            if file not in file_dicts:
                continue

            new_keys = [key for key in file_dicts[file] if key not in contents]

            # Restore sorting in project files
            sorted_file_dicts[file] = CommentedMap()
            for key in contents:
                if key in file_dicts[file]:
                    sorted_file_dicts[file][key] = file_dicts[file][key]

            # Add the new keys at the end
            for new_key in new_keys:
                sorted_file_dicts[file][new_key] = file_dicts[file][new_key]

        return sorted_file_dicts

    def _copy_yaml_attributes(self, file_dicts: FilesContent) -> None:
        """Restore comments from top-level YAML entries in project files.

        For every file, use the top-level entries (e.g. "plugins") to copy the comments
        from the original config.

        Args:
            file_dicts: The dictionary mapping included files to their contents.
        """
        for file, file_dict in file_dicts.items():
            original_contents = self._raw_contents_map[file]
            original_contents.copy_attributes(file_dict)

            original_environments = original_contents.get(
                "environments",
                CommentedSeq(),
            )
            environments = file_dict.get("environments", CommentedSeq())
            original_environments.copy_attributes(environments)

            original_jobs = original_contents.get("jobs", CommentedSeq())
            jobs = file_dict.get("jobs", CommentedSeq())
            original_jobs.copy_attributes(jobs)

            original_plugins = original_contents.get("plugins", CommentedMap())
            plugins = file_dict.get("plugins", CommentedMap())
            for plugin_type, plugin_type_plugins in plugins.items():
                original_plugin_type_plugins = original_plugins.get(
                    plugin_type,
                    CommentedSeq(),
                )
                original_plugin_type_plugins.copy_attributes(plugin_type_plugins)

            original_schedules = original_contents.get("schedules", CommentedSeq())
            schedules = file_dict.get("schedules", CommentedSeq())
            original_schedules.copy_attributes(schedules)

    def _write_file(self, file_path: InProjectPath, contents: Mapping) -> None:
        # No containment check here: file_path is only ever an InProjectPath,
        # which is only ever produced by `_validate_include_path` (or is
        # `self._meltano_file_path`, trusted by construction). See the
        # `InProjectPath` definition above for the invariant this relies on.
        dirname = file_path.parent
        fd, tmp_name = tempfile.mkstemp(dir=dirname, suffix=".tmp.yml")
        try:
            with os.fdopen(fd, "w") as tmp_file:
                yaml.dump(contents, tmp_file)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            # Atomically replace the target file
            os.replace(tmp_name, file_path)  # noqa: PTH105
        except Exception:  # pragma: no cover
            # Clean up temp file if write or replace fails
            with contextlib.suppress(OSError):
                os.unlink(tmp_name)  # noqa: PTH108
            raise
