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
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.project_add_custom_service import ProjectAddCustomService
from meltano.core.plugin_install_service import (
    PluginInstallService,
    PluginNotInstallable,
)
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.config_service import ConfigService
from meltano.core.plugin import PluginType, Plugin
from meltano.core.project import Project
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.error import SubprocessError
from meltano.core.db import project_engine


@cli.group()
@click.option("--custom", is_flag=True)
@project()
@click.pass_context
def add(ctx, project, custom):
    if custom:
        if ctx.invoked_subcommand in (
            "related",
            "transformer",
            "transform",
            "orchestrator",
            "connections",
        ):
            click.secho(f"--custom is not supported for {ctx.invoked_subcommand}")
            raise click.Abort()

        ctx.obj["add_service"] = ProjectAddCustomService(project)
    else:
        ctx.obj["add_service"] = ProjectAddService(project)


@add.command()
@project()
@click.pass_context
def related(ctx, project):
    config_service = ConfigService(project)
    discovery_service = PluginDiscoveryService(project)

    added_plugins = []
    installed_plugins = config_service.plugins()
    for plugin_install in installed_plugins:
        try:
            plugin_def = discovery_service.find_plugin(
                plugin_install.type, plugin_install.name
            )
        except PluginNotFoundError:
            continue

        related_plugins = ctx.obj["add_service"].add_related(plugin_def)

        for plugin in related_plugins:
            if plugin in installed_plugins or plugin in added_plugins:
                continue

            click.secho(
                f"Added '{plugin.name}' to your Meltano project because it is related to '{plugin_def.name}'.",
                fg="green",
            )

            added_plugins.append(plugin)

    if len(added_plugins) == 0:
        click.secho("No related plugins found that are not already installed.")
        return

    click.secho("Run `meltano install` to install them.")


@add.command()
@click.argument("plugin_name")
@project()
@click.pass_context
def dashboard(ctx, project, plugin_name):
    add_plugin(ctx.obj["add_service"], project, PluginType.DASHBOARDS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="dashboard", plugin_name=plugin_name)


@add.command()
@click.argument("plugin_name")
@project()
@click.pass_context
def extractor(ctx, project, plugin_name):
    add_plugin(ctx.obj["add_service"], project, PluginType.EXTRACTORS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="extractor", plugin_name=plugin_name)


@add.command()
@click.argument("plugin_name")
@project()
@click.pass_context
def model(ctx, project, plugin_name):
    add_plugin(ctx.obj["add_service"], project, PluginType.MODELS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="model", plugin_name=plugin_name)


@add.command()
@click.argument("plugin_name")
@project()
@click.pass_context
def loader(ctx, project, plugin_name):
    add_plugin(ctx.obj["add_service"], project, PluginType.LOADERS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="loader", plugin_name=plugin_name)


@add.command()
@click.argument("plugin_name")
@project()
@click.pass_context
def transformer(ctx, project, plugin_name):
    add_plugin(ctx.obj["add_service"], project, PluginType.TRANSFORMERS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="transformer", plugin_name=plugin_name)


@add.command()
@click.argument("plugin_name")
@project()
@click.pass_context
def orchestrator(ctx, project, plugin_name):
    add_plugin(ctx.obj["add_service"], project, PluginType.ORCHESTRATORS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="orchestrator", plugin_name=plugin_name)


@add.command()
@click.argument("plugin_name")
@project()
@click.pass_context
def transform(ctx, project, plugin_name):
    add_plugin(ctx.obj["add_service"], project, PluginType.TRANSFORMS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="transform", plugin_name=plugin_name)


def add_plugin(
    add_service, project: Project, plugin_type: PluginType, plugin_name: str
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

    try:
        click.secho(f"Installing '{plugin_name}'...")
        install_service = PluginInstallService(project)
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
