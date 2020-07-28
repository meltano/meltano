import os
import yaml
import json
import click
import sys
import logging
from urllib.parse import urlparse
from typing import List

from . import cli
from .params import project
from .utils import CliError, add_plugin, add_related_plugins, install_plugins
from meltano.core.plugin import PluginType
from meltano.core.config_service import ConfigService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.project_add_service import ProjectAddService
from meltano.core.project_add_custom_service import ProjectAddCustomService
from meltano.core.plugin_install_service import PluginInstallReason


@cli.command()
@click.argument("plugin_type", type=click.Choice(PluginType.cli_arguments()))
@click.argument("plugin_name", nargs=-1, required=True)
@click.option("--custom", is_flag=True)
@click.option("--include-related", is_flag=True)
@project()
@click.pass_context
def add(ctx, project, plugin_type, plugin_name, **flags):
    plugin_type = PluginType.from_cli_argument(plugin_type)
    plugin_names = plugin_name  # nargs=-1

    config_service = ConfigService(project)
    discovery_service = PluginDiscoveryService(project, config_service=config_service)

    if flags["custom"]:
        if plugin_type in (
            PluginType.TRANSFORMERS,
            PluginType.TRANSFORMS,
            PluginType.ORCHESTRATORS,
        ):
            raise CliError(f"--custom is not supported for {ctx.invoked_subcommand}")

        add_service = ProjectAddCustomService(project, config_service=config_service)
    else:
        add_service = ProjectAddService(
            project,
            plugin_discovery_service=discovery_service,
            config_service=config_service,
        )

    plugins = [
        add_plugin(project, plugin_type, plugin_name, add_service=add_service)
        for plugin_name in plugin_names
    ]

    related_plugin_types = [PluginType.FILES]
    if flags["include_related"]:
        related_plugin_types = list(PluginType)

    related_plugins = add_related_plugins(
        project, plugins, add_service=add_service, plugin_types=related_plugin_types
    )
    plugins.extend(related_plugins)

    # We will install the plugins in reverse order, since dependencies
    # are listed after their dependents in `related_plugins`, but should
    # be installed first.
    plugins.reverse()

    success = install_plugins(project, plugins, reason=PluginInstallReason.ADD)

    if not success:
        raise CliError("Failed to install plugin(s)")

    for plugin in plugins:
        plugin_def = discovery_service.find_plugin(plugin.type, plugin.name)
        docs_url = plugin_def.docs
        if docs_url:
            click.echo()
            click.echo(
                f"To learn more about {plugin.type.descriptor} '{plugin.name}', visit {docs_url}"
            )
