import os
import yaml
import json
import click
import sys
from urllib.parse import urlparse
from . import cli
from .params import project
from meltano.core.project_add_service import (
    ProjectAddService,
    PluginNotSupportedException,
    PluginAlreadyAddedException,
)
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.database_add_service import DatabaseAddService
from meltano.core.transform_add_service import TransformAddService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.error import SubprocessError


@cli.group()
def add():
    pass


@add.command()
@project
@click.option("--name", prompt="Database connection name")
@click.option("--host", prompt="Database host")
@click.option("--database", prompt="Database database")
@click.option("--schema", prompt="Database schema")
@click.option("--username", prompt="Database username")
@click.option(
    "--password", prompt="Database password", hide_input=True, confirmation_prompt=True
)
def database(project, name, host, database, schema, username, password):
    database_add_service = DatabaseAddService(project)
    database_add_service.add(
        name=name,
        host=host,
        database=database,
        schema=schema,
        username=username,
        password=password,
    )
    click.secho("database yml file updated", fg="green")


@add.command()
@project
@click.argument("plugin_name")
def extractor(project, plugin_name):
    add_plugin(project, PluginType.EXTRACTORS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="extractor", plugin_name=plugin_name)


@add.command()
@project
@click.argument("plugin_name")
def model(project, plugin_name):
    add_plugin(project, PluginType.MODELS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="model", plugin_name=plugin_name)


@add.command()
@project
@click.argument("plugin_name")
def loader(project, plugin_name):
    add_plugin(project, PluginType.LOADERS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="loader", plugin_name=plugin_name)


@add.command()
@project
@click.argument("plugin_name")
def transformer(project, plugin_name):
    add_plugin(project, PluginType.TRANSFORMERS, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="transformer", plugin_name=plugin_name)


@add.command()
@project
@click.argument("plugin_name")
def transform(project, plugin_name):
    add_transform(project, plugin_name)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type="transform", plugin_name=plugin_name)


def add_plugin(project: Project, plugin_type: PluginType, plugin_name: str):
    try:
        add_service = ProjectAddService(project)
        plugin = add_service.add(plugin_type, plugin_name)
        click.secho(f"Added '{plugin_name}' to your Meltano project.")
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
        install_service = PluginInstallService(project)
        install_service.create_venv(plugin)
        click.secho(f"Activated '{plugin_name}' virtual environment.", fg="green")

        run = install_service.install_plugin(plugin)
        click.secho(run.stdout)
        click.secho(f"Installed '{plugin_name}'.", fg="green")

        click.secho(f"Added and installed {plugin_type} '{plugin_name}'.", fg="green")

        docs_link = plugin._extras.get("docs")
        if docs_link:
            click.secho(f"Visit {docs_link} for more details about '{plugin.name}'.")
    except SubprocessError as proc_err:
        click.secho(str(proc_err), fg="red")
        click.secho(proc_err.process.stderr, err=True)
        raise click.Abort()


def add_transform(project: Project, plugin_name: str):
    try:
        project_add_service = ProjectAddService(project)
        plugin = project_add_service.add(PluginType.TRANSFORMS, plugin_name)
        click.secho(f"Added transform '{plugin_name}' to your Meltano project.")

        # Add repo to my-test-project/transform/packages.yml
        transform_add_service = TransformAddService(project)
        transform_add_service.add_to_packages(plugin)
        click.secho(f"Added transform '{plugin_name}' to your dbt packages", fg="green")

        # Add model and vars to my-test-project/transform/dbt_project.yml
        transform_add_service.update_dbt_project(plugin)
        click.secho(
            f"Added transform '{plugin_name}' to your dbt_project.yml", fg="green"
        )
    except (PluginNotSupportedException, PluginNotFoundError):
        click.secho(f"Error: transform '{plugin_name}' is not supported", fg="red")
        raise click.Abort()
