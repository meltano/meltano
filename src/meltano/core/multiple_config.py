import os
from pathlib import Path

import yaml


def load(configfile: Path) -> dict:
    return yaml.safe_load(configfile.open())


class MultipleConfigService:
    """
    Represent the current Meltano project from a file-system
    perspective.
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
        ]  # TODO Expand to include critical Meltano keys
        self.key_value_holder: dict = {}
        for key in self.keys:
            self.key_value_holder[key] = {}
        self._secondary_configs = []  # list of Paths of secondary configs as strings

    @property
    def secondary_configs(self):
        return self._secondary_configs

    @secondary_configs.setter
    def secondary_configs(self, primary_load):
        # TODO get directory contents
        try:
            paths = primary_load["include-paths"].copy()
            for path in paths:
                full_path = self.primary.parent.joinpath(path)
                files = sorted(os.listdir(full_path))
                yamls = [
                    full_path.joinpath(file) for file in files if file[-4::] == ".yml"
                ]
                self._secondary_configs += [
                    yaml for yaml in yamls if yaml not in self._secondary_configs
                ]
        except KeyError:
            pass

    def process_loaded_values(self, key, secondary_load):
        try:
            values = secondary_load[key]
            for value in values:
                self.key_value_holder[key][value["name"]] = value
        except KeyError:
            pass

    def process_secondary_configs(self, primary_load):
        # Update global key values with contents from secondary loads
        self.secondary_configs = primary_load
        if self.secondary_configs:
            for secondary in self.secondary_configs:
                secondary_load = load(secondary)
                for key in self.keys:
                    self.process_loaded_values(key, secondary_load)

    def process_primary_config(self, primary_load):
        # Update global key values with contents from primary load
        try:
            extractors = primary_load["plugins"]["extractors"]
            for extractor in extractors:
                self.key_value_holder["extractors"][extractor["name"]] = extractor
        except KeyError:
            pass

        try:
            loaders = primary_load["plugins"]["loaders"]
            for loader in loaders:
                self.key_value_holder["loaders"][loader["name"]] = loader
        except KeyError:
            pass

        try:
            schedules = primary_load["schedules"]
            for schedule in schedules:
                self.key_value_holder["schedules"][schedule["name"]] = schedule
        except KeyError:
            pass

        # replace primary key values with global key values
        try:
            primary_load["plugins"]["extractors"] = list(
                self.key_value_holder["extractors"].values()
            )
            primary_load["plugins"]["loaders"] = list(
                self.key_value_holder["loaders"].values()
            )
            primary_load["schedules"] = list(
                self.key_value_holder["schedules"].values()
            )
        except KeyError:
            pass

    def load_meltano_read(self):
        primary_load = load(self.primary)
        self.process_secondary_configs(primary_load)
        self.process_primary_config(primary_load)
        return primary_load

    def load_meltano_write(self):
        # primary_load = yaml.safe_load(self.primary.open())
        # TODO Yield individual YAMLs (of secondary) for writing purposes
        return None
