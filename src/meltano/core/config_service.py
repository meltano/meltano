import os
import yaml
import logging
from typing import Dict, List, Optional

from meltano.core.utils import nest
from .project import Project
from .plugin import Plugin, PluginType
from .plugin.singer import plugin_factory
from .plugin.dbt import DbtPlugin, DbtTransformPlugin
from .plugin.model import ModelPlugin
from .plugin.error import PluginMissingError


class ConfigService:
    def __init__(self, project: Project):
        self.project = project

    def make_meltano_secret_dir(self):
        os.makedirs(self.project.meltano_dir(), exist_ok=True)

    def add_to_file(self, plugin: Plugin):
        with self.project.meltano_update() as meltano_yml:
            plugins = nest(meltano_yml, "plugins")
            plugins[plugin.type] = plugins.get(plugin.type, [])

        if plugin in self.plugins():
            logging.warning(
                f"{plugin.name} is already present, use `meltano install` to install it."
            )
            return

        with self.project.meltano_update() as meltano_yml:
            meltano_yml["plugins"][plugin.type].append(plugin.canonical())

    def get_plugin(self, plugin_name: str, plugin_type: Optional[PluginType] = None):
        try:
            return next(
                plugin
                for plugin in self.plugins()
                if (
                    plugin.name == plugin_name
                    and (plugin_type is None or plugin.type == plugin_type)
                )
            )
        except StopIteration:
            raise PluginMissingError(plugin_name)

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

    def get_database(self, database_name):
        return yaml.load(
            open(self.project.meltano_dir(f".database_{database_name}.yml"))
        )

    def plugins(self) -> List[Plugin]:
        """Parse the meltano.yml file and return it as `Plugin` instances."""
        # this will parse the meltano.yml file and create an instance of the
        # corresponding `plugin_class` for all the plugins.
        return (
            self.plugin_generator(plugin_type, plugin_def)
            for plugin_type, plugin_defs in self.project.meltano.get(
                "plugins", {}
            ).items()
            for plugin_def in plugin_defs
        )

    def plugin_generator(self, plugin_type: PluginType, plugin_def: Dict):
        if plugin_type == PluginType.TRANSFORMERS:
            return DbtPlugin(**plugin_def)
        elif plugin_type == PluginType.TRANSFORMS:
            return DbtTransformPlugin(**plugin_def)
        elif plugin_type == PluginType.MODELS:
            return ModelPlugin(**plugin_def)
        else:
            return plugin_factory(plugin_type, plugin_def)
