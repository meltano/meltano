import os
import yaml
from typing import Dict, List

from .plugin import Plugin, PluginType
from .plugin.singer import plugin_factory
from .plugin.dbt import DbtPlugin


class PluginNotFoundError(Exception):
    pass


class PluginDiscoveryInvalidError(Exception):
    invalid_message = "Invalid discovery file."
    pass


class PluginDiscoveryService:
    def __init__(self):
        self.discovery_file = os.path.join(os.path.dirname(__file__), "discovery.yml")
        self.load()

    def load(self):
        with open(self.discovery_file) as f:
            try:
                self.discovery_data = yaml.load(f)
            except Exception as e:
                raise PluginDiscoveryInvalidError()

    def plugins(self) -> List[Plugin]:
        """Parse the discovery file and returns it as `Plugin` instances."""
        # this will parse the discovery file and create an instance of the
        # corresponding `plugin_class` for all the plugins.
        return (
            self.plugin_generator(plugin_type, plugin_def)
            for plugin_type, plugin_defs in self.discovery_data.items()
            for plugin_def in plugin_defs
        )

    def plugin_generator(self, plugin_type: PluginType, plugin_def: Dict):
        if plugin_type == PluginType.TRANSFORMERS:
            return DbtPlugin(**plugin_def)
        else:
            return plugin_factory(plugin_type, plugin_def)

    def find_plugin(self, plugin_type: PluginType, plugin_name: str):
        try:
            return next(
                plugin
                for plugin in self.plugins()
                if (plugin.type == plugin_type and plugin.name == plugin_name)
            )
        except StopIteration:
            raise PluginNotFoundError()

    def discover(self, plugin_type: PluginType):
        """Return a pretty printed list of available plugins."""
        enabled_plugin_types = (
            (PluginType.EXTRACTORS, PluginType.LOADERS, PluginType.TRANSFORMERS)
            if plugin_type == PluginType.ALL
            else (plugin_type,)
        )
        return {
            plugin_type: self.list_discovery(plugin_type)
            for plugin_type in enabled_plugin_types
        }

    def list_discovery(self, discovery):
        return "\n".join(
            plugin.name for plugin in self.plugins() if plugin.type == discovery
        )
