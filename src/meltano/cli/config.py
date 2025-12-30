"""Config management CLI."""

from __future__ import annotations

import json
import sys
import tempfile
import typing as t
from functools import wraps
from pathlib import Path

import click
import dotenv
import structlog

from meltano.cli.interactive import InteractiveConfig
from meltano.cli.params import (
    PluginTypeArg,
    get_install_options,
    pass_project,
)
from meltano.cli.utils import (
    CliEnvironmentBehavior,
    CliError,
    InstrumentedGroup,
    PartialInstrumentedCmd,
)
from meltano.core.db import project_engine
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin_test_service import PluginTestServiceFactory
from meltano.core.setting_definition import SettingValueJSONEncoder
from meltano.core.settings_service import SettingValueStore
from meltano.core.settings_store import StoreNotSupportedError
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext
from meltano.core.utils import run_async

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from meltano.cli.params import InstallPlugins
    from meltano.core.plugin import PluginType
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project
    from meltano.core.project_settings_service import ProjectSettingsService
    from meltano.core.setting_definition import SettingDefinition
    from meltano.core.tracking.tracker import Tracker

logger = structlog.stdlib.get_logger(__name__)

install, no_install, only_install = get_install_options(include_only_install=True)


def _get_plugin(
    *,
    project: Project,
    plugin_name: str,
    plugin_type: PluginType | None = None,
    tracker: Tracker,
) -> ProjectPlugin | None:
    """Get a plugin from the project."""
    plugin: ProjectPlugin | None = None
    try:
        plugin = project.plugins.find_plugin(
            plugin_name,
            plugin_type=plugin_type,
            configurable=True,
        )
        tracker.add_contexts(PluginsTrackingContext([(plugin, None)]))
    except PluginNotFoundError:
        if plugin_name != "meltano":
            tracker.track_command_event(CliEvent.aborted)
            raise

    return plugin


@t.overload
def _get_settings(
    *,
    project: Project,
    plugin: None,
) -> ProjectSettingsService: ...


@t.overload
def _get_settings(
    *,
    project: Project,
    plugin: ProjectPlugin,
) -> PluginSettingsService: ...


def _get_settings(
    *,
    project: Project,
    plugin: ProjectPlugin | None,
) -> ProjectSettingsService | PluginSettingsService:
    """Get project or plugin settings.

    Args:
        project: Meltano project
        plugin: Plugin, or None for Meltano

    Returns:
        Project or plugin settings
    """
    if plugin is None:
        return project.settings

    return PluginSettingsService(project, plugin)


@t.overload
def _get_invoker(*, project: Project, plugin: None) -> None: ...


@t.overload
def _get_invoker(
    *,
    project: Project,
    plugin: ProjectPlugin,
) -> PluginInvoker: ...


def _get_invoker(
    *, project: Project, plugin: ProjectPlugin | None
) -> PluginInvoker | None:
    """Set up plugin invoker, session, and tracker for config test command.

    Args:
        project: Meltano project
        plugin: Plugin, or None for Meltano

    Returns:
        Plugin invoker, or None for Meltano

    Raises:
        PluginNotFoundError: If plugin is not found and not 'meltano'
    """
    return PluginInvoker(project, plugin) if plugin is not None else None


def _get_ctx_arg(*args: t.Any) -> click.Context:
    """Get the click.Context arg from a set of args.

    Args:
        args: the args to get Context from

    Returns:
        The click.Context arg.

    Raises:
        ValueError: if there is no click.Context in the given args.
    """
    for arg in args:
        if isinstance(arg, click.Context):
            return arg
    raise ValueError("No clickContext provided in *args")  # noqa: EM101, TRY003


def _get_store_choices() -> list[str]:
    """Get a list of valid choices for the --store flag.

    Returns:
        SettingValueStore.writables(), without meltano_env
    """
    writables = SettingValueStore.writables()
    writables.remove(SettingValueStore.MELTANO_ENVIRONMENT)
    return [w.value for w in writables]


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
        if store not in {
            SettingValueStore.MELTANO_YML,
            SettingValueStore.MELTANO_ENVIRONMENT,
        }:
            return func(*args, **kwargs, store=store)
        ctx = _get_ctx_arg(*args)
        store = (
            SettingValueStore.MELTANO_YML
            if ctx.obj["is_default_environment"]
            else SettingValueStore.MELTANO_ENVIRONMENT
        )
        return func(*args, **kwargs, store=store)

    return _wrapper


