import os
import json
import yaml
import logging

from .project import Project
from .plugin_discovery_service import PluginDiscoveryService


class PluginNotSupportedException(Exception):
    pass


class MissingPluginException(Exception):
    pass


class ProjectAddService:
    EXTRACTOR = "extractor"
    LOADER = "loader"

    def __init__(
        self,
        project: Project,
        plugin_type=None,
        plugin_name=None,
        discovery_service: PluginDiscoveryService = None,
    ):
        self.project = project
        self.plugin_type = plugin_type
        self.plugin_name = plugin_name
        self.plugin = None
        self.discovery_service = discovery_service or PluginDiscoveryService()

        try:
            self.meltano_yml = yaml.load(open(self.project.meltanofile)) or {}
        except Exception as e:
            self.project.meltanofile.open("a").close()
            self.meltano_yml = yaml.load(open(self.project.meltanofile)) or {}

        if self.plugin_type:
            self.plugin = self.discovery_service.find_plugin(
                self.plugin_type, self.plugin_name
            )

    def add(self):
        if not self.plugin:
            raise MissingPluginException("Plugin type or plugin name is not set")

        extract_dict = self.meltano_yml.get(self.plugin_type)
        if not extract_dict:
            self.meltano_yml[self.plugin_type] = []
            extract_dict = self.meltano_yml.get(self.plugin_type)

        if self.plugin.pip_url is not None:
            self.add_to_file()
            self.add_config_stub()
        else:
            raise PluginNotSupportedException()

    def add_config_stub(self):
        plugin_dir = self.project.meltano_dir(self.plugin_type, self.plugin_name)
        os.makedirs(plugin_dir, exist_ok=True)

        with open(
            plugin_dir.joinpath(f"{self.plugin_name}.config.json"), "w"
        ) as config:
            json.dump(self.plugin.config, config)

    def add_to_file(self):
        exists = any(
            p["name"] == self.plugin_name
            for p in self.meltano_yml.get(self.plugin_type, [])
        )

        if exists:
            logging.warn(
                f"{self.plugin_name} is already present, use `meltano install` to install it."
            )
            return

        self.meltano_yml[self.plugin_type].append(
            {"name": self.plugin.name, "url": self.plugin.pip_url}
        )
        with open(self.project.meltanofile, "w") as f:
            f.write(yaml.dump(self.meltano_yml, default_flow_style=False))
