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

        self.config_service = ConfigService(project)
        dbt_plugin = self.config_service.find_plugin(
            plugin_name="dbt", plugin_type=PluginType.TRANSFORMERS
        )

        self.discovery_service = PluginDiscoveryService(
            self.project, config_service=self.config_service
        )
        settings_service = PluginSettingsService(
            project,
            dbt_plugin,
            config_service=self.config_service,
            plugin_discovery_service=self.discovery_service,
        )
        dbt_project_dir = settings_service.get("project_dir")
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
            f.write(yaml.dump(package_yaml, default_flow_style=False, sort_keys=False))

    def update_dbt_project(self, plugin: PluginInstall):
        plugin_def = self.discovery_service.find_plugin(plugin.type, plugin.name)
        model_name = plugin_def.namespace

        dbt_project_yaml = yaml.safe_load(self.dbt_project_file.open())
        model_def = {}

        settings_service = PluginSettingsService(
            self.project,
            plugin,
            config_service=self.config_service,
            plugin_discovery_service=self.discovery_service,
        )
        vars = settings_service.get("_vars")
        if vars:
            model_def["vars"] = vars

        dbt_project_yaml["models"][model_name] = model_def

        with open(self.dbt_project_file, "w") as f:
            f.write(
                yaml.dump(dbt_project_yaml, default_flow_style=False, sort_keys=False)
            )
