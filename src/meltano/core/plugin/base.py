from enum import Enum


class PluginType(str, Enum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    ALL = "all"

    def __str__(self):
        return self.value


class Plugin:
    def __init__(self, plugin_type: PluginType, name: str, pip_url=None, config=None):
        self.name = name
        self.type = plugin_type
        self.pip_url = pip_url
        self.config = config

    def canonical(self):
        return {
            "name": self.name,
            "pip_url": self.pip_url,
            "config": self.config
        }

    @property
    def config_files(self):
        """
        Return a list of stubbed files created for this plugin.
        """
        return []

    @property
    def output_files(self):
        return []

    def __eq__(self, other):
        return (self.name == other.name and
                self.type == other.type)
