"""CLI command `meltano invoke`."""

from __future__ import annotations

import logging
import sys

import click
from sqlalchemy.orm import sessionmaker

from meltano.cli.cli import cli
from meltano.cli.params import pass_project
from meltano.core.db import project_engine
from meltano.core.error import AsyncSubprocessError
from meltano.core.legacy_tracking import LegacyTracker
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_invoker import (
    PluginInvoker,
    UnknownCommandError,
    invoker_factory,
)
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.tracking import CliContext, CliEvent, PluginsTrackingContext, Tracker
from meltano.core.utils import run_async

from .utils import CliError, propagate_stop_signals

logger = logging.getLogger(__name__)


@cli.commands.invoke
@click.option(
    "--print-var",
    help="Print to stdout the values for the provided environment variables, as passed to the plugininvoker context. Useful for debugging.",
    multiple=True,
)
@click.option(
    "--plugin-type", type=click.Choice(PluginType.cli_arguments()), default=None
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
@pass_project(migrate=True)
def invoke(
    project: Project,
    plugin_type: str,
    dump: str,
    list_commands: bool,
    plugin_name: str,
    plugin_args: tuple[str, ...],
    containers: bool = False,
    print_var: str | None = None,
):
    """
    Invoke a plugin's executable with specified arguments.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#invoke
    """
    tracker = Tracker(project)
    legacy_tracker = LegacyTracker(project, context_overrides=tracker.contexts)
    # the `started` event is delayed until we've had a chance to try to resolve the requested plugin
    tracker.add_contexts(
        CliContext.from_command_and_kwargs(
            "invoke",
            None,
            plugin_type=plugin_type,
            dump=dump,
            list_commands=list_commands,
            containers=containers,
            print_var=print_var,
        )
    )

    try:
        plugin_name, command_name = plugin_name.split(":")
    except ValueError:
        command_name = None

    plugin_type = PluginType.from_cli_argument(plugin_type) if plugin_type else None

    _, Session = project_engine(project)  # noqa: N806
    session = Session()
    plugins_service = ProjectPluginsService(project)

    try:
        plugin = plugins_service.find_plugin(
            plugin_name, plugin_type=plugin_type, invokable=True
        )
        tracker.add_contexts(PluginsTrackingContext([(plugin, command_name)]))
        tracker.track_command_event(CliEvent.started)
    except PluginNotFoundError:
        # if the plugin is not found, we fire started and aborted tracking events together to keep tracking consistent
        tracker.track_command_event(CliEvent.started)
        tracker.track_command_event(CliEvent.aborted)
        raise

    if list_commands:
        do_list_commands(plugin)
        tracker.track_command_event(CliEvent.completed)
        return

    invoker = invoker_factory(project, plugin, plugins_service=plugins_service)
    try:
        exit_code = run_async(
            _invoke(
                invoker,
                project,
                plugin_name,
                plugin_args,
                session,
                dump,
                command_name,
                containers,
                print_var=print_var,
                legacy_tracker=legacy_tracker,
            )
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
    project: Project,
    plugin_name: str,
    plugin_args: str,
    session: sessionmaker,
    dump: str,
    command_name: str,
    containers: bool,
    print_var: list | None = None,
    legacy_tracker: LegacyTracker = None,
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

    legacy_tracker.track_meltano_invoke(
        plugin_name=plugin_name, plugin_args=" ".join(plugin_args)
    )

    return exit_code


def do_list_commands(plugin):
    """List the commands supported by plugin."""
    if not plugin.supported_commands:
        click.secho(
            f"Plugin '{plugin.name}' does not define any commands.", fg="yellow"
        )
        return

    descriptions = {
        f"{plugin.name}:{cmd}": props.description
        for cmd, props in plugin.all_commands.items()
    }
    column_len = max(len(name) for name in descriptions.keys()) + 2
    for name, desc in descriptions.items():
        click.secho(name.ljust(column_len, " "), fg="blue", nl=False)
        click.echo(desc)


async def dump_file(invoker: PluginInvoker, file_id: str):
    """Dump file."""
    try:
        content = await invoker.dump(file_id)
    except FileNotFoundError as err:
        raise CliError(f"Could not find {file_id}") from err
    except Exception as err:
        raise CliError(f"Could not dump {file_id}: {err}") from err
    print(content)  # noqa: WPS421
