import os
import yaml
import logging
from typing import Dict, List, Optional, Iterable

from meltano.core.utils import nest, find_named
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
        with self.project.meltano_update() as meltano_yml:
            if not plugin in self.plugins():
                if not plugin.type in meltano_yml.plugins:
                    setattr(meltano_yml.plugins, plugin.type, [])

                plugins = getattr(meltano_yml.plugins, plugin.type)
                plugins.append(plugin)

                return plugin
            else:
                logging.warning(
                    f"{plugin.name} is already present, use `meltano install` to install it."
                )

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
            raise PluginMissingError(plugin.name)

    def get_plugin(self, plugin_ref: PluginRef) -> PluginInstall:
        try:
            plugin = next(
                plugin
                for plugin in self.plugins()
                if (
                    plugin.name == plugin_ref.name
                )
            )

            if plugin_ref.profile and not find_named(plugin.profiles, plugin_ref.profile):
                raise PluginProfileMissingError(plugin.name, plugin_ref.profile)

            plugin.profile = plugin_ref.profile
            return plugin
        except StopIteration:
            raise PluginMissingError(plugin.name)

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

    def update_plugin(self, plugin: PluginInstall):
        with self.project.meltano_update() as meltano:
            # find the proper plugin to update
            idx = next(
                i
                for i, it in enumerate(self.plugins())
                if it == plugin
            )
            meltano["plugins"][plugin.type][idx] = plugin.canonical()

    def plugins(self) -> Iterable[PluginInstall]:
        for plugin_type, plugins in self.project.meltano.plugins:
            yield from plugins
