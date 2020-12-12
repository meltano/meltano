import json
import logging
import os
import sys
from typing import List
from urllib.parse import urlparse

import click
import yaml
from meltano.core.plugin import PluginType
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.project_add_service import ProjectAddService
from meltano.core.project_plugins_service import ProjectPluginsService

from . import cli
from .params import pass_project
from .utils import CliError, add_plugin, add_related_plugins, install_plugins


@cli.command()
@click.argument("plugin_type", type=click.Choice(PluginType.cli_arguments()))
@click.argument("plugin_name", nargs=-1, required=True)
@click.option("--inherit-from")
@click.option("--variant")
@click.option("--as", "as_name")
@click.option("--custom", is_flag=True)
@click.option("--include-related", is_flag=True)
@pass_project()
@click.pass_context
def add(
    ctx,
    project,
    plugin_type,
    plugin_name,
    inherit_from=None,
    variant=None,
    as_name=None,
    **flags,
):
    """Add a plugin to your project."""
    plugin_type = PluginType.from_cli_argument(plugin_type)
    plugin_names = plugin_name  # nargs=-1

    if as_name:
        # `add <type> <inherit-from> --as <name>``
        # is equivalent to:
        # `add <type> <name> --inherit-from <inherit-from>``
        inherit_from = plugin_names[0]
        plugin_names = [as_name]

    plugins_service = ProjectPluginsService(project)

    if flags["custom"]:
        if plugin_type in (
            PluginType.TRANSFORMERS,
            PluginType.TRANSFORMS,
            PluginType.ORCHESTRATORS,
        ):
            raise CliError(f"--custom is not supported for {plugin_type}")

    add_service = ProjectAddService(project, plugins_service=plugins_service)

    plugins = [
        add_plugin(
            project,
            plugin_type,
            plugin_name,
            inherit_from=inherit_from,
            variant=variant,
            custom=flags["custom"],
            add_service=add_service,
        )
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

    _print_plugins(plugins)


def _print_plugins(plugins):
    printed_empty_line = False
    for plugin in plugins:
        docs_url = plugin.docs or plugin.repo
        if not docs_url:
            continue

        if not printed_empty_line:
            click.echo()
            printed_empty_line = True

        click.echo(
            f"To learn more about {plugin.type.descriptor} '{plugin.name}', visit {docs_url}"
        )
