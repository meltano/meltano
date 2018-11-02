import yaml
from enum import Enum


class YAMLEnum(str, Enum):
    def __str__(self):
        return self.value

    @staticmethod
    def yaml_representer(dumper, obj):
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))


yaml.add_multi_representer(YAMLEnum, YAMLEnum.yaml_representer)


class PluginType(YAMLEnum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    ALL = "all"

    def __str__(self):
        return self.value


class Plugin:
    def __init__(
        self, plugin_type: PluginType, name: str, pip_url=None, config=None, **extras
    ):
        self.name = name
        self.type = plugin_type
        self.pip_url = pip_url
        self.config = config
        self._extras = extras or {}

    def canonical(self):
        return {
            "name": self.name,
            "pip_url": self.pip_url,
            "config": self.config,
            **self._extras,
        }

    @property
    def config_files(self):
        """Return a list of stubbed files created for this plugin."""
        return []

    @property
    def output_files(self):
        return []

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type
