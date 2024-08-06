"""Config management CLI."""

from __future__ import annotations

import json
import tempfile
import typing as t
from functools import wraps
from pathlib import Path

import click
import dotenv
import structlog

from meltano.cli.interactive import InteractiveConfig
from meltano.cli.params import InstallPlugins, get_install_options, pass_project
from meltano.cli.utils import (
    CliEnvironmentBehavior,
    CliError,
    InstrumentedGroup,
    PartialInstrumentedCmd,
)
from meltano.core.db import project_engine
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin_test_service import PluginTestServiceFactory
from meltano.core.settings_service import SettingValueStore
from meltano.core.settings_store import StoreNotSupportedError
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from meltano.core.project import Project
    from meltano.core.project_settings_service import ProjectSettingsService

logger = structlog.stdlib.get_logger(__name__)

install, no_install, only_install = get_install_options(include_only_install=True)


def _get_ctx_arg(*args: t.Any) -> click.core.Context:
    """Get the click.core.Context arg from a set of args.

    Args:
        args: the args to get Context from

    Returns:
        The click.core.Context arg.

    Raises:
        ValueError: if there is no click.core.Context in the given args.
    """
    for arg in args:
        if isinstance(arg, click.core.Context):
            return arg
    raise ValueError("No click.core.Context provided in *args")  # noqa: EM101


def _get_store_choices() -> list[SettingValueStore]:
    """Get a list of valid choices for the --store flag.

    Returns:
        SettingValueStore.writables(), without meltano_env
    """
    writables = SettingValueStore.writables()
    writables.remove(SettingValueStore.MELTANO_ENV)
    return writables


def _use_meltano_env(func):  # noqa: ANN001, ANN202
    """Override the 'meltano_yml' choice for a config command's 'store' argument.

    If an --environment flag is passed, the decorated command will use
    the MELTANO_ENV store instead of MELTANO_YML but _will not_ use MELTANO_ENV
    store if the active environment is set via the default environment.

    Args:
       func: the command to override

    Returns:
       A wrapped function with overridden store argument
    """

    @wraps(func)
    def _wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        store = kwargs.pop("store")
        if store not in {SettingValueStore.MELTANO_YML, SettingValueStore.MELTANO_ENV}:
            return func(*args, **kwargs, store=store)
        ctx = _get_ctx_arg(*args)
        store = (
            SettingValueStore.MELTANO_YML
            if ctx.obj["is_default_environment"]
            else SettingValueStore.MELTANO_ENV
        )
        return func(*args, **kwargs, store=store)

    return _wrapper


def get_label(metadata) -> str:  # noqa: ANN001
    """Get the label for an environment variable's source.

    Args:
        metadata: the metadata for the variable

    Returns:
        string describing the source of the variable's value
    """
    source = metadata["source"]
    try:
        return f"from the {metadata['env_var']} variable in {source.label}"
    except KeyError:
        return f"from {source.label}"


