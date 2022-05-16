"""Config management CLI."""

import json
import tempfile
from pathlib import Path

import click
import dotenv

from meltano.core.db import project_engine
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin_test_service import PluginTestServiceFactory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.settings_service import SettingValueStore
from meltano.core.settings_store import StoreNotSupportedError
from meltano.core.utils import run_async

from . import cli
from .params import pass_project
from .utils import CliError


@cli.group(
    invoke_without_command=True, short_help="Display Meltano or plugin configuration."
)
@click.option(
    "--plugin-type", type=click.Choice(PluginType.cli_arguments()), default=None
)
@click.argument("plugin_name")
@click.option(
    "--format",
    "config_format",
    type=click.Choice(["json", "env"]),
    default="json",
)
@click.option("--extras", is_flag=True, help="View or list only plugin extras.")
@pass_project(migrate=True)
@click.pass_context
def config(  # noqa: WPS231
    ctx,
    project: Project,
    plugin_type: str,
    plugin_name: str,
    config_format: str,
    extras: bool,
):
    """
    Display Meltano or plugin configuration.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#config
    """
    plugin_type = PluginType.from_cli_argument(plugin_type) if plugin_type else None

    plugins_service = ProjectPluginsService(project)

    try:
        plugin = plugins_service.find_plugin(
            plugin_name, plugin_type=plugin_type, configurable=True
        )
    except PluginNotFoundError:
        if plugin_name == "meltano":
            plugin = None
        else:
            raise

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    try:
        if plugin:
            settings = PluginSettingsService(
                project,
                plugin,
                plugins_service=plugins_service,
            )
            invoker = PluginInvoker(project, plugin)
            run_async(invoker.prepare(session))
        else:
            settings = ProjectSettingsService(
                project, config_service=plugins_service.config_service
            )
            invoker = None

        ctx.obj["settings"] = settings
        ctx.obj["session"] = session
        ctx.obj["invoker"] = invoker

        if ctx.invoked_subcommand is None:
            if config_format == "json":
                process = extras is not True
                json_config = settings.as_dict(
                    extras=extras, process=process, session=session
                )
                click.echo(json.dumps(json_config, indent=2))
            elif config_format == "env":
                env = settings.as_env(extras=extras, session=session)

                with tempfile.NamedTemporaryFile() as temp_dotenv:
                    path = temp_dotenv.name
                    for key, value in env.items():
                        dotenv.set_key(path, key, value)

                    dotenv_content = Path(temp_dotenv.name).read_text()

                click.echo(dotenv_content)
    finally:
        session.close()


@config.command(
    "list",
    short_help=(
        "List all settings for the specified plugin with their names, environment variables, and current values."
    ),
)
@click.option("--extras", is_flag=True)
@click.pass_context
def list_settings(ctx, extras):
    """List all settings for the specified plugin with their names, environment variables, and current values."""
    settings = ctx.obj["settings"]
    session = ctx.obj["session"]

    printed_custom_heading = False
    printed_extra_heading = extras

    # If `--extras` is not specified (`False`), we still want to load both
    # regular and extra settings, since we show custom extras.
    load_extras = True if extras else None

    full_config = settings.config_with_metadata(session=session, extras=load_extras)
    for name, config_metadata in full_config.items():
        value = config_metadata["value"]
        source = config_metadata["source"]
        setting_def = config_metadata["setting"]

        if extras:
            if not setting_def.is_extra:
                continue

            if setting_def.is_custom and not printed_custom_heading:
                click.echo()
                click.echo("Custom:")
                printed_custom_heading = True
        elif setting_def.is_extra:
            if not setting_def.is_custom:
                continue

            if not printed_extra_heading:
                click.echo()
                click.echo("Custom extras, plugin-specific options handled by Meltano:")
                printed_extra_heading = True
        elif setting_def.is_custom and not printed_custom_heading:
            click.echo()
            click.echo("Custom, possibly unsupported by the plugin:")
            printed_custom_heading = True

        click.secho(name, fg="blue", nl=False)

        env_keys = [var.definition for var in settings.setting_env_vars(setting_def)]
        click.echo(f" [env: {', '.join(env_keys)}]", nl=False)

        if source is not SettingValueStore.DEFAULT:
            default_value = setting_def.value
            if default_value is not None:
                click.echo(f" (default: {default_value!r})", nl=False)

        if source is SettingValueStore.DEFAULT:
            label = "default"
        elif source is SettingValueStore.INHERITED:
            label = f"inherited from '{settings.plugin.parent.name}'"
        else:
            label = f"from {source.label}"

        current_value = click.style(f"{value!r}", fg="green")
        click.echo(f" current value: {current_value}", nl=False)

        unexpanded_value = config_metadata.get("unexpanded_value")
        if not unexpanded_value or unexpanded_value == value:
            click.echo(f" ({label})")
        else:
            click.echo(f" ({label}: {unexpanded_value!r})")

        if setting_def.description:
            click.echo("\t", nl=False)
            if setting_def.label:
                click.echo(f"{setting_def.label}: ", nl=False)
            click.echo(f"{setting_def.description}")

    docs_url = settings.docs_url
    if docs_url:
        click.echo()
        click.echo(
            f"To learn more about {settings.label} and its settings, visit {docs_url}"
        )


