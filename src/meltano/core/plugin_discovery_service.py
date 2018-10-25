import os, yaml, json
from typing import Dict, List

from .plugin import Plugin, PluginType


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

    def plugins(self, plugin_type: PluginType):
        return (
            Plugin(**plugin_def) for plugin_def in self.discovery_data.get(plugin_type)
        )

    def find_plugin(self, plugin_type: PluginType, plugin_name: str):
        try:
            return next(
                plugin
                for plugin in self.plugins(plugin_type)
                if plugin.name == plugin_name
            )
        except StopIteration:
            return None

    def discover(self, plugin_type: PluginType):
        enabled_plugin_types = (
            (PluginType.EXTRACTORS, PluginType.LOADERS)
            if PluginType.ALL
            else (plugin_type,)
        )
        return {
            plugin_type: self.list_discovery(plugin_type)
            for plugin_type in enabled_plugin_types
        }

    def list_discovery(self, discovery):
        return "\n".join(plugin.name for plugin in self.plugins(discovery))
