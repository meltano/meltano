import os.path
from contextlib import contextmanager
from functools import reduce
from pathlib import Path
from typing import List, Optional

import yaml
from meltano.core.meltano_file import MeltanoFile

# TODO:
#   [ ] appropriate name for trio: schedules, plugins.extractors, plugins.loaders
#   [ ] use trio name to rename plugin_states(), update_plugin(), add_plugins()
#   [ ] move same_name() and contains_plugin() to multiple_config.py if they can be used there
#   ALLOW-LIST
#   1.  write to multiple Meltano files for Plugins.Extractors, Plugins.Loaders, Schedules
#   2.  duplicate plugins/schedules throw build error (this means record is not needed)


def same_name(plugin1: dict, plugin2: dict) -> bool:
    return plugin1["name"] == plugin2["name"]


def contains_plugin(plugins: List[dict], plugin: dict) -> Optional[dict]:
    """
    p from plugins if plugin in plugins else None
    """
    for p in plugins:
        if same_name(plugin, p):
            return p
    return None


# def load(configfile) -> dict:  # TODO takes Path or str, doesn't hurt to reinit Path
#     return yaml.safe_load(Path(configfile).open())


@contextmanager
def load(configfile: Path) -> dict:  # TODO need to see about locking
    return yaml.safe_load(configfile.open())  # TODO do this with a contextmanager


def deep_get(dictionary, keys, default=None):
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        keys.split("."),
        dictionary,
    )


def empty_yaml():
    return {
        "plugins": {"extractors": [], "loaders": []},
        "schedules": [],
        "transforms": [],
    }


INCLUDE_PATHS_KEY = "include-paths"
INCLUDE_KEYS = [
    "plugins.extractors",
    "plugins.loaders",
    "schedules",
    "transforms",
]  # TODO better name for include_keys
ACCEPTED_YAML_EXTENSIONS = [".yml", ".yaml"]  # TODO allow caps?


def get_included_directories(meltano_config):
    # Process included paths
    included_directories: List[str] = []  # TODO FB: type hint everywhere or nowhere
    for path_name in meltano_config[INCLUDE_PATHS_KEY]:
        # verify each path is valid TODO (FB: in the end, ADD files - it makes the product better) are only directories allowed, or are paths allowed too?
        if os.path.isdir(
            path_name
        ):  # This accepts paths relative to root, and absolute paths TODO (FB: enforce relative paths) one or the other?
            included_directories.append(path_name)
        else:
            pass  # TODO FB: throw an error (include-path {path_name} is not a valid directory)
    return included_directories


def get_included_config_file_paths(included_directories):
    # Extract configs from included paths
    included_config_file_paths: List[str] = []
    for (
        directory
    ) in (
        included_directories
    ):  # TODO prevent <project_root>/meltano.yml from being extracted here
        file_names = sorted(os.listdir(directory))
        for file_name in file_names:
            extension = os.path.splitext(file_name)[-1]
            if extension in ACCEPTED_YAML_EXTENSIONS:
                file_path = Path(directory).joinpath(
                    file_name
                )  # use Path to ensure string is correct  # TODO (FB: excessive) is this expensive/excessive?
                included_config_file_paths.append(file_path)
    return included_config_file_paths


def get_included_config_file_contents(included_config_file_paths):
    # Save loaded contents of each config file
    included_config_file_contents = {}
    for config_file in included_config_file_paths:
        included_config_file_contents[config_file] = load(config_file)
    return included_config_file_contents


def get_included_config_file_plugins(included_config_file_contents):
    # Get record of plugins in each file
    inlcuded_config_file_plugins = (
        {}
    )  # mirrors structure of meltano config, but with plugin names only
    for config_file in included_config_file_contents:
        inlcuded_config_file_plugins[config_file] = empty_yaml()
        config_dict = included_config_file_contents[config_file]
        for key in INCLUDE_KEYS:
            values = deep_get(config_dict, key)
            if not values:
                continue
            for value in values:
                included_config = inlcuded_config_file_plugins[config_file]
                try:
                    deep_get(included_config, key).append(value["name"])
                except KeyError:
                    pass  # TODO throw error "all plugins must have name - plugin in {configfile}.{key}"
    return inlcuded_config_file_plugins


def add_config_plugins(main_config_file, included_config_file_contents):
    # Process keys in included configs
    for config_file in included_config_file_contents:
        config_dict = included_config_file_contents[
            config_file
        ]  # TODO rename config_dict -> ??
        for key in INCLUDE_KEYS:
            values = deep_get(config_dict, key)
            if not values:
                continue
            for value in values:
                if contains_plugin(deep_get(main_config_file, key), value):
                    pass  # TODO throw an error "{value} already exists" (FB: later "already exists in {where}")
                else:
                    deep_get(main_config_file, key).append(
                        value
                    )  # TODO see if this works


def get_updated_plugin(updated_data, config_file, included_config_file_plugins):
    """
    Remove updated contents from self that belong in file at config_file_path, return these contents as a dict
    """

    # Initialize empty output_config
    output_config_data = empty_yaml()
    config_plugin_data = included_config_file_plugins[config_file]

    # Iterate through INCLUDE_KEYS of config file contents at config_file
    for key in INCLUDE_KEYS:
        for included_plugin_names in deep_get(config_plugin_data, key):
            if (
                not included_plugin_names
            ):  # config_file does not have plugins of type 'key'
                continue
            for name in included_plugin_names:

                # Search self for the same plugin type and name, retrieve that index
                updated_plugins = deep_get(updated_data, key)
                if (
                    not updated_plugins
                ):  # updated_data does not have plugins of type 'key'
                    continue
                idx = [
                    idx
                    for idx, plugin in enumerate(updated_plugins)
                    if plugin.get("name") == name
                ]

                # Remove contents of self at index
                updated_plugin = updated_plugins.pop(idx)

                #  Write the contents of self at index to output config at 'key'
                deep_get(output_config_data, key).append(updated_plugin)

    # (optional) remove empty keys in output_config

    # return output_config
    return output_config_data


class MultipleMeltanoFile(MeltanoFile):
    def __init__(
        self, *args, **attrs
    ):  # TODO check it out (bet args is empty, bet attrs is a dict)
        # TODO 'if attrs.get(INCLUDE_PATHS_KEY):' is explicit but it complicates project.meltano_update... opinion?
        self.included_directories = get_included_directories(attrs)
        self.included_config_file_paths = get_included_config_file_paths(
            self.included_directories
        )
        self.included_config_file_contents = get_included_config_file_contents(
            self.included_config_file_paths
        )
        self.included_config_file_plugins = get_included_config_file_plugins(
            self.included_config_file_contents
        )
        add_config_plugins(attrs, self.included_config_file_contents)
        super().__init__(**attrs)

    def get_update(self, config_file):
        return get_updated_plugin(self, config_file, self.included_config_file_plugins)