def get_label(metadata, source) -> str:  # noqa: ANN001
    """Get the label for an environment variable's source.

    Args:
        metadata: the metadata for the variable
        source: the source of the variable

    Returns:
        string describing the source of the variable's value
    """
    try:
        return f"from the {metadata['env_var']} variable in {source.label}"
    except KeyError:
        return f"from {source.label}"


class StoreArg(click.Choice):
    """A click.Choice for the --store flag."""

    def __init__(self, **kwargs: t.Any):
        """Initialise StoreArg instance."""
        super().__init__(_get_store_choices(), **kwargs)

    @override
    def convert(
        self,
        value: str,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> SettingValueStore:
        """Convert the value to a SettingValueStore."""
        return SettingValueStore(value)


@click.group(
    cls=InstrumentedGroup,
    invoke_without_command=True,
    short_help="Display Meltano or plugin configuration.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_ignore_default,
)
@click.option(
    "--safe/--unsafe",
    default=True,
    show_default=True,
    help="Expose values for sensitive settings.",
)
@click.pass_context
def config(ctx: click.Context, *, safe: bool) -> None:
    """Display Meltano or plugin configuration.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#config
    """  # noqa: D301
    ctx.obj["safe"] = safe


@_use_meltano_env
@config.command(
    cls=PartialInstrumentedCmd,
    name="print",
    short_help="Print a plugin's configuration.",
)
@click.argument("plugin_name")
@click.option("--plugin-type", type=PluginTypeArg())
@click.option(
    "--format",
    "config_format",
    type=click.Choice(["json", "env"]),
    default="json",
)
@click.option("--extras", is_flag=True, help="View or list only plugin extras.")
@pass_project(migrate=True)
@click.pass_context
def print_config(
    ctx: click.Context,
    project: Project,
    *,
    plugin_name: str,
    plugin_type: PluginType | None,
    config_format: t.Literal["json", "env"],
    extras: bool,
) -> None:
    """Print a plugin's configuration."""
    safe: bool = ctx.obj["safe"]

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    ctx.obj["session"] = session
    ctx.with_resource(session)

    plugin = _get_plugin(
        project=project,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        tracker=ctx.obj["tracker"],
    )
    settings = _get_settings(project=project, plugin=plugin)

    match config_format:
        case "json":
            process = extras is not True
            json_config = settings.as_dict(
                extras=extras,
                process=process,
                session=session,
                redacted=safe,
                redacted_value="*****",
            )
            click.echo(json.dumps(json_config, cls=SettingValueJSONEncoder, indent=2))
        case "env":
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
        case _:  # pragma: no cover
            t.assert_never(config_format)


@_use_meltano_env
@config.command(
    cls=PartialInstrumentedCmd,
    name="list",
    short_help=(
        "List all settings for the specified plugin with their names, "
        "environment variables, and current values."
    ),
)
@click.argument("plugin_name")
@click.option("--plugin-type", type=PluginTypeArg())
@click.option("--extras", is_flag=True, help="List only plugin extras.")
@pass_project(migrate=True)
@click.pass_context
def list_settings(
    ctx: click.Context,
    project: Project,
    *,
    plugin_name: str,
    plugin_type: PluginType | None,
    extras: bool,
) -> None:
    """List all settings for the specified plugin with their names, environment variables, and current values."""  # noqa: E501
    safe: bool = ctx.obj["safe"]
    tracker: Tracker = ctx.obj["tracker"]

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    ctx.obj["session"] = session
    ctx.with_resource(session)

    plugin = _get_plugin(
        project=project,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        tracker=tracker,
    )
    settings = _get_settings(project=project, plugin=plugin)

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
        setting_def: SettingDefinition = config_metadata["setting"]

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
            label = f"{get_label(config_metadata, source)}"

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
@click.argument("plugin_name")
@click.option("--plugin-type", type=PluginTypeArg())
@click.option("--store", type=StoreArg(), default=SettingValueStore.AUTO.value)
@click.confirmation_option()
@pass_project(migrate=True)
@click.pass_context
@_use_meltano_env
def reset(
    ctx: click.Context,
    project: Project,
    *,
    plugin_name: str,
    plugin_type: PluginType | None,
    store: SettingValueStore,
) -> None:
    """Clear the configuration (back to defaults)."""
    tracker: Tracker = ctx.obj["tracker"]

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    ctx.obj["session"] = session
    ctx.with_resource(session)

    plugin = _get_plugin(
        project=project,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        tracker=tracker,
    )
    settings = _get_settings(project=project, plugin=plugin)

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
@click.argument("plugin_name", required=False)
@click.option("--plugin-type", type=PluginTypeArg())
@click.option("--interactive", is_flag=True)
@click.option("--from-file", type=click.File("r"))
@click.argument("setting_name", nargs=-1)
@click.argument("value", required=False)
@click.option("--store", type=StoreArg(), default=SettingValueStore.AUTO.value)
@pass_project(migrate=True)
@click.pass_context
@_use_meltano_env
def set_(
    ctx: click.Context,
    project: Project,
    *,
    plugin_name: str | None,
    plugin_type: PluginType | None,
    setting_name: tuple[str, ...],
    value: str | None,
    store: SettingValueStore,
    interactive: bool,
    from_file: t.TextIO | None,
) -> None:
    """Set the configurations' setting `<name>` to `<value>`."""
    safe: bool = ctx.obj["safe"]
    tracker: Tracker = ctx.obj["tracker"]

    plugin_name = plugin_name or click.prompt("Plugin name", type=str)

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    ctx.obj["session"] = session
    ctx.with_resource(session)

    plugin = _get_plugin(
        project=project,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        tracker=tracker,
    )
    settings = _get_settings(project=project, plugin=plugin)
    setting_name = (
        tuple(setting_name[0].split(".")) if len(setting_name) == 1 else setting_name
    )

    interaction = InteractiveConfig(
        store=store,
        project=project,
        settings=settings,
        safe=safe,
        session=session,
        tracker=tracker,
        extras=False,
    )

    if interactive or (not setting_name and value is None):
        interaction.configure_all()
        ctx.exit()

    if from_file is not None:
        setting_name += (value,)  # type: ignore[operator]
        value = from_file.read().strip()

    interaction.set_value(setting_name=setting_name, value=value, store=store)


@config.command(cls=PartialInstrumentedCmd, name="test")
@click.argument("plugin_name")
@click.option("--plugin-type", type=PluginTypeArg())
@install
@no_install
@only_install
@pass_project(migrate=True)
@click.pass_context
@run_async
async def test(
    ctx: click.Context,
    project: Project,
    *,
    plugin_type: PluginType | None,
    plugin_name: str,
    install_plugins: InstallPlugins,
) -> None:
    """Test the configuration of a plugin."""
    tracker: Tracker = ctx.obj["tracker"]

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    ctx.obj["session"] = session
    ctx.with_resource(session)

    plugin = _get_plugin(
        project=project,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        tracker=tracker,
    )
    invoker = _get_invoker(project=project, plugin=plugin)

    if invoker is None:
        tracker.track_command_event(CliEvent.aborted)
        raise CliError("Testing of the Meltano project configuration is not supported")  # noqa: EM101, TRY003

    plugin_test_service = PluginTestServiceFactory(invoker).get_test_service()

    await install_plugins(
        project,
        [plugin_test_service.plugin_invoker.plugin],
        reason=PluginInstallReason.AUTO,
    )

    stream_buffer_size = project.settings.get("elt.buffer_size")
    line_length_limit = stream_buffer_size // 2

    try:
        async with plugin_test_service.plugin_invoker.prepared(session):
            is_valid, detail = await plugin_test_service.validate(
                limit=line_length_limit,
            )
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
@click.argument("plugin_name")
@click.argument("setting_name", nargs=-1, required=True)
@click.option("--plugin-type", type=PluginTypeArg())
@click.option("--store", type=StoreArg(), default=SettingValueStore.AUTO.value)
@pass_project(migrate=True)
@click.pass_context
@_use_meltano_env
def unset(
    ctx: click.Context,
    project: Project,
    *,
    plugin_name: str,
    plugin_type: PluginType | None,
    setting_name: tuple[str, ...],
    store: SettingValueStore,
) -> None:
    """Unset the configurations' setting called `<name>`."""
    safe: bool = ctx.obj["safe"]
    tracker: Tracker = ctx.obj["tracker"]

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    ctx.obj["session"] = session
    ctx.with_resource(session)

    plugin = _get_plugin(
        project=project,
        plugin_name=plugin_name,
        plugin_type=plugin_type,
        tracker=tracker,
    )
    settings = _get_settings(project=project, plugin=plugin)

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

    current_value, current_metadata = settings.get_with_metadata(
        name,
        session=session,
        redacted=safe,
    )
    if (source := current_metadata["source"]) is not SettingValueStore.DEFAULT:
        click.secho(
            f"Current value is now: {current_value!r} "
            f"({get_label(current_metadata, source)})",
            fg="yellow",
        )
    tracker.track_command_event(CliEvent.completed)
