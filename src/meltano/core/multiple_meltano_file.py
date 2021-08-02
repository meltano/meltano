import logging
import os.path
from functools import reduce
from pathlib import Path
from typing import Dict, List

import yaml
from meltano.core.meltano_file import MeltanoFile

# TODO:
#   [x] appropriate name for trio: schedules, plugins.extractors, plugins.loaders
#   [x] use trio name to rename plugin_states(), update_plugin(), add_plugins()
#   [x] included
#   [ ] add type hints everywhere
#   [x] lowercase to let caps works in paths
#   [x] change for loops: for key, value in dict:
#   [x] empty_yaml -> empty_meltano_config
#   [x] plugins -> components && included_keys -> included_components
#   [x] get_include_config_file_plugins -> names
#   [ ] get_included_config_file_plugins -> include docstring sample of output
#   [ ] move comments to docstrings
#   [ ] update all docstrings
#   [ ] verify where 'transforms' component belongs
#   [x] values -> components
#   [x] get_included_config_file_plugins => extract names from values as list, use that list to replace the list in config_dict
#   [x] don't loop through func call, assign call to variable, loop through variable
#   [ ] lock load()
#   [ ] enforce relative paths for include-paths
#   [ ] sorted - verify alphabetical or ascii
#   [ ] remove *args in init if no break
#   [ ] git rm test_multiple_config.py
#   [ ] verify + replciate how Meltano throws errors
#   QUESTIONS
#   [ ] use docstrings with :return:/:params: labels?
#   [ ] is pop_updated_components clear?
#   [ ] should the check in pop_config_file_data() got to project.py?
#   [ ] idea for naming empty_meltano_components(), and expected_empty_config (in test_MMF)
#   [ ] what to test for in load()
#   [ ] keep test_empty_meltano_components()?
#   [ ] project fxtr cleans up, but only aft entire (class? test suite?) - is there a better way to manually clean than what i have?
#   [ ] don't add to all to attrs, just necessary - better design? (list repercussions elsewhere) (try it out first)
#   MAYBE-DO
#   [ ] idea - default scope to current file
#   [ ] include-paths allows files and directories
#   [ ] create deep_set(), use to replace pre-init empty nested dicts
#   ALLOW-LIST
#   1.  write to multiple Meltano files for Plugins.Extractors, Plugins.Loaders, Schedules
#   2.  duplicate plugins/schedules throw build error (this means record is not needed)

logger = logging.getLogger(__name__)


ACCEPTED_YAML_EXTENSIONS = [".yml", ".yaml"]
COMPONENT_KEYS = [
    "plugins.extractors",
    "plugins.loaders",
    "schedules",
    "transforms",
]
INCLUDE_PATHS_KEY = "include_paths"
MELTANO_FILE_PATH_NAME = "meltano.yml"
EXTRA_KEYS = [
    "included_directories",
    "included_config_file_path_names",
    "included_config_file_contents",
    "included_config_file_component_names",
]


