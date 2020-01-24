import os
import yaml
import json
import click
import sys
import logging
from urllib.parse import urlparse

from . import cli
from .params import project
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
from meltano.core.error import SubprocessError
from meltano.core.db import project_engine


@cli.command()
@click.argument(
    "plugin_type", type=click.Choice([type.cli_command for type in list(PluginType)])
)
@click.argument("plugin_name")
@click.option("--custom", is_flag=True)
@click.option("--include-related", is_flag=True)
@project()
@click.pass_context
def add(ctx, project, plugin_type, plugin_name, **flags):
    if flags["custom"]:
        if plugin_type in ("transformer", "transform", "orchestrator"):
            click.secho(f"--custom is not supported for {ctx.invoked_subcommand}")
            raise click.Abort()

        add_service = ProjectAddCustomService(project)
    else:
        add_service = ProjectAddService(project)

    add_plugin(
        add_service,
        project,
        PluginType(f"{plugin_type}s"),
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

    install_service = PluginInstallService(project)

    try:
        click.secho(f"Installing '{plugin_name}'...")
        run = install_service.install_plugin(plugin)
        if run:
            click.secho(run.stdout)
        click.secho(f"Installed '{plugin_name}'.", fg="green")

        click.secho(f"Added and installed {plugin_type} '{plugin_name}'.", fg="green")
    except PluginNotInstallable as install_err:
        logging.info(f"{plugin_type} is not installable, skipping install.")
    except SubprocessError as proc_err:
        click.secho(str(proc_err), fg="red")
        click.secho(proc_err.process.stderr, err=True)
        raise click.Abort()

    docs_link = plugin._extras.get("docs")
    if docs_link:
        click.secho(f"Visit {docs_link} for more details about '{plugin.name}'.")

    if include_related:
        discovery_service = PluginDiscoveryService(project)
        plugin_def = discovery_service.find_plugin(plugin.type, plugin.name)

        related_plugins = add_service.add_related(plugin_def)
        if len(related_plugins) == 0:
            click.secho("No related plugins found that are not already installed.")
        else:
            for plugin in related_plugins:
                click.secho(
                    f"Added related plugin '{plugin.name}' to your Meltano project.",
                    fg="green",
                )

            click.secho(f"Installing {len(related_plugins)} related plugins...")
            install_status = install_service.install_plugins(related_plugins)

            num_installed = len(install_status["installed"])
            num_failed = len(install_status["errors"])

            fg = "green"
            if num_failed >= 0 and num_installed == 0:
                fg = "red"
            elif num_failed > 0 and num_installed > 0:
                fg = "yellow"

            click.secho(
                f"Installed {num_installed}/{num_installed+num_failed} related plugins.",
                fg=fg,
            )
