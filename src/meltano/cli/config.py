import click
from . import cli
from .params import project

from meltano.core.db import project_engine
from meltano.core.project import Project
from meltano.core.config_service import ConfigService
from meltano.core.plugin.settings_service import PluginSettingsService


@cli.group(invoke_without_command=True)
@click.argument("plugin_name")
@project
@click.pass_context
def config(ctx, project, plugin_name):
    config = ConfigService(project)
    plugin = config.find_plugin(plugin_name)

    _, Session = project_engine(project)
    session = Session()
    settings = PluginSettingsService(session, project)

    ctx.obj["settings"] = settings
    ctx.obj["plugin"] = plugin

    if ctx.invoked_subcommand is None:
        print(settings.as_config(plugin))


@config.command()
@click.argument("setting_name")
@click.argument("value")
@click.pass_context
def set(ctx, setting_name, value):
    settings = ctx.obj["settings"]
    plugin = ctx.obj["plugin"]

    settings.set(plugin, setting_name, value)


@config.command()
@click.argument("setting_name")
@click.pass_context
def unset(ctx, setting_name):
    settings = ctx.obj["settings"]
    plugin = ctx.obj["plugin"]

    settings.unset(plugin, setting_name)


@config.command()
@click.pass_context
def reset(ctx):
    settings = ctx.obj["settings"]
    plugin = ctx.obj["plugin"]

    for setting in settings.settings(plugin):
        settings.unset(plugin, setting.name)


@config.command()
@click.pass_context
def list(ctx):
    settings = ctx.obj["settings"]
    plugin = ctx.obj["plugin"]
    plugin_def = settings.get_definition(plugin)

    for setting_def in plugin_def.settings:
        env_key = settings.setting_env(setting_def, plugin_def)
        description_marker = (
            f": {setting_def['description']}" if "description" in setting_def else ""
        )
        click.secho(f"{setting_def['name']} [{env_key}]{description_marker}")
