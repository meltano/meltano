import os
import yaml
import logging
from typing import Dict, List, Optional

from meltano.core.utils import nest
from .project import Project
from .plugin import Plugin, PluginInstall, PluginType, PluginRef
from .plugin.factory import plugin_factory
from .plugin.error import PluginMissingError


class ConfigService:
    def __init__(self, project: Project):
        self.project = project

    def make_meltano_secret_dir(self):
        os.makedirs(self.project.meltano_dir(), exist_ok=True)

    def add_to_file(self, plugin: PluginInstall):
        installed_def = plugin.canonical()

        if not plugin in self.plugins():
            with self.project.meltano_update() as meltano_yml:
                plugins = nest(meltano_yml, f"plugins.{plugin.type}", value=[])
                plugins.append(installed_def)
        else:
            logging.warning(
                f"{plugin.name} is already present, use `meltano install` to install it."
            )

        return plugin_factory(plugin.type, installed_def)

    def has_plugin(self, plugin_name: str):
        try:
            self.find_plugin(plugin_name)
            return True
        except PluginMissingError:
            return False

    def find_plugin(self, plugin_name: str, plugin_type: Optional[PluginType] = None):
        name, profile = PluginRef.parse_name(plugin_name)
        try:
            plugin = next(
                plugin
                for plugin in self.plugins()
                if (
                    plugin.name == name
                    and (plugin_type is None or plugin.type == plugin_type)
                )
            )

            plugin.profile = profile
            return plugin
        except StopIteration:
            raise PluginMissingError(name)

    def get_extractors(self):
        return filter(lambda p: p.type == PluginType.EXTRACTORS, self.plugins())

    def get_loaders(self):
        return filter(lambda p: p.type == PluginType.LOADERS, self.plugins())

    def get_transformers(self):
        return filter(lambda p: p.type == PluginType.TRANSFORMERS, self.plugins())

    def get_transforms(self):
        return filter(lambda p: p.type == PluginType.TRANSFORMS, self.plugins())

    def get_models(self):
        return filter(lambda p: p.type == PluginType.MODELS, self.plugins())

    def get_connections(self):
        return filter(lambda p: p.type == PluginType.CONNECTIONS, self.plugins())

    def get_database(self, database_name):
        return yaml.load(
            open(self.project.meltano_dir(f".database_{database_name}.yml"))
        )

    def plugins(self) -> List[PluginInstall]:
        """Parse the meltano.yml file and return it as `PluginInstall` instances."""

        # this will parse the meltano.yml file and create an instance of the
        # corresponding `plugin_class` for all the plugins.
        return (
            plugin_factory(plugin_type, plugin_def)
            for plugin_type, plugin_defs in self.project.meltano.get(
                "plugins", {}
            ).items()
            for plugin_def in plugin_defs
        )
