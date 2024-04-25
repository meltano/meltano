"""CLI command `meltano invoke`."""

from __future__ import annotations

import sys
import typing as t

import click
import structlog

from meltano.cli.params import InstallPlugins, install_option, pass_project
from meltano.cli.utils import (
    CliEnvironmentBehavior,
    CliError,
    PartialInstrumentedCmd,
    propagate_stop_signals,
)
from meltano.core.db import project_engine
from meltano.core.error import AsyncSubprocessError
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin_invoker import (
    PluginInvoker,
    UnknownCommandError,
    invoker_factory,
)
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker

    from meltano.core.project import Project
    from meltano.core.tracking import Tracker

logger = structlog.stdlib.get_logger(__name__)


@click.command(
    cls=PartialInstrumentedCmd,
    context_settings={"ignore_unknown_options": True, "allow_interspersed_args": False},
    short_help="Invoke a plugin.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_use_default,
)
@click.option(
    "--print-var",
    help=(
        "Print to stdout the values for the provided environment variables, "
        "as passed to the plugininvoker context. Useful for debugging."
    ),
    multiple=True,
)
@click.option(
    "--plugin-type",
    type=click.Choice(PluginType.cli_arguments()),
    default=None,
)
@click.option(
    "--dump",
    type=click.Choice(["catalog", "config"]),
    help="Dump content of specified file to disk.",
)
@click.option(
    "--list-commands",
    is_flag=True,
    help="List the commands supported by the plugin.",
)
@click.argument("plugin_name", metavar="PLUGIN_NAME[:COMMAND_NAME]")
@click.argument("plugin_args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "--containers",
    is_flag=True,
    help="Execute plugins using containers where possible.",
)
@install_option
@click.pass_context
@pass_project(migrate=True)
@run_async
async def invoke(  # noqa: C901
    project: Project,
    ctx: click.Context,
    plugin_type: str,
    dump: str,
    list_commands: bool,
    plugin_name: str,
    plugin_args: tuple[str, ...],
    install_plugins: InstallPlugins,
    containers: bool = False,
    print_var: str | None = None,
):
    """
    Invoke a plugin's executable with specified arguments.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#invoke
    """
    tracker: Tracker = ctx.obj["tracker"]

    try:
        plugin_name, command_name = plugin_name.split(":")
    except ValueError:
        command_name = None

    plugin_type = PluginType.from_cli_argument(plugin_type) if plugin_type else None

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    try:
        plugin = project.plugins.find_plugin(
            plugin_name,
            plugin_type=plugin_type,
            invokable=True,
        )
        tracker.add_contexts(PluginsTrackingContext([(plugin, command_name)]))
        tracker.track_command_event(CliEvent.inflight)
    except PluginNotFoundError:
        tracker.track_command_event(CliEvent.aborted)
        raise

    if list_commands:
        do_list_commands(plugin)
        tracker.track_command_event(CliEvent.completed)
        return

    await install_plugins(
        project,
        [plugin],
        reason=PluginInstallReason.INVOKE,
        skip_installed=True,
    )

    invoker = invoker_factory(project, plugin)
    try:
        exit_code = await _invoke(
            invoker,
            plugin_args,
            session,
            dump,
            command_name,
            containers,
            print_var=print_var,
        )
    except Exception as invoke_err:
        tracker.track_command_event(CliEvent.failed)
        raise invoke_err

    if exit_code == 0:
        tracker.track_command_event(CliEvent.completed)
    else:
        tracker.track_command_event(CliEvent.failed)
    sys.exit(exit_code)


async def _invoke(
    invoker: PluginInvoker,
    plugin_args: str,
    session: sessionmaker,
    dump: str,
    command_name: str,
    containers: bool,
    print_var: list | None = None,
):
    if command_name is not None:
        command = invoker.find_command(command_name)

    try:
        async with invoker.prepared(session):
            if print_var:
                env = invoker.env()
                for key in print_var:
                    val = env.get(key)
                    click.echo(f"{key}={val}")
            if dump:
                await dump_file(invoker, dump)
                exit_code = 0
            elif (  # noqa: WPS337
                containers
                and command_name is not None
                and command.container_spec is not None
            ):
                return await invoker.invoke_docker(
                    command_name,
                    *plugin_args,
                )
            else:
                handle = await invoker.invoke_async(*plugin_args, command=command_name)
                with propagate_stop_signals(handle):
                    exit_code = await handle.wait()

    except UnknownCommandError as err:
        raise click.BadArgumentUsage(err) from err
    except AsyncSubprocessError as err:
        logger.error(await err.stderr)
        raise
    finally:
        session.close()

    return exit_code


def do_list_commands(plugin):
    """List the commands supported by plugin."""
    if not plugin.supported_commands:
        click.secho(
            f"Plugin '{plugin.name}' does not define any commands.",
            fg="yellow",
        )
        return

    descriptions = {
        f"{plugin.name}:{cmd}": props.description
        for cmd, props in plugin.all_commands.items()
    }
    column_len = max(len(name) for name in descriptions) + 2
    for name, desc in descriptions.items():
        click.secho(name.ljust(column_len, " "), fg="blue", nl=False)
        click.echo(desc)


async def dump_file(invoker: PluginInvoker, file_id: str):
    """Dump file."""
    try:
        content = await invoker.dump(file_id)
    except FileNotFoundError as err:
        raise CliError(f"Could not find {file_id}") from err  # noqa: EM102
    except Exception as err:
        raise CliError(f"Could not dump {file_id}: {err}") from err  # noqa: EM102
    print(content)  # noqa: T201, WPS421
