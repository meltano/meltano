import os
import json
import yaml
import logging
import click

from .project import Project
from .plugin import PluginType, Plugin
from .plugin.factory import plugin_factory
from .config_service import ConfigService


class ProjectAddCustomService:
    def __init__(self, project: Project, config_service: ConfigService = None):
        self.project = project
        self.config_service = config_service or ConfigService(project)

    def add(self, plugin_type: PluginType, plugin_name: str):
        plugin = Plugin(plugin_type, plugin_name)
        plugin.pip_url = click.prompt(
            "The `pip URL` refers to the pip installation specification.\n"
            "You may provide any pip-compatible entry:\n"
            "\tfrom VCS: git+https://gitlab.com/meltano/tap-carbon-intensity.git\n"
            "\tfrom PyPI: tap-something\n"
            "\tfrom Source: [-e] /path/to/plugin/source\n\n"
            "(pip_url)",
            type=str,
        )
        plugin._extras["executable"] = click.prompt(
            "The `executable` refers to the entrypoint of the plugin.\n"
            "By convention, plugins should use their package name as executable, "
            "but it might be useful to override it to have multiple flavors of the same "
            "plugin installed.\n\n"
            "(executable)",
            default=plugin_name,
        )

        self.config_service.add_to_file(plugin)

        click.secho(
            "The plugin has been added to your `meltano.yml`.\n"
            "If your plugin requires configuration options, you must add them directly "
            "in the created plugin definition under the `config` section.\n\n"
            "Then, run `meltano install` to update the plugin configuration.",
            fg="yellow",
        )

        return plugin_factory(plugin.type, plugin.canonical())
