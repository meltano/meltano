import os
import yaml
import logging
from typing import Dict, List, Optional, Iterable

from meltano.core.utils import nest, NotFound
from .project import Project
from .plugin import Plugin, PluginInstall, PluginType, PluginRef, Profile
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
                    meltano_yml.plugins[plugin.type] = []

                meltano_yml.plugins[plugin.type].append(plugin)
            else:
                logging.warning(
                    f"{plugin.name} is already present, use `meltano install` to install it."
                )

        return plugin_factory(plugin.type, plugin.canonical())

    def has_plugin(self, plugin_name: str):
        try:
            self.find_plugin(plugin_name)
            return True
        except PluginMissingError:
            return False

    def find_plugin(self, plugin_name: str, plugin_type: Optional[PluginType] = None):
        name, profile_name = PluginRef.parse_name(plugin_name)
        try:
            plugin = next(
                plugin
                for plugin in self.plugins()
                if (
                    plugin.name == name
                    and (plugin_type is None or plugin.type == plugin_type)
                )
            )
            plugin.use_profile(profile_name)

            return plugin
        except StopIteration as stop:
            raise PluginMissingError(name) from stop

    def get_plugin(self, plugin_ref: PluginRef) -> PluginInstall:
        try:
            plugin = next(plugin for plugin in self.plugins() if plugin == plugin_ref)
            plugin.use_profile(plugin_ref.current_profile_name)

            return plugin
        except StopIteration as stop:
            raise PluginMissingError(plugin_ref.name) from stop

    def get_extractors(self):
        return filter(lambda p: p.type == PluginType.EXTRACTORS, self.plugins())

    def get_loaders(self):
        return filter(lambda p: p.type == PluginType.LOADERS, self.plugins())

    def get_transforms(self):
        return filter(lambda p: p.type == PluginType.TRANSFORMS, self.plugins())

    def get_models(self):
        return filter(lambda p: p.type == PluginType.MODELS, self.plugins())

    def get_dashboards(self):
        return filter(lambda p: p.type == PluginType.DASHBOARDS, self.plugins())

    def get_transformers(self):
        return filter(lambda p: p.type == PluginType.TRANSFORMERS, self.plugins())

    def update_plugin(self, plugin: PluginInstall):
        with self.project.meltano_update() as meltano:
            # find the proper plugin to update
            idx, outdated = next(
                (i, it)
                for i, it in enumerate(meltano.plugins[plugin.type])
                if it == plugin
            )

            meltano.plugins[plugin.type][idx] = plugin

            return outdated

    def plugins(self) -> Iterable[PluginInstall]:
        for plugin_type, plugins in self.project.meltano.plugins:
            yield from plugins
