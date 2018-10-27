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


class Plugin:
    def __init__(self, name=None, pip_url=None, config=None):
        self.name = name
        self.pip_url = pip_url
        self.config = config

