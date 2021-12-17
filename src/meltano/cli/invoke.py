import logging
import sys
from typing import Tuple

import click
from meltano.core.db import project_engine
from meltano.core.error import AsyncSubprocessError
from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import (
    PluginInvoker,
    UnknownCommandError,
    invoker_factory,
)
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import run_async

from . import cli
from .params import pass_project
from .utils import CliError, propagate_stop_signals

logger = logging.getLogger(__name__)


@cli.command(
    context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=False)
)
@click.option(
    "--plugin-type", type=click.Choice(PluginType.cli_arguments()), default=None
)
@click.option(
    "--dump",
    type=click.Choice(["catalog", "config"]),
    help="Dump content of generated file",
)
@click.option(
    "--list-commands",
    is_flag=True,
    help="List the commands supported by the plugin",
)
@click.argument("plugin_name", metavar="PLUGIN_NAME[:COMMAND_NAME]")
@click.argument("plugin_args", nargs=-1, type=click.UNPROCESSED)
@pass_project(migrate=True)
def invoke(
    project: Project,
    plugin_type: str,
    dump: str,
    list_commands: bool,
    plugin_name: str,
    plugin_args: Tuple[str, ...],
):
    """Invoke the plugin's executable with specified arguments."""
    try:
        plugin_name, command_name = plugin_name.split(":")
    except ValueError:
        command_name = None

    plugin_type = PluginType.from_cli_argument(plugin_type) if plugin_type else None

    _, Session = project_engine(project)
    session = Session()
    plugins_service = ProjectPluginsService(project)
    plugin = plugins_service.find_plugin(
        plugin_name, plugin_type=plugin_type, invokable=True
    )

    if list_commands:
        do_list_commands(plugin)
        return

    invoker = invoker_factory(project, plugin, plugins_service=plugins_service)
    exit_code = run_async(
        _invoke(invoker, project, plugin_name, plugin_args, session, dump, command_name)
    )
    sys.exit(exit_code)


async def _invoke(
    invoker, project, plugin_name, plugin_args, session, dump, command_name
):
    try:
        async with invoker.prepared(session):
            if dump:
                await dump_file(invoker, dump)
                exit_code = 0
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

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_invoke(
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
        print(content)
    except FileNotFoundError as err:
        raise CliError(f"Could not find {file_id}") from err
    except Exception as err:
        raise CliError(f"Could not dump {file_id}: {err}") from err