@click.group(
    cls=InstrumentedGroup,
    invoke_without_command=True,
    short_help="Display Meltano or plugin configuration.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_ignore_default,
)
@click.option(
    "--plugin-type",
    type=click.Choice(PluginType.cli_arguments()),
    default=None,
)
@click.argument("plugin_name")
@click.option(
    "--format",
    "config_format",
    type=click.Choice(["json", "env"]),
    default="json",
)
@click.option("--extras", is_flag=True, help="View or list only plugin extras.")
@click.option(
    "--safe/--unsafe",
    default=True,
    show_default=True,
    help="Expose values for sensitive settings.",
)
@pass_project(migrate=True)
@click.pass_context
def config(
    ctx,  # noqa: ANN001
    project: Project,
    *,
    plugin_type: str,
    plugin_name: str,
    config_format: str,
    extras: bool,
    safe: bool,
) -> None:
    """Display Meltano or plugin configuration.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#config
    """  # noqa: D301
    tracker = ctx.obj["tracker"]
    try:
        ptype = PluginType.from_cli_argument(plugin_type) if plugin_type else None
    except ValueError:
        tracker.track_command_event(CliEvent.aborted)
        raise

    try:
        plugin = project.plugins.find_plugin(
            plugin_name,
            plugin_type=ptype,
            configurable=True,
        )
    except PluginNotFoundError:
        if plugin_name == "meltano":
            plugin = None
        else:
            tracker.track_command_event(CliEvent.aborted)
            raise

    if plugin:
        tracker.add_contexts(PluginsTrackingContext([(plugin, None)]))
    tracker.track_command_event(CliEvent.inflight)

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    try:
        if plugin:
            settings = PluginSettingsService(project, plugin)
            invoker = PluginInvoker(project, plugin)
        else:
            settings = project.settings
            invoker = None

        ctx.obj["settings"] = settings
        ctx.obj["session"] = session
        ctx.obj["invoker"] = invoker
        ctx.obj["safe"] = safe

        if ctx.invoked_subcommand is None:
            if config_format == "json":
                process = extras is not True
                json_config = settings.as_dict(
                    extras=extras,
                    process=process,
                    session=session,
                    redacted=safe,
                    redacted_value="*****",
                )
                click.echo(json.dumps(json_config, indent=2))
            elif config_format == "env":
                env = settings.as_env(
                    extras=extras,
                    session=session,
                    redacted=safe,
                    redacted_value="*****",
                )

                with tempfile.TemporaryDirectory() as temp_dir:
                    path = Path(temp_dir) / ".env"
                    for key, value in env.items():
                        dotenv.set_key(path, key, value)

                    dotenv_content = path.read_text()

                click.echo(dotenv_content)
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise
    finally:
        session.close()


@_use_meltano_env
@config.command(
    cls=PartialInstrumentedCmd,
    name="list",
    short_help=(
        "List all settings for the specified plugin with their names, "
        "environment variables, and current values."
    ),
)
@click.option("--extras", is_flag=True)
@click.pass_context
def list_settings(ctx: click.Context, *, extras: bool) -> None:
    """List all settings for the specified plugin with their names, environment variables, and current values."""  # noqa: E501
    settings: ProjectSettingsService | PluginSettingsService = ctx.obj["settings"]
    session = ctx.obj["session"]
    tracker = ctx.obj["tracker"]
    safe: bool = ctx.obj["safe"]

    printed_custom_heading = False
    printed_extra_heading = extras

    # If `--extras` is not specified (`False`), we still want to load both
    # regular and extra settings, since we show custom extras.
    load_extras = True if extras else None

    full_config = settings.config_with_metadata(
        session=session,
        extras=load_extras,
        redacted=safe,
    )

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
            label = f"inherited from '{settings.plugin.parent.name}'"  # type: ignore[union-attr]
        else:
            label = f"{get_label(config_metadata)}"

        redacted_with_value = safe and setting_def.is_redacted and value is not None

        current_value = click.style(
            value if redacted_with_value else f"{value!r}",
            fg="yellow" if redacted_with_value else "green",
        )

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

    if docs_url := settings.docs_url:
        click.echo()
        click.echo(
            f"To learn more about {settings.label} and its settings, visit {docs_url}",
        )
    tracker.track_command_event(CliEvent.completed)


@config.command(cls=PartialInstrumentedCmd)
@click.option(
    "--store",
    type=click.Choice(_get_store_choices()),
    default=SettingValueStore.AUTO,
)
@click.pass_context
@_use_meltano_env
def reset(ctx, store) -> None:  # noqa: ANN001
    """Clear the configuration (back to defaults)."""
    store = SettingValueStore(store)

    settings = ctx.obj["settings"]
    session = ctx.obj["session"]
    tracker = ctx.obj["tracker"]

    try:
        metadata = settings.reset(store=store, session=session)
    except StoreNotSupportedError:  # pragma: no cover
        tracker.track_command_event(CliEvent.aborted)
        raise

    store = metadata["store"]
    click.secho(
        f"{settings.label.capitalize()} settings in {store.label} were reset",
        fg="green",
    )
    tracker.track_command_event(CliEvent.completed)


