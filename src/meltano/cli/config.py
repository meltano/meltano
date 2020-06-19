import click
import json

from . import cli
from .params import project

from meltano.core.db import project_engine
from meltano.core.project import Project
from meltano.core.plugin import PluginType
from meltano.core.config_service import ConfigService
from meltano.core.plugin.settings_service import (
    PluginSettingsService,
    PluginSettingValueStore,
)


@cli.group(invoke_without_command=True)
@click.option(
    "--plugin-type", type=click.Choice(PluginType.cli_arguments()), default=None
)
@click.argument("plugin_name")
@click.option("--format", type=click.Choice(["json", "env"]), default="json")
@project(migrate=True)
@click.pass_context
def config(ctx, project, plugin_type, plugin_name, format):
    plugin_type = PluginType.from_cli_argument(plugin_type) if plugin_type else None

    config = ConfigService(project)
    plugin = config.find_plugin(plugin_name, plugin_type=plugin_type, configurable=True)

    _, Session = project_engine(project)
    session = Session()
    try:
        settings = PluginSettingsService(project)

        ctx.obj["settings"] = settings
        ctx.obj["plugin"] = plugin
        ctx.obj["session"] = session

        if ctx.invoked_subcommand is None:
            if format == "json":
                config = settings.as_config(session, plugin)
                print(json.dumps(config))
            elif format == "env":
                for env, value in settings.as_env(session, plugin).items():
                    print(f"{env}={value}")
    finally:
        session.close()


@config.command()
@click.argument("setting_name", nargs=-1, required=True)
@click.argument("value")
@click.option(
    "--store",
    type=click.Choice(list(PluginSettingValueStore)),
    default=PluginSettingValueStore.MELTANO_YML,
)
@click.pass_context
def set(ctx, setting_name, value, store):
    settings = ctx.obj["settings"]
    plugin = ctx.obj["plugin"]
    session = ctx.obj["session"]

    path = list(setting_name)
    settings.set(session, plugin, path, value, store)


@config.command()
@click.argument("setting_name", nargs=-1, required=True)
@click.option(
    "--store",
    type=click.Choice(list(PluginSettingValueStore)),
    default=PluginSettingValueStore.MELTANO_YML,
)
@click.pass_context
def unset(ctx, setting_name, store):
    settings = ctx.obj["settings"]
    plugin = ctx.obj["plugin"]
    session = ctx.obj["session"]

    path = list(setting_name)
    settings.unset(session, plugin, path, store)


@config.command()
@click.option(
    "--store",
    type=click.Choice(list(PluginSettingValueStore)),
    default=PluginSettingValueStore.MELTANO_YML,
)
@click.pass_context
def reset(ctx, store):
    settings = ctx.obj["settings"]
    plugin = ctx.obj["plugin"]
    session = ctx.obj["session"]

    settings.reset(session, plugin, store)


@config.command("list")
@click.pass_context
def list_settings(ctx):
    settings = ctx.obj["settings"]
    plugin = ctx.obj["plugin"]
    plugin_def = settings.get_definition(plugin)

    for setting_def in settings.definitions(plugin):
        click.secho(setting_def.name, fg="blue", nl=False)

        env_key = settings.setting_env(setting_def, plugin_def)
        click.echo(f" [{env_key}]", nl=False)

        if setting_def.value is not None:
            click.echo(" (default: %r)" % setting_def.value, nl=False)

        if setting_def.description:
            click.echo(f": {setting_def.description}", nl=False)

        click.echo()
