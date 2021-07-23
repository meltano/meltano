import os
from pathlib import Path
from typing import List

import yaml

VERBOSE = ["extractors", "loaders"]


def load(configfile: Path) -> dict:
    return yaml.safe_load(configfile.open())


def is_yaml(filename: str) -> bool:
    return filename[-4::] == ".yml" or filename[-5::] == ".yaml"


def is_verbose(config: dict) -> bool:
    """
    A 'verbose' config file is one that contains organizational keys.
    Organizational keys are keys that are only for organizational purposes.
    (For example, 'plugins' in "/meltano.yml".)

    Note: Currently assumes the only organizational key is 'plugins'.
    """
    return "plugins" in config  # May need to check for other organizational keys


class MultipleConfigService:
    """
    Merge configuration information from meltano.yml and included YAMLs into a single dictionary.
    Record history of what configuration information from which config files is used in this dictionary.
    """

    def __init__(
        self,
        primary: Path,
    ):
        self.primary = primary  # pathname of primary config as Path object
        self.keys = [
            "extractors",
            "loaders",
            "schedules",
        ]  # Assumes these are the only keys that are dictionaries
        self.key_value_holder: dict = {}
        for key in self.keys:
            self.key_value_holder[key] = {}
        self._paths: List[Path] = []  # list of Paths of all config files
        self.path_dicts: dict = (
            {}
        )  # mapping of Paths to a dictionary of the loaded config at that path.
        # dictionaries are updated to reflect what from Path is actually used
        self._multiple_config: dict = {}  # the output of this class

    @property
    def multiple_config(self):
        return self._multiple_config

    @multiple_config.setter
    def multiple_config(self, primary_load):
        self._multiple_config = primary_load
        self.process_configs()
        try:
            self._multiple_config["plugins"]["extractors"] = list(
                self.key_value_holder["extractors"].values()
            )
            self._multiple_config["plugins"]["loaders"] = list(
                self.key_value_holder["loaders"].values()
            )
            self._multiple_config["schedules"] = list(
                self.key_value_holder["schedules"].values()
            )
        except KeyError:
            pass

    @property
    def paths(self):
        return self._paths

    @paths.setter
    def paths(self, primary_load):
        self._paths.append(self.primary)
        try:
            for path in primary_load["include-paths"]:
                full_path = self.primary.parent.joinpath(path)
                files = sorted(os.listdir(full_path))
                yaml_files = [
                    full_path.joinpath(file) for file in files if is_yaml(file)
                ]
                self._paths += [
                    yaml_file
                    for yaml_file in yaml_files
                    if yaml_file not in self._paths
                ]
        except KeyError:
            pass

    def process_loaded_values(self, key, config: dict):
        try:
            values = (
                config["plugins"][key]
                if key in VERBOSE and is_verbose(config)
                else config[key]
            )
            for value in values:
                if value["name"] not in self.key_value_holder[key]:
                    self.key_value_holder[key][value["name"]] = value
                else:
                    _ = (
                        config["plugins"][key].remove(value)
                        if key in VERBOSE and is_verbose(config)
                        else config[key].remove(value)
                    )
        except KeyError:
            pass

    def process_configs(self):
        for path in self.paths:
            path_dict = load(path)
            self.path_dicts[path] = path_dict
            for key in self.keys:
                self.process_loaded_values(key, self.path_dicts[path])

    def load(self):
        primary_load = load(self.primary)
        self.paths = primary_load
        self.multiple_config = primary_load
