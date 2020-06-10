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
from .utils import add_plugin, add_related_plugins, install_plugins
from meltano.core.plugin import PluginType
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

    if flags["custom"]:
        if plugin_type in (
            PluginType.TRANSFORMERS,
            PluginType.TRANSFORMS,
            PluginType.ORCHESTRATORS,
        ):
            click.secho(f"--custom is not supported for {ctx.invoked_subcommand}")
            raise click.Abort()

        add_service = ProjectAddCustomService(project)
    else:
        add_service = ProjectAddService(project)

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

    success = install_plugins(project, plugins, reason=PluginInstallReason.ADD)

    for plugin in plugins:  # TODO: Only works on Plugin from discovery...
        docs_link = plugin._extras.get("docs")
        if docs_link:
            click.echo(
                f"For more details about {plugin.type.descriptor} '{plugin.name}', visit {docs_link}"
            )

    if not success:
        raise click.Abort()
