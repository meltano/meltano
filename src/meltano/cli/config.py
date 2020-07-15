import click
import json

from . import cli
from .params import project

from meltano.core.db import project_engine
from meltano.core.project import Project
from meltano.core.settings_service import SettingValueStore, StoreNotSupportedError
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginMissingError
from meltano.core.config_service import ConfigService
from meltano.core.plugin.settings_service import PluginSettingsService


@cli.group(invoke_without_command=True)
@click.option(
    "--plugin-type", type=click.Choice(PluginType.cli_arguments()), default=None
)
@click.argument("plugin_name")
@click.option("--format", type=click.Choice(["json", "env"]), default="json")
@project(migrate=True)
@click.pass_context
def config(ctx, project, plugin_type, plugin_name, format):
    try:
        plugin_type = PluginType.from_cli_argument(plugin_type) if plugin_type else None

        config = ConfigService(project)
        plugin = config.find_plugin(
            plugin_name, plugin_type=plugin_type, configurable=True
        )

        ctx.obj["subject"] = f"{plugin.type.descriptor} '{plugin.name}'"
    except PluginMissingError:
        if plugin_name == "meltano":
            ctx.obj["subject"] = "Meltano"
            plugin = None
        else:
            raise

    _, Session = project_engine(project)
    session = Session()
    try:
        if plugin:
            settings = PluginSettingsService(project, plugin)
        else:
            settings = ProjectSettingsService(project)

        ctx.obj["settings"] = settings
        ctx.obj["session"] = session

        if ctx.invoked_subcommand is None:
            if format == "json":
                config = settings.as_dict(session=session)
                print(json.dumps(config))
            elif format == "env":
                for env, value in settings.as_env(session=session).items():
                    print(f"{env}={value}")
    finally:
        session.close()


@config.command()
@click.argument("setting_name", nargs=-1, required=True)
@click.argument("value")
@click.option(
    "--store",
    type=click.Choice(SettingValueStore.writables()),
    default=SettingValueStore.AUTO,
)
@click.pass_context
def set(ctx, setting_name, value, store):
    store = SettingValueStore(store)

    settings = ctx.obj["settings"]
    session = ctx.obj["session"]
    subject = ctx.obj["subject"]

    path = list(setting_name)
    try:
        value, metadata = settings.set_with_metadata(
            path, value, store=store, session=session
        )
    except StoreNotSupportedError as err:
        click.secho(
            f"{subject.capitalize()} setting '{path}' could not be set in {store.label}: {err}",
            fg="red",
        )
        raise click.Abort()

    name = metadata["name"]
    store = metadata["store"]
    click.secho(
        f"{subject.capitalize()} setting '{name}' was set in {store.label}: {value!r}",
        fg="green",
    )

    current_value, source = settings.get_with_source(name, session=session)
    if source != store:
        click.secho(
            f"Current value is still: {current_value!r} (from {source.label})",
            fg="yellow",
        )


@config.command()
@click.argument("setting_name", nargs=-1, required=True)
@click.option(
    "--store",
    type=click.Choice(SettingValueStore.writables()),
    default=SettingValueStore.AUTO,
)
@click.pass_context
def unset(ctx, setting_name, store):
    store = SettingValueStore(store)

    settings = ctx.obj["settings"]
    session = ctx.obj["session"]
    subject = ctx.obj["subject"]

    path = list(setting_name)
    try:
        metadata = settings.unset(path, store=store, session=session)
    except StoreNotSupportedError as err:
        click.secho(
            f"{subject.capitalize()} setting '{path}' in {store.label} could not be unset: {err}",
            fg="red",
        )
        raise click.Abort()

    name = metadata["name"]
    store = metadata["store"]
    click.secho(
        f"{subject.capitalize()} setting '{name}' in {store.label} was unset",
        fg="green",
    )

    current_value, source = settings.get_with_source(name, session=session)
    if source is not SettingValueStore.DEFAULT:
        click.secho(
            f"Current value is now: {current_value!r} (from {source.label})",
            fg="yellow",
        )


@config.command()
@click.option(
    "--store",
    type=click.Choice(SettingValueStore.writables()),
    default=SettingValueStore.AUTO,
)
@click.pass_context
def reset(ctx, store):
    store = SettingValueStore(store)

    settings = ctx.obj["settings"]
    session = ctx.obj["session"]
    subject = ctx.obj["subject"]

    try:
        metadata = settings.reset(store=store, session=session)
    except StoreNotSupportedError as err:
        click.secho(
            f"{subject.capitalize()} settings in {store.label} could not be reset: {err}",
            fg="red",
        )
        raise click.Abort()

    store = metadata["store"]
    click.secho(
        f"{subject.capitalize()} settings in {store.label} were reset", fg="green"
    )


@config.command("list")
@click.pass_context
def list_settings(ctx):
    settings = ctx.obj["settings"]
    session = ctx.obj["session"]

    full_config = settings.config_with_metadata(session=session)
    for name, config_metadata in full_config.items():
        value = config_metadata["value"]
        source = config_metadata["source"]
        setting_def = config_metadata["setting"]

        if setting_def._custom:
            click.echo("custom: ", nl=False)

        click.secho(name, fg="blue", nl=False)

        env_keys = [settings.setting_env(setting_def), *setting_def.env_aliases]
        click.echo(f" [env: {', '.join(env_keys)}]", nl=False)

        current_value = click.style(f"{value!r}", fg="green")
        if source is SettingValueStore.DEFAULT:
            click.echo(f" current value: {current_value}", nl=False)

            # The default value and the current value may not match
            # if env vars have been expanded
            if setting_def.value == value:
                click.echo(" (from default)")
            else:
                click.echo(f" (from default: {setting_def.value!r})")
        else:
            if setting_def.value is not None:
                click.echo(f" (default: {setting_def.value!r})", nl=False)

            click.echo(f" current value: {current_value} (from {source.label})")

        if setting_def.description:
            click.echo("\t", nl=False)
            if setting_def.label:
                click.echo(f"{setting_def.label}: ", nl=False)
            click.echo(f"{setting_def.description}")
