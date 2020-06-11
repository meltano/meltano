import os
import yaml
import json
import click
import sys
import logging
from urllib.parse import urlparse

from . import cli
from .params import project
from .install import install_plugins
from meltano.core.project_add_service import (
    ProjectAddService,
    PluginNotSupportedException,
    PluginAlreadyAddedException,
)
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.project_add_custom_service import ProjectAddCustomService
from meltano.core.plugin_install_service import (
    PluginInstallService,
    PluginNotInstallable,
)
from meltano.core.plugin import PluginType, Plugin
from meltano.core.project import Project
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.error import PluginInstallError
from meltano.core.db import project_engine


@cli.command()
@click.argument("plugin_type", type=click.Choice(PluginType.cli_arguments()))
@click.argument("plugin_name")
@click.option("--custom", is_flag=True)
@click.option("--include-related", is_flag=True)
@project()
@click.pass_context
def add(ctx, project, plugin_type, plugin_name, **flags):
    plugin_type = PluginType.from_cli_argument(plugin_type)

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

    add_plugin(
        add_service,
        project,
        plugin_type,
        plugin_name,
        include_related=flags["include_related"],
    )

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type=plugin_type, plugin_name=plugin_name)


def add_plugin(
    add_service,
    project: Project,
    plugin_type: PluginType,
    plugin_name: str,
    include_related=False,
):
    try:
        plugin = add_service.add(plugin_type, plugin_name)
        click.secho(f"Added '{plugin_name}' to your Meltano project.", fg="green")
    except PluginAlreadyAddedException as err:
        click.secho(
            f"'{plugin_name}' was found in your Meltano project. Use `meltano install` to install it.",
            fg="yellow",
            err=True,
        )
        plugin = err.plugin
    except (PluginNotSupportedException, PluginNotFoundError):
        click.secho(f"Error: {plugin_type} '{plugin_name}' is not supported.", fg="red")
        raise click.Abort()

    plugins = [plugin]

    if include_related:
        discovery_service = PluginDiscoveryService(project)
        plugin_def = discovery_service.find_plugin(plugin.type, plugin.name)

        related_plugins = add_service.add_related(plugin_def)
        for plugin in related_plugins:
            click.secho(
                f"Added related plugin '{plugin.name}' to your Meltano project.",
                fg="green",
            )

        plugins.extend(related_plugins)

    success = install_plugins(project, plugins)

    docs_link = plugin._extras.get("docs")
    if docs_link:
        click.echo(
            f"For more details about {plugin.type.descriptor} '{plugin.name}', visit {docs_link}"
        )

    if not success:
        raise click.Abort()
