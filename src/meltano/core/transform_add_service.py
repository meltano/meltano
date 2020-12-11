import json
import logging
import os
from pathlib import Path

import yaml

from .db import project_engine
from .plugin import PluginType
from .plugin.project_plugin import ProjectPlugin
from .plugin.settings_service import PluginSettingsService
from .project import Project
from .project_plugins_service import ProjectPluginsService


class TransformAddService:
    def __init__(self, project: Project):
        self.project = project

        self.plugins_service = ProjectPluginsService(project)
        dbt_plugin = self.plugins_service.find_plugin(
            plugin_name="dbt", plugin_type=PluginType.TRANSFORMERS
        )

        settings_service = PluginSettingsService(
            project, dbt_plugin, plugins_service=self.plugins_service
        )
        dbt_project_dir = settings_service.get("project_dir")
        dbt_project_path = Path(dbt_project_dir)

        self.packages_file = dbt_project_path.joinpath("packages.yml")
        self.dbt_project_file = dbt_project_path.joinpath("dbt_project.yml")

    def add_to_packages(self, plugin: ProjectPlugin):
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

    def update_dbt_project(self, plugin: ProjectPlugin):
        settings_service = PluginSettingsService(
            self.project, plugin, plugins_service=self.plugins_service
        )

        package_name = settings_service.get("_package_name")
        vars = settings_service.get("_vars")

        model_def = {}
        if vars:
            model_def["vars"] = vars

        dbt_project_yaml = yaml.safe_load(self.dbt_project_file.open())
        dbt_project_yaml["models"][package_name] = model_def

        with open(self.dbt_project_file, "w") as f:
            f.write(
                yaml.dump(dbt_project_yaml, default_flow_style=False, sort_keys=False)
            )
