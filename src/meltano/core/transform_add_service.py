import os
import json
import yaml
import logging
from pathlib import Path

from .project import Project
from .config_service import ConfigService
from .plugin.settings_service import PluginSettingsService
from .plugin_discovery_service import PluginDiscoveryService
from .plugin import Plugin, PluginType, PluginInstall
from .db import project_engine


class TransformAddService:
    def __init__(self, project: Project):
        self.project = project

        _, Session = project_engine(project)
        session = Session()

        config_service = ConfigService(project)
        dbt_plugin = config_service.find_plugin(
            plugin_name="dbt", plugin_type=PluginType.TRANSFORMERS
        )

        plugin_settings_service = PluginSettingsService(project)
        dbt_project_dir, _ = plugin_settings_service.get_value(
            session, dbt_plugin, "project_dir"
        )
        dbt_project_path = Path(dbt_project_dir)

        self.packages_file = dbt_project_path.joinpath("packages.yml")
        self.dbt_project_file = dbt_project_path.joinpath("dbt_project.yml")

    def add_to_packages(self, plugin: Plugin):
        if not os.path.exists(self.packages_file):
            with open(self.packages_file, "w"):
                pass

        package_yaml = yaml.safe_load(self.packages_file.open()) or {"packages": []}

        for package in package_yaml["packages"]:
            if package.get("git", "") == plugin.pip_url:
                return

        package_yaml["packages"].append({"git": plugin.pip_url})

        with open(self.packages_file, "w") as f:
            f.write(yaml.dump(package_yaml, default_flow_style=False))

    def update_dbt_project(self, plugin: PluginInstall):
        discovery_service = PluginDiscoveryService(self.project)
        plugin_def = discovery_service.find_plugin(plugin.type, plugin.name)
        model_name = plugin_def.namespace

        dbt_project_yaml = yaml.safe_load(self.dbt_project_file.open())

        dbt_project_yaml["models"][model_name] = plugin._extras

        with open(self.dbt_project_file, "w") as f:
            f.write(yaml.dump(dbt_project_yaml, default_flow_style=False))
