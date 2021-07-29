import os.path
from contextlib import contextmanager
from functools import reduce
from pathlib import Path
from typing import List

import yaml
from meltano.core.meltano_file import MeltanoFile

# TODO:
#   [x] appropriate name for trio: schedules, plugins.extractors, plugins.loaders
#   [x] use trio name to rename plugin_states(), update_plugin(), add_plugins()
#   [ ] add type annotations
#   [x] included
#   [ ] add type hints everywhere
#   [x] lowercase to let caps works in paths
#   [ ] change for loops: for key, value in dict:
#   [x] empty_yaml -> empty_meltano_config
#   [x] plugins -> components && included_keys -> included_components
#   [x] get_include_config_file_plugins -> names
#   [ ] get_included_config_file_plugins -> include docstring sample of output
#   [ ] change comments to docstring
#   [ ] verify where transforms belong
#   [ ] values -> components
#   [ ] get_included_config_file_plugins => extract names from values as list, use that list to replace the list in config_dict
#   [ ] don't loop through func call, assign call to variable, loop through variable
#   [ ] lock load()
#   [ ] enforce relative paths for include-paths
#   [ ] sorted - verify alphabetical or ascii
#   [ ] remove *args in init if no break
#   QUESTIONS
#   [ ] use docstrings with :return:/:params: labels?
#   MAYBE-DO
#   [ ] idea - default scope to current file
#   [ ] include-paths allows files and directories
#   [ ] create deep_set(), use to replace pre-init empty nested dicts
#   ALLOW-LIST
#   1.  write to multiple Meltano files for Plugins.Extractors, Plugins.Loaders, Schedules
#   2.  duplicate plugins/schedules throw build error (this means record is not needed)

ACCEPTED_YAML_EXTENSIONS = [".yml", ".yaml"]
COMPONENT_KEYS = [
    "plugins.extractors",
    "plugins.loaders",
    "schedules",
    "transforms",
]
INCLUDE_PATHS_KEY = "include-paths"


@contextmanager
def load(configfile: Path) -> dict:
    return yaml.safe_load(configfile.open())


def deep_get(dictionary, keys, default=None):
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        keys.split("."),
        dictionary,
    )


def empty_meltano_components():
    """
    Return a nested dictionary based on COMPONENT_KEYS
    """
    return {
        "plugins": {"extractors": [], "loaders": []},
        "schedules": [],
        "transforms": [],
    }


def contains_component(components: List[dict], component: dict) -> bool:
    """
    True if component in components else False
    """
    for c in components:
        if component["name"] == c["name"]:
            return True
    return False


def get_included_directories(main_meltano_config):
    # Process included paths
    included_directories: List[str] = []
    for path_name in main_meltano_config[INCLUDE_PATHS_KEY]:
        # Verify each path is valid
        if os.path.isdir(path_name):  # TODO paths must be relative to project root
            included_directories.append(path_name)
        else:
            pass  # TODO throw an error (include-path {path_name} is not a valid directory)
    return included_directories


def get_included_config_file_paths(included_directories):
    # Get config paths in included directories
    included_config_file_paths: List[Path] = []
    for (
        directory
    ) in (
        included_directories
    ):  # TODO prevent <project_root>/meltano.yml from being extracted here
        # Files are grabbed in UNIX system default: alphabetical/ASCII order
        file_names = sorted(os.listdir(directory))
        for file_name in file_names:
            extension = os.path.splitext(file_name)[-1].lower()
            if extension in ACCEPTED_YAML_EXTENSIONS:
                file_path = Path(directory)
                file_path = file_path.joinpath(file_name)
                included_config_file_paths.append(file_path)
    return included_config_file_paths


def get_included_config_file_data(included_config_file_paths):
    # Store loaded contents of each config file
    included_config_file_data = {}
    for config_file_path in included_config_file_paths:
        included_config_file_data[config_file_path] = load(config_file_path)
    return included_config_file_data


def get_included_config_file_component_names(included_config_file_data):
    # Get names of components in each config file
    included_config_file_component_names = {}
    for config_file_path, config_file_data in included_config_file_data.items():
        included_config_file_component_names[
            config_file_path
        ] = empty_meltano_components()
        for key in COMPONENT_KEYS:
            components = deep_get(config_file_data, key)
            if not components:
                continue
            for component in components:
                included_config = included_config_file_component_names[config_file_path]
                component_names = deep_get(included_config, key)
                try:
                    component_names.append(component["name"])
                except KeyError:
                    pass  # TODO throw error "all plugins must have name - plugin in {configfile}.{key}"
    return included_config_file_component_names


def add_config_plugins(main_config_file, included_config_file_contents):
    # Process keys in included configs
    for config_file in included_config_file_contents:
        config_dict = included_config_file_contents[
            config_file
        ]  # TODO rename config_dict -> ??
        for key in COMPONENT_KEYS:
            values = deep_get(config_dict, key)
            if not values:
                continue
            for value in values:
                if contains_component(deep_get(main_config_file, key), value):
                    pass  # TODO throw an error "{value} already exists" (FB: later "already exists in {where}")
                else:
                    deep_get(main_config_file, key).append(
                        value
                    )  # TODO see if this works
    return main_config_file


def pop_updated_components(updated_data, config_file, included_config_file_plugins):
    """
    Remove updated contents from self that belong in file at config_file_path, return these contents as a dict
    """

    # Initialize empty output_config
    output_config_data = empty_meltano_components()
    config_plugin_data = included_config_file_plugins[config_file]

    # Iterate through INCLUDE_KEYS of config file contents at config_file
    for key in COMPONENT_KEYS:
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
    def __init__(self, *args, **attrs):
        # Include paths are optional
        if attrs.get(INCLUDE_PATHS_KEY):
            self.included_directories = get_included_directories(attrs)
            self.included_config_file_paths = get_included_config_file_paths(
                self.included_directories
            )
            self.all_config_file_paths = self.included_config_file_paths.copy().append(
                Path("meltano.yml")
            )
            self.included_config_file_contents = get_included_config_file_data(
                self.included_config_file_paths
            )
            self.included_config_file_plugins = (
                get_included_config_file_component_names(
                    self.included_config_file_contents
                )
            )
            attrs = add_config_plugins(attrs, self.included_config_file_contents)
        super().__init__(**attrs)

    def pop_config_file_data(self, config_file):
        return pop_updated_components(
            self, config_file, self.included_config_file_plugins
        )
