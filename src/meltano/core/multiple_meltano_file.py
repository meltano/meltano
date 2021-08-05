import logging
import os.path
from functools import reduce
from pathlib import Path
from typing import Dict, List

import yaml
from meltano.core.meltano_file import MeltanoFile

logger = logging.getLogger(__name__)


ACCEPTED_YAML_EXTENSIONS = [".yml", ".yaml"]
COMPONENT_KEYS = [
    "plugins.extractors",
    "plugins.loaders",
    "plugins.transforms",
    "plugins.models",
    "plugins.dashboards",
    "plugins.orchestrators",
    "plugins.transformers",
    "plugins.files",
    "plugins.utilities",
    "schedules",
]
INCLUDE_PATHS_KEY = "include_paths"
MELTANO_FILE_PATH_NAME = "meltano.yml"
EXTRA_KEYS = [
    "included_directories",
    "included_config_file_path_names",
    "included_config_file_contents",
    "included_config_file_component_names",
    "all_config_file_path_names",
]


def load(config_file_path_name: str) -> dict:
    config_file = Path(config_file_path_name)
    return yaml.safe_load(config_file.open())


def deep_get(dictionary: dict, keys: str, default=None):
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        keys.split("."),
        dictionary,
    )


def deep_set(dictionary: dict, keys: str, default=None):
    if default is None:
        default = []
    keys = keys.split(".")
    for key in keys[:-1]:
        dictionary = dictionary.setdefault(key, {})
    dictionary[keys[-1]] = default


def deep_pop(dictionary: dict, keys: str, default=None):
    """
    Assumes keys is at least two levels deep.
    """
    keys = keys.split(".")
    base_keys = ".".join(keys[:-1:])
    pop_key = keys[-1]
    base = deep_get(dictionary, base_keys)
    try:
        return base.pop(pop_key)
    except KeyError:
        return default


def pop_keys(dictionary: dict, keys: List[str]):
    for k in keys:
        try:
            dictionary.pop(k)
        except KeyError:
            pass


def empty_components():
    """
    Return a nested dictionary based on COMPONENT_KEYS
    """
    components = {}
    for key in COMPONENT_KEYS:
        deep_set(components, key)
    return components


def contains_component(components: List[dict], component: dict) -> bool:
    """
    True if component in components else False.
    Assumes all components have names.
    """
    for c in components:
        if component["name"] == c["name"]:
            return True
    return False


def populate_components(main_config: dict):
    for key in COMPONENT_KEYS:
        if deep_get(main_config, key) is None:
            deep_set(main_config, key)
    return main_config


def clean_components(config: dict):
    for key in COMPONENT_KEYS:
        if "." in key:
            value = deep_get(config, key)
        else:
            value = config.get(key)
        if value == [] or value == {}:
            if "." in key:
                deep_pop(config, key)
            else:
                config.pop(key)

    # Hardcoded
    value = config.get("plugins")
    if value == {}:
        config.pop("plugins")

    # Leave template behind if file would empty after cleaning
    if config == {}:
        config = empty_components()

    return config


def get_included_directories(main_config: dict):
    # Process included paths
    included_directories: List[str] = []
    try:
        for path_name in main_config[INCLUDE_PATHS_KEY]:
            # Verify each path is valid
            # TODO abs_path = get absolute of path_name, pass to isdir() (Project() should have abs_path)
            if os.path.isdir(
                path_name
            ):  # TODO paths_name must be relative to project root
                included_directories.append(path_name)
            else:
                logger.critical(
                    f"Included path '{path_name}' is not a valid directory."
                )
                raise Exception("Invalid Included Path")
    except KeyError:
        pass  # Include paths are optional
    return included_directories


def get_included_config_file_path_names(included_directories: List[str]):
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


def get_included_config_file_components(included_config_file_path_names: List[str]):
    # Store loaded contents of each config file
    included_config_file_components: Dict[str, dict] = {}
    for config_file_path_name in included_config_file_path_names:
        config_file_components = load(config_file_path_name)
        included_config_file_components[config_file_path_name] = config_file_components
    return included_config_file_components


def get_included_config_file_component_names(
    included_config_file_components: Dict[str, dict]
):
    # Get names of components in each config file
    included_config_file_component_names: Dict[str, dict] = {}
    for (
        config_file_path_name,
        config_file_components,
    ) in included_config_file_components.items():
        included_config_file_component_names[config_file_path_name] = empty_components()
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


def merge_components(
    main_config: dict, included_config_file_components: Dict[str, dict]
):
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
    updated_config: dict,
    config_file_path_name: str,
    included_config_file_component_names: Dict[str, dict],
):
    """
    Remove updated contents from self that belong in file at config_file_path_name, return these contents as a dict
    """
    all_output_components = empty_components()
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
                    output_components = deep_get(all_output_components, key)
                    output_components.append(updated_component)
                    break
    return all_output_components


def pop_config_file_data(
    updated_config: dict,
    config_file_path_name: str,
    included_config_file_component_names: Dict[str, dict],
):
    if config_file_path_name == MELTANO_FILE_PATH_NAME:
        updated_config = clean_components(updated_config)
        return updated_config
    else:
        output_config = pop_updated_components(
            updated_config, config_file_path_name, included_config_file_component_names
        )
        output_config = clean_components(output_config)
        return output_config


class MultipleMeltanoFile(MeltanoFile):
    def __init__(self, **attrs):
        attrs = populate_components(attrs)
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

    def get_config_path_names(self):
        return self["extras"]["all_config_file_path_names"]

    def get_included_component_names(self):
        return self["extras"]["included_config_file_component_names"]

    def canonical(self):
        as_canonical = super().canonical()
        pop_keys(as_canonical, EXTRA_KEYS)
        return as_canonical