@config.command()
@click.option(
    "--store",
    type=click.Choice(SettingValueStore.writables()),
    default=SettingValueStore.AUTO,
)
@click.pass_context
def reset(ctx, store):
    """Clear the configuration (back to defaults)."""
    store = SettingValueStore(store)

    settings = ctx.obj["settings"]
    session = ctx.obj["session"]

    try:
        metadata = settings.reset(store=store, session=session)
    except StoreNotSupportedError as err:
        raise CliError(
            f"{settings.label.capitalize()} settings in {store.label} could not be reset: {err}"
        ) from err

    store = metadata["store"]
    click.secho(
        f"{settings.label.capitalize()} settings in {store.label} were reset",
        fg="green",
    )


@config.command("set")
@click.argument("setting_name", nargs=-1, required=True)
@click.argument("value")
@click.option(
    "--store",
    type=click.Choice(SettingValueStore.writables()),
    default=SettingValueStore.AUTO,
)
@click.pass_context
def set_(ctx, setting_name, value, store):
    """Set the configurations' setting `<name>` to `<value>`."""
    store = SettingValueStore(store)

    try:
        value = json.loads(value)
    except json.JSONDecodeError:
        pass

    settings = ctx.obj["settings"]
    session = ctx.obj["session"]

    path = list(setting_name)
    try:
        value, metadata = settings.set_with_metadata(
            path, value, store=store, session=session
        )
    except StoreNotSupportedError as err:
        raise CliError(
            f"{settings.label.capitalize()} setting '{path}' could not be set in {store.label}: {err}"
        ) from err

    name = metadata["name"]
    store = metadata["store"]
    click.secho(
        f"{settings.label.capitalize()} setting '{name}' was set in {store.label}: {value!r}",
        fg="green",
    )

    current_value, source = settings.get_with_source(name, session=session)
    if source != store:
        click.secho(
            f"Current value is still: {current_value!r} (from {source.label})",
            fg="yellow",
        )


@config.command("test")
@click.pass_context
def test(ctx):
    """Test the configuration of a plugin."""
    invoker = ctx.obj["invoker"]
    if not invoker:
        raise CliError("Testing of the Meltano project configuration is not supported")

    session = ctx.obj["session"]

    async def _validate():  # noqa: WPS430
        async with invoker.prepared(session):
            plugin_test_service = PluginTestServiceFactory(invoker).get_test_service()
            return await plugin_test_service.validate()

    is_valid, detail = run_async(_validate())

    if not is_valid:
        raise CliError("\n".join(("Plugin configuration is invalid", detail)))

    click.secho("Plugin configuration is valid", fg="green")


@config.command()
@click.argument("setting_name", nargs=-1, required=True)
@click.option(
    "--store",
    type=click.Choice(SettingValueStore.writables()),
    default=SettingValueStore.AUTO,
)
@click.pass_context
def unset(ctx, setting_name, store):
    """Unset the configurations' setting called `<name>`."""
    store = SettingValueStore(store)

    settings = ctx.obj["settings"]
    session = ctx.obj["session"]

    path = list(setting_name)
    try:
        metadata = settings.unset(path, store=store, session=session)
    except StoreNotSupportedError as err:
        raise CliError(
            f"{settings.label.capitalize()} setting '{path}' in {store.label} could not be unset: {err}"
        ) from err

    name = metadata["name"]
    store = metadata["store"]
    click.secho(
        f"{settings.label.capitalize()} setting '{name}' in {store.label} was unset",
        fg="green",
    )

    current_value, source = settings.get_with_source(name, session=session)
    if source is not SettingValueStore.DEFAULT:
        click.secho(
            f"Current value is now: {current_value!r} (from {source.label})",
            fg="yellow",
        )
