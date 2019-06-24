import os
import json
import yaml
import logging
import click

from .project import Project
from .plugin import PluginType, PluginInstall
from .plugin.factory import plugin_factory
from .config_service import ConfigService


class ProjectAddCustomService:
    def __init__(self, project: Project, config_service: ConfigService = None):
        self.project = project
        self.config_service = config_service or ConfigService(project)

    def add(self, plugin_type: PluginType, plugin_name: str):
        namespace = click.prompt(
            "The `namespace` refers to the data source name.\n"
            "It is used to infer compatibilty between components.\n"
            "(namespace)",
            type=str,
        )
        pip_url = click.prompt(
            "The `pip URL` refers to the pip installation specification.\n"
            "You may provide any pip-compatible entry:\n"
            "\tfrom VCS: git+https://gitlab.com/meltano/tap-carbon-intensity.git\n"
            "\tfrom PyPI: tap-something\n"
            "\tfrom Source: [-e] /path/to/plugin/source\n\n"
            "(pip_url)",
            type=str,
        )
        executable = click.prompt(
            "The `executable` refers to the entrypoint of the plugin.\n"
            "By convention, plugins should use their package name as executable, "
            "but it might be useful to override it to have multiple flavors of the same "
            "plugin installed.\n\n"
            "(executable)",
            default=plugin_name,
        )

        # manually create the generic PluginInstall to save it
        # as a custom plugin
        install = PluginInstall(
            plugin_type,
            plugin_name,
            pip_url,
            namespace=namespace,
            executable=executable,
        )

        installed = self.config_service.add_to_file(install)
        click.secho(
            "The plugin has been added to your `meltano.yml`.\n"
            "If your plugin requires configuration options, you must add them directly "
            "in the created plugin definition under the `settings` section.\n\n"
            "Then, run `meltano install` to update the plugin configuration.",
            fg="yellow",
        )

        return installed
