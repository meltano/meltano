import copy
import glob
import logging
from pathlib import Path
from typing import List

import yaml
from atomicwrites import atomic_write

logger = logging.getLogger(__name__)

BLANK_SUBFILE = {"plugins": {}, "schedules": []}


def deep_merge(parent: dict, children: List[dict]) -> dict:
    """Deep merge a list of child dicts with a given parent."""
    for child in children:
        for key, value in child.items():
            if isinstance(value, dict):
                # get node or create one
                node = parent.setdefault(key, {})
                parent[key] = deep_merge(node, [value])
            elif isinstance(value, list):
                parent[key].extend(value)
            else:
                parent[key] = value
    return parent


class ProjectFiles:
    """Interface for working with multiple project yaml files."""

    def __init__(self, root: Path, meltano_file_path: Path):
        self.root = root.resolve()
        self._meltano = None
        self._meltano_file_path = meltano_file_path.resolve()
        self._plugin_file_map = {}

    def _is_valid_include_path(self, file_path: Path) -> bool:
        """Determine if given path is a valid `include_paths` file."""
        # Verify path is a file
        if not (file_path.is_file() and file_path.exists()):
            logger.critical(f"Included path '{file_path}' not found.")
            raise Exception("Invalid Included Path")
        # checks passed
        return True

    def _resolve_include_paths(self, include_path_patterns: List[str]) -> List[Path]:
        """Return a list of paths from a list of glob pattern strings."""
        include_paths = []
        for pattern in include_path_patterns:
            for path_name in glob.iglob(pattern):
                path = Path(path_name)
                path = path.resolve()
                if self._is_valid_include_path(path):
                    include_paths.append(path)
            # never include meltano.yml
            if self._meltano_file_path in include_paths:
                include_paths.remove(self._meltano_file_path)
        return include_paths

    def _add_to_index(self, key: tuple, include_path: Path) -> None:
        """Add a new key:path to the `_plugin_file_map`."""
        if key in self._plugin_file_map:
            key_path_string = ":".join(key)
            existing_key_file_path = self._plugin_file_map.get(key)
            logger.critical(
                f'Plugin with path "{key_path_string}" already added in file {existing_key_file_path}.'
            )
            raise Exception("Duplicate plugin name found.")
        else:
            self._plugin_file_map[key] = str(include_path)

    def _index_file(self, include_file_path: Path, include_file_contents: dict) -> None:
        """Populate map of plugins/schedules to their respective files.

        This allows us to know exactly which plugin is configured where when we come to update plugins.
        """
        # index plugins
        plugins = include_file_contents.get("plugins", {})
        for plugin_type, plugins in plugins.items():
            for plugin in plugins:
                plugin_key = ("plugins", plugin_type, plugin["name"])
                self._add_to_index(key=plugin_key, include_path=include_file_path)
        # index schedules
        schedules = include_file_contents.get("schedules", {})
        for schedule in schedules:
            schedule_key = ("schedules", schedule["name"])
            self._add_to_index(key=schedule_key, include_path=include_file_path)

    def _load_included_files(self):
        """Read and index included files."""
        self._plugin_file_map = {}
        included_file_contents = []
        for path in self.include_paths:
            try:
                with path.open() as file:
                    contents = yaml.safe_load(file)
                    # TODO: validate dict schema
                    self._index_file(
                        include_file_path=path, include_file_contents=contents)
                    included_file_contents.append(contents)
            except yaml.YAMLError as exc:
                logger.critical(f"Error while parsing YAML file: {path} \n {exc}")
                raise exc
        return included_file_contents

    @property
    def meltano(self):
        if self._meltano is None:
            with open(self._meltano_file_path) as f:
                self._meltano = yaml.safe_load(f)
        return self._meltano

    @property
    def include_paths(self) -> List[Path]:
        """A list of paths derived from glob patterns defined in the meltanofile."""
        include_path_patterns = self.meltano.get("include_paths", [])
        include_paths = self._resolve_include_paths(include_path_patterns)
        return include_paths

    def load(self) -> dict:
        """Load all project files into a single dict representation."""
        # load individual file dicts
        included_file_contents = self._load_included_files()
        # combine into a single dict
        meltano_config = deep_merge(copy.deepcopy(self.meltano), included_file_contents)
        # TODO: validate schema?
        return meltano_config

    def _split_config_dict(self, config:dict):
        file_dicts = {}
        for key, value in config.items():
            if key == "plugins":
                for plugin_type, plugins in value.items():
                    plugin_type = str(plugin_type)
                    for plugin in plugins:
                        key = ("plugins", plugin_type, plugin.get("name"))
                        file = self._plugin_file_map.get(key, str(self._meltano_file_path))
                        if not file in file_dicts:
                            file_dicts[file] = {}
                        if not "plugins" in file_dicts[file]:
                            file_dicts[file]["plugins"] = {}
                        if not plugin_type in file_dicts[file]["plugins"]:
                            file_dicts[file]["plugins"][plugin_type] = []
                        if not plugin["name"] in [p["name"] for p in file_dicts[file]["plugins"][plugin_type]]:
                            file_dicts[file]["plugins"][plugin_type].append(plugin)
            elif key == "schedules":
                for schedule in value:
                    key = ("schedules", schedule["name"])
                    file = self._plugin_file_map.get(key, str(self._meltano_file_path))
                    if not file in file_dicts:
                        file_dicts[file] = {}
                    if not "schedules" in file_dicts[file]:
                        file_dicts[file]["schedules"] = []
                    if not schedule["name"] in [s["name"] for s in file_dicts[file]["schedules"]]:
                        file_dicts[file]["schedules"].append(schedule)
            else:
                file = str(self._meltano_file_path)
                if not file in file_dicts:
                    file_dicts[file] = {}
                file_dicts[file][key] = value
        return file_dicts

    def update(self, meltano_config: dict):
        """Update config by overriding current config with new, changed config."""
        # construct individual dicts per file
        file_dicts = self._split_config_dict(meltano_config)
        for file_path, contents in file_dicts.items():
            with atomic_write(file_path, overwrite=True) as f:
                yaml.dump(contents, f, default_flow_style=False, sort_keys=False)
        # write blank entities for those no longer in use (i.e. contained config on load, but not on save)
        unused_files = [f for f in self.include_paths if str(f) not in file_dicts]
        for file_path in unused_files:
            with atomic_write(file_path, overwrite=True) as f:
                yaml.dump(BLANK_SUBFILE, f, default_flow_style=False, sort_keys=False)
        # reset cache
        self._meltano = None
        return meltano_config
