import os
import yaml
from typing import List

from .project import Project
from .plugin import Plugin, PluginType
from .plugin.singer import plugin_factory
from .plugin.error import PluginMissingError


class ConfigService:
    def __init__(self, project: Project):
        self.project = project

    def make_meltano_secret_dir(self):
        os.makedirs(self.project.meltano_dir(), exist_ok=True)

    def get_plugin(self, plugin_type: PluginType, plugin_name: str):
        try:
            return next(
                plugin
                for plugin in self.plugins()
                if plugin.type == plugin_type and plugin.name == plugin_name
            )
        except StopIteration:
            raise PluginMissingError(plugin_name)

    def get_extractors(self):
        return filter(lambda p: p.type == PluginType.EXTRACTORS, self.plugins())

    def get_loaders(self):
        return filter(lambda p: p.type == PluginType.LOADERS, self.plugins())

    def get_database(self, database_name):
        return yaml.load(
            open(self.project.meltano_dir(f".database_{database_name}.yml"))
        )

    def plugins(self) -> List[Plugin]:
        """Parse the discovery file and returns it as `Plugin` instances."""
        # this will parse the discovery file and create an instance of the
        # corresponding `plugin_class` for all the plugins.
        return (
            plugin_factory(plugin_type, plugin_def)
            for plugin_type, plugin_defs in self.project.meltano.items()
            for plugin_def in plugin_defs
        )
