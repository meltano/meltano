"""Helper class for dbt package installation."""

from __future__ import annotations

import os
from pathlib import Path

from meltano.core import yaml
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService


class TransformAddService:
    """Helper class for adding a dbt package to the project."""

    def __init__(self, project: Project) -> None:
        """Create a new TransformAddService.

        Args:
            project: The project to add the dbt package to.
        """
        self.project = project

        self.plugins_service = ProjectPluginsService(project)

        dbt_plugin = self.plugins_service.get_transformer()

        settings_service = PluginSettingsService(
            project, dbt_plugin, plugins_service=self.plugins_service
        )
        dbt_project_dir = settings_service.get("project_dir")
        dbt_project_path = Path(dbt_project_dir)

        self.packages_file = dbt_project_path.joinpath("packages.yml")
        self.dbt_project_file = dbt_project_path.joinpath("dbt_project.yml")

    def add_to_packages(self, plugin: ProjectPlugin) -> None:
        """Add the plugin's package to the project's `packages.yml` file.

        Args:
            plugin: The plugin to add to the project.

        Raises:
            ValueError: If the plugin is missing the git repo URL.
        """
        if not os.path.exists(self.packages_file):
            self.packages_file.touch()

        package_yaml = yaml.load(self.packages_file) or {"packages": []}

        git_repo = plugin.pip_url
        if not git_repo:
            raise ValueError(f"Missing pip_url for transform plugin '{plugin.name}'")

        revision: str | None = None
        if len(git_repo.split("@")) == 2:
            git_repo, revision = git_repo.split("@")
        for package in package_yaml["packages"]:
            same_ref = (
                package.get("git", "") == git_repo
                and package.get("revision", None) == revision
            )
            if same_ref:
                return

        package_ref = {"git": git_repo}
        if revision:
            package_ref["revision"] = revision
        package_yaml["packages"].append(package_ref)

        with open(self.packages_file, "w") as f:
            yaml.dump(package_yaml, f)

    def update_dbt_project(self, plugin: ProjectPlugin) -> None:
        """Set transform package variables in `dbt_project.yml`.

        If not already present, the package name will also be added under dbt 'models'.

        Args:
            plugin: The plugin to add to the project.
        """
        settings_service = PluginSettingsService(
            self.project, plugin, plugins_service=self.plugins_service
        )

        package_name = settings_service.get("_package_name")
        package_vars = settings_service.get("_vars")

        dbt_project_yaml = yaml.load(self.dbt_project_file)

        model_def = {}

        if package_vars:
            # Add variables scoped to the plugin's package name
            config_version = dbt_project_yaml.get("config-version", 1)
            if config_version == 1:
                model_def["vars"] = package_vars
            else:
                project_vars = dbt_project_yaml.get("vars", {})
                project_vars[package_name] = package_vars
                dbt_project_yaml["vars"] = project_vars

        # Add the package's definition to the list of models:
        dbt_project_yaml["models"][package_name] = model_def

        with open(self.dbt_project_file, "w") as f:
            yaml.dump(dbt_project_yaml, f)
