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
    from collections.abc import Mapping
    from pathlib import Path

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
        self._meltano_file_path = meltano_file_path.resolve()
        self._plugin_file_map: dict[tuple[str, ...], str] = {}
        self._raw_contents_map: dict[str, CommentedMap] = {}
        self._cached_loaded: CommentedMap | None = None

    @property
    def meltano(self) -> CommentedMap:
        """Return the contents of this project's `meltano.yml`.

        Returns:
            The contents of this projects `meltano.yml`.
        """
        return yaml.load(self._meltano_file_path)

    @property
    def include_paths(self) -> list[Path]:
        """Return list of paths derived from glob patterns defined in the meltanofile.

        Returns:
            List of paths derived from glob patterns defined in the meltanofile.
        """
        include_path_patterns = self.meltano.get("include_paths", [])
        return self._resolve_include_paths(include_path_patterns)

    def load(self) -> CommentedMap:
        """Load all project files into a single dict representation.

        Returns:
            A dict representation of all project files.
        """
        prev_raw_contents_map = self._raw_contents_map.copy()
        self._raw_contents_map.clear()
        self._raw_contents_map[str(self._meltano_file_path)] = self.meltano
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

        unused_files = [fl for fl in self.include_paths if str(fl) not in file_dicts]
        for unused_file_path in unused_files:
            self._write_file(unused_file_path, BLANK_SUBFILE)
        return meltano_config

    def _is_valid_include_path(self, file_path: Path) -> None:
        """Determine if given path is a valid `include_paths` file.

        Args:
            file_path: The path to check.

        Raises:
            InvalidIncludePathError: If the included path is not a valid file.
        """
        if not (file_path.is_file() and file_path.exists()):
            raise InvalidIncludePathError(f"Included path '{file_path}' not found.")  # noqa: EM102, TRY003

    def _resolve_include_paths(self, include_path_patterns: list[str]) -> list[Path]:
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
        include_paths = []
        for pattern in include_path_patterns:
            for path in self.root.glob(pattern):
                try:
                    self._is_valid_include_path(path)
                except InvalidIncludePathError as err:
                    logger.critical(f"Include path '{path}' is invalid: \n {err}")  # noqa: G004
                    raise err  # noqa: TRY201
                include_paths.append(path)
            if self._meltano_file_path in include_paths:
                include_paths.remove(self._meltano_file_path)

        # Deduplicate entries
        return list(dict.fromkeys(include_paths))

    def _add_to_index(self, key: tuple[str, ...], include_path: Path) -> None:
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
                f'Plugin with path "{key_path_string}" already added in '  # noqa: G004
                f"file {existing_key_file_path}.",
            )
            raise Exception("Duplicate plugin name found.")  # noqa: EM101, TRY002, TRY003

        self._plugin_file_map[key] = str(include_path)

    def _index_file(
        self,
        include_file_path: Path,
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
                logger.critical(f"Error while parsing YAML file: {path} \n {exc}")  # noqa: G004
                raise exc  # noqa: TRY201
            else:
                self._raw_contents_map[str(path)] = contents
                # TODO: validate dict schema
                # https://gitlab.com/meltano/meltano/-/issues/3029
                self._index_file(include_file_path=path, include_file_contents=contents)
                included_file_contents.append(contents)
        return included_file_contents

    def _add_mapping_entry(self, file_dicts, file, key, value) -> None:  # noqa: ANN001
        file_dict = file_dicts.setdefault(file, CommentedMap())
        entries = file_dict.setdefault(key, CommentedSeq())
        if value["name"] not in {scd["name"] for scd in entries}:
            entries.append(value)

    def _add_sequence_entry(self, file_dicts, key, elements) -> None:  # noqa: ANN001
        for elem in elements:
            file_key = (key, elem["name"])
            file = self._plugin_file_map.get(file_key, str(self._meltano_file_path))
            self._add_mapping_entry(file_dicts, file, key, elem)

    def _add_plugin(self, file_dicts, file, plugin_type, plugin) -> None:  # noqa: ANN001
        file_dict = file_dicts.setdefault(file, CommentedMap())
        plugins_dict = file_dict.setdefault("plugins", CommentedMap())
        plugins = plugins_dict.setdefault(plugin_type, CommentedSeq())
        if plugin["name"] not in {plg["name"] for plg in plugins}:
            plugins.append(plugin)

    def _add_plugins(self, file_dicts, all_plugins) -> None:  # noqa: ANN001
        for plugin_type, plugins in all_plugins.items():
            plugin_type = str(plugin_type)
            for plugin in plugins:
                key = ("plugins", plugin_type, plugin.get("name"))
                file = self._plugin_file_map.get(key, str(self._meltano_file_path))
                self._add_plugin(file_dicts, file, plugin_type, plugin)

    def _split_config_dict(self, config: CommentedMap):  # noqa: ANN202
        file_dicts: dict[str, CommentedMap] = {}

        # Fill in the top-level entries
        for key, value in config.items():
            if key == "plugins":
                self._add_plugins(file_dicts, value)
            elif key in MULTI_FILE_KEYS:
                self._add_sequence_entry(file_dicts, key, value)
            else:
                file = str(self._meltano_file_path)
                file_dict = file_dicts.setdefault(file, CommentedMap())
                file_dict[key] = value

        # Make sure that the top-level keys are in the same order as the original files
        sorted_file_dicts = self._restore_file_key_order(file_dicts)

        # Ensure meltano.yml is always present, even if empty
        meltano_file_path = str(self._meltano_file_path)
        if meltano_file_path not in sorted_file_dicts:
            sorted_file_dicts[meltano_file_path] = CommentedMap()

        # Copy comments from the original config to the new config
        config.copy_attributes(sorted_file_dicts[meltano_file_path])
        self._copy_yaml_attributes(sorted_file_dicts)
        return sorted_file_dicts

    def _restore_file_key_order(self, file_dicts: dict[str, CommentedMap]):  # noqa: ANN202
        """Restore the order of the keys in the meltano project files.

        Args:
            file_dicts: The dictionary mapping included files to their contents.

        Returns:
            The file contents mapping with order preserved from the original files.∫
        """
        sorted_file_dicts: dict[str, CommentedMap] = {}

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

    def _copy_yaml_attributes(
        self,
        file_dicts: dict[str, CommentedMap],
    ) -> None:
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

    def _write_file(self, file_path: str | os.PathLike[str], contents: Mapping) -> None:
        dirname = os.path.dirname(file_path)  # noqa: PTH120
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
