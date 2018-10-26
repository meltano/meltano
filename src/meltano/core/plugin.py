from enum import Enum


class PluginType(str, Enum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    ALL = "all"

    def __str__(self):
        return self.value


class Plugin:
    def __init__(self, name=None, pip_url=None, config=None):
        self.name = name
        self.pip_url = pip_url
        self.config = config
