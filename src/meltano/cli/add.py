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
from meltano.core.project_add_custom_service import ProjectAddCustomService
from meltano.core.plugin_install_service import (
    PluginInstallService,
    PluginNotInstallable,
)
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.plugin import PluginType, Plugin
from meltano.core.project import Project
from meltano.core.transform_add_service import TransformAddService
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
def transform(project, plugin_name):
    add_transform(project, plugin_name)

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


def add_transform(project: Project, plugin_name: str):
    try:
        project_add_service = ProjectAddService(project)
        plugin = project_add_service.add(PluginType.TRANSFORMS, plugin_name)
        click.secho(
            f"Added transform '{plugin_name}' to your Meltano project.", fg="green"
        )

        # Add repo to my-test-project/transform/packages.yml
        transform_add_service = TransformAddService(project)
        transform_add_service.add_to_packages(plugin)
        click.secho(
            f"Added transform '{plugin_name}' to your dbt packages.", fg="green"
        )

        # Add model and vars to my-test-project/transform/dbt_project.yml
        transform_add_service.update_dbt_project(plugin)
        click.secho(
            f"Added transform '{plugin_name}' to your dbt_project.yml.", fg="green"
        )
        click.secho(f"Installed '{plugin_name}'.", fg="green")
    except (PluginNotSupportedException, PluginNotFoundError):
        click.secho(f"Error: transform '{plugin_name}' is not supported.", fg="red")
        raise click.Abort()