def load(configfile_path_name: str) -> dict:
    configfile = Path(configfile_path_name)
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
    True if component in components else False.
    Assumes all components have names.
    """
    for c in components:
        if component["name"] == c["name"]:
            return True
    return False


def get_included_directories(main_meltano_config):
    # Process included paths
    included_directories: List[str] = []
    try:
        for path_name in main_meltano_config[INCLUDE_PATHS_KEY]:
            # Verify each path is valid
            if os.path.isdir(path_name):  # TODO paths must be relative to project root
                included_directories.append(path_name)
            else:
                logger.critical(
                    f"Included path '{path_name}' is not a valid directory."
                )
                raise Exception("Invalid Included Path")
    except KeyError:
        pass  # Include paths are optional
    return included_directories


def get_included_config_file_path_names(included_directories):
    # Get config paths in included directories
    included_config_file_path_names: List[str] = []
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
                file_path_name = str(file_path.joinpath(file_name))
                included_config_file_path_names.append(file_path_name)
    return included_config_file_path_names


def get_included_config_file_components(included_config_file_path_names):
    # Store loaded contents of each config file
    included_config_file_components: Dict[Path, dict] = dict()
    for config_file_path_name in included_config_file_path_names:
        config_file_components = load(config_file_path_name)
        included_config_file_components[config_file_path_name] = config_file_components
    return included_config_file_components


def get_included_config_file_component_names(included_config_file_components):
    # Get names of components in each config file
    included_config_file_component_names = {}
    for (
        config_file_path_name,
        config_file_components,
    ) in included_config_file_components.items():
        included_config_file_component_names[
            config_file_path_name
        ] = empty_meltano_components()
        for key in COMPONENT_KEYS:
            components = deep_get(config_file_components, key)
            if not components:
                continue
            try:
                component_names = [component["name"] for component in components]
            except KeyError:
                logger.critical(
                    f"Component of type {key} in {config_file_path_name} does not have name."
                )
                raise Exception("Unnamed Component")
            included_config = included_config_file_component_names[
                config_file_path_name
            ]
            blank_component_names = deep_get(included_config, key)
            blank_component_names += component_names
    return included_config_file_component_names


def merge_components(main_config, included_config_file_components):
    # Process keys in included configs
    for (
        config_file_path_name,
        config_file_components,
    ) in included_config_file_components.items():
        for key in COMPONENT_KEYS:
            components = deep_get(config_file_components, key)
            if not components:
                continue
            existing_components = deep_get(main_config, key)
            for component in components:
                if contains_component(existing_components, component):
                    logger.critical(f"Component {component['name']} already exists.")
                    raise Exception("Duplicate Component")
                else:
                    existing_components.append(component)
    return main_config


def pop_updated_components(
    updated_config, config_file_path_name, included_config_file_component_names
):
    """
    Remove updated contents from self that belong in file at config_file_path_name, return these contents as a dict
    """
    output_components = empty_meltano_components()
    config_file_component_names = included_config_file_component_names[
        config_file_path_name
    ]
    for key in COMPONENT_KEYS:
        component_names = deep_get(config_file_component_names, key)
        if not component_names:
            continue
        updated_components = deep_get(updated_config, key)
        if not updated_components:
            continue
        for name in component_names:
            for idx, updated_component in enumerate(updated_components):
                if updated_component.get("name") == name:
                    updated_component = updated_components.pop(idx)
                    output_components = deep_get(output_components, key)
                    output_components.append(updated_component)
                    break
    # (optional) remove empty keys in output_config
    return output_components


def pop_extras(updated_config):
    for key in EXTRA_KEYS:
        updated_config["extras"].pop(key)


class MultipleMeltanoFile(MeltanoFile):
    def __init__(self, *args, **attrs):
        attrs["included_directories"] = get_included_directories(attrs)
        attrs["included_config_file_path_names"] = get_included_config_file_path_names(
            attrs["included_directories"]
        )
        attrs["all_config_file_path_names"] = attrs[
            "included_config_file_path_names"
        ].copy()
        attrs["all_config_file_path_names"].append(MELTANO_FILE_PATH_NAME)
        attrs["included_config_file_contents"] = get_included_config_file_components(
            attrs["included_config_file_path_names"]
        )
        attrs[
            "included_config_file_component_names"
        ] = get_included_config_file_component_names(
            attrs["included_config_file_contents"]
        )
        attrs = merge_components(attrs, attrs["included_config_file_contents"])
        # Call to super's init will place these new attrs keys in the sub-dictionary 'extras'
        super().__init__(**attrs)

    def pop_config_file_data(self, config_file_path_name):
        if config_file_path_name == MELTANO_FILE_PATH_NAME:
            # Remove the new attrs keys above from the sub-dictionary 'extras'
            pop_extras(self)
            return self
        else:
            return pop_updated_components(
                self, config_file_path_name, self.included_config_file_component_names
            )
