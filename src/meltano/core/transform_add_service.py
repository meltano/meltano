import os
import json
import yaml
import logging

from .project import Project
from .plugin import Plugin


class TransformAddService:
    def __init__(self, project: Project):
        self.project = project
        self.packages_file = project.root.joinpath("transform").joinpath("packages.yml")
        self.dbt_project_file = project.root.joinpath("transform").joinpath(
            "dbt_project.yml"
        )

    def add_to_packages(self, plugin: Plugin):
        if not os.path.exists(self.packages_file):
            with open(self.packages_file, "w"):
                pass

        package_yaml = yaml.load(self.packages_file.open()) or {"packages": []}

        for package in package_yaml["packages"]:
            if package.get("git", "") == plugin.pip_url:
                return

        package_yaml["packages"].append({"git": plugin.pip_url})

        with open(self.packages_file, "w") as f:
            f.write(yaml.dump(package_yaml, default_flow_style=False))

    def update_dbt_project(self, plugin: Plugin):
        transform_name = plugin.name.replace("-", "_")
        dbt_project_yaml = yaml.load(self.dbt_project_file.open())

        dbt_project_yaml["models"][transform_name] = plugin._extras

        with open(self.dbt_project_file, "w") as f:
            f.write(yaml.dump(dbt_project_yaml, default_flow_style=False))
