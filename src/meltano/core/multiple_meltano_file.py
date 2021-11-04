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
EXTRA_KEYS = [
    "included_directories",
    "included_config_file_path_names",
    "included_config_file_contents",
    "included_config_file_component_names",
    "all_config_file_path_names",
    "project_root",
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


def deep_set(dictionary: dict, keys: str, value=None) -> None:
    """
    Set the value at a key in a nested dictionary.
    If any of the keys in the chain do not exist, create them with an empty dictionary as their value.
    Set the value of the key at the end of the chain to the given value.
    Should not fail, returns nothing.
    :param dictionary: A nested dictionary of n layers (where n>=1).
    :param keys: A chain of keys (joined by '.') representing a path through the nested dictionary.
    :param value: The value to set the key at the end of the chain. The default value is an empty list.
    :return: None
    """
    if value is None:
        value = []
    keys = keys.split(".")
    for key in keys[:-1]:
        dictionary = dictionary.setdefault(key, {})
    dictionary[keys[-1]] = value


def deep_pop(dictionary: dict, keys: str):
    """
    Pop a key-value pair from a nested dictionary. Raises KeyError like a normal dict.pop.
    Also raises AttributeError if the value of any key in the chain does not have a pop method.
    :param dictionary: A nested dictionary of n layers (where n>=1).
    :param keys: A chain of keys (joined by '.') representing a path through the nested dictionary.
    :return: The value popped from the dictionary at key.
    """
    keys = keys.split(".")
    pop_key = keys.pop(-1)
    if keys:
        keys = ".".join(keys)
        dictionary = deep_get(dictionary, keys)
    return dictionary.pop(pop_key)


def pop_keys(dictionary: dict, keys: List[str]):
    """
    Pop a list of keys from a dictionary and discard their values.
    Should not fail, returns nothing.
    :param dictionary: A dictionary.
    :param keys: A list of keys
    :return: None
    """
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
    """
    If any component key in COMPONENT_KEYS does not exist in the given config, create it with an empty list as its value.
    :param main_config: A dictionary representation of a Meltano config file
    :return: The same dictionary after cleaning.
    """
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
    project_root = Path(main_config["project_root"])
    included_path_names = main_config.get(INCLUDE_PATHS_KEY)

    if included_path_names is None:
        # Include paths are optional
        pass
    else:
        for path_name in included_path_names:

            # Enforce relative paths
            if os.path.isabs(path_name):
                logger.critical(
                    f"Included path '{path_name}' is not relative to the project root."
                )
                raise Exception("Invalid Included Path")

            # Assumes root is already resolved
            abs_path_name = str(project_root.joinpath(path_name))

            # Exclude project root
            if abs_path_name == str(project_root):
                logger.critical("Project root is not allowed to be an included path.")
                raise Exception("Invalid Included Path")

            # Verify each path is valid
            if os.path.isdir(abs_path_name):
                included_directories.append(abs_path_name)
            else:
                logger.critical(
                    f"Included path '{abs_path_name}' is not a valid directory."
                )
                raise Exception("Invalid Included Path")

    return included_directories


def get_included_config_file_path_names(included_directories: List[str]):
    # Get config paths in included directories
    included_config_file_path_names: List[str] = []
    for directory in included_directories:
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
    is_main_config: bool = True,
):
    if is_main_config:
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
        attrs["all_config_file_path_names"].append(
            os.path.join(attrs["project_root"], "meltano.yml")
        )
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
