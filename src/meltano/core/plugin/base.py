from enum import Enum


class PluginMissingError(Exception):
    """
    Base exception when a plugin seems to be missing.
    """
    def __init__(self, plugin_or_name):
        if isinstance(Plugin, plugin_or_name):
            self.plugin_name = plugin_or_name.name
        else:
            self.plugin_name = plugin_or_name


class PluginType(str, Enum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    ALL = "all"

    def __str__(self):
        return self.value



class Plugin:
    def __init__(self,
                 plugin_type: PluginType,
                 name: str,
                 pip_url=None,
                 config=None):
        self.name = name
        self.type = plugin_type
        self.pip_url = pip_url
        self.config = config

    @property
    def config_files(self):
        """
        Return a list of stubbed files created for this plugin.
        """
        return []

    @property
    def output_files(self):
        return []