@config.command(cls=PartialInstrumentedCmd, name="set")
@click.option("--interactive", is_flag=True)
@click.option("--from-file", type=click.File("r"))
@click.argument("setting_name", nargs=-1)
@click.argument("value", required=False)
@click.option(
    "--store",
    type=click.Choice(_get_store_choices()),
    default=SettingValueStore.AUTO,
)
@click.pass_context
@_use_meltano_env
def set_(
    ctx: click.core.Context,
    *,
    setting_name: tuple[str, ...],
    value: t.Any,  # noqa: ANN401
    store: str,
    interactive: bool,
    from_file: t.TextIO,
) -> None:
    """Set the configurations' setting `<name>` to `<value>`."""
    if len(setting_name) == 1:
        setting_name = tuple(setting_name[0].split("."))

    interaction = InteractiveConfig(ctx=ctx, store=store, extras=False)

    if interactive:
        interaction.configure_all()
        ctx.exit()

    if from_file:
        setting_name += (value,)
        value = from_file.read().strip()

    interaction.set_value(setting_name=setting_name, value=value, store=store)


@config.command(cls=PartialInstrumentedCmd, name="test")
@pass_project(migrate=True)
@click.pass_context
@install
@no_install
@only_install
@run_async
async def test(
    ctx,  # noqa: ANN001
    project: Project,
    install_plugins: InstallPlugins,
) -> None:
    """Test the configuration of a plugin."""
    invoker = ctx.obj["invoker"]
    tracker = ctx.obj["tracker"]
    if not invoker:
        tracker.track_command_event(CliEvent.aborted)
        raise CliError("Testing of the Meltano project configuration is not supported")  # noqa: EM101

    session = ctx.obj["session"]
    plugin_test_service = PluginTestServiceFactory(invoker).get_test_service()

    await install_plugins(
        project,
        [plugin_test_service.plugin_invoker.plugin],
        reason=PluginInstallReason.AUTO,
    )

    try:
        async with plugin_test_service.plugin_invoker.prepared(session):
            is_valid, detail = await plugin_test_service.validate()
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise

    if not is_valid:
        tracker.track_command_event(CliEvent.failed)
        raise CliError(
            "\n".join(
                (
                    "Plugin configuration is invalid",
                    detail or "Plugin did not emit any output",
                ),
            ),
        )

    click.secho("Plugin configuration is valid", fg="green")
    tracker.track_command_event(CliEvent.completed)


@config.command(cls=PartialInstrumentedCmd)
@click.argument("setting_name", nargs=-1, required=True)
@click.option(
    "--store",
    type=click.Choice(_get_store_choices()),
    default=SettingValueStore.AUTO,
)
@click.pass_context
@_use_meltano_env
def unset(ctx, setting_name, store) -> None:  # noqa: ANN001
    """Unset the configurations' setting called `<name>`."""
    store = SettingValueStore(store)

    settings = ctx.obj["settings"]
    session = ctx.obj["session"]
    tracker = ctx.obj["tracker"]

    path = list(setting_name)
    try:
        metadata = settings.unset(path, store=store, session=session)
    except StoreNotSupportedError:  # pragma: no cover
        tracker.track_command_event(CliEvent.aborted)
        raise

    name = metadata["name"]
    store = metadata["store"]
    click.secho(
        f"{settings.label.capitalize()} setting '{name}' in {store.label} was unset",
        fg="green",
    )

    current_value, source = settings.get_with_source(name, session=session)
    if source is not SettingValueStore.DEFAULT:
        click.secho(
            f"Current value is now: {current_value!r} ({get_label(metadata)})",
            fg="yellow",
        )
    tracker.track_command_event(CliEvent.completed)
