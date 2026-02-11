"""CLI command `meltano invoke`."""

from __future__ import annotations

import asyncio
import sys
import typing as t

import click
import structlog

from meltano.cli.params import (
    PluginTypeArg,
    get_install_options,
    pass_project,
)
from meltano.cli.utils import (
    CliEnvironmentBehavior,
    CliError,
    PartialInstrumentedCmd,
    propagate_stop_signals,
)
from meltano.core.db import project_engine
from meltano.core.error import AsyncSubprocessError
from meltano.core.logging.utils import capture_subprocess_output
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin_invoker import (
    UnknownCommandError,
    invoker_factory,
)
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from meltano.cli.params import InstallPlugins
    from meltano.core.plugin import PluginType
    from meltano.core.plugin_invoker import PluginInvoker
    from meltano.core.project import Project
    from meltano.core.tracking import Tracker

logger = structlog.stdlib.get_logger(__name__)

install, no_install, only_install = get_install_options(include_only_install=True)


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
    type=PluginTypeArg(),
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
@install
@no_install
@only_install
@click.pass_context
@pass_project(migrate=True)
@run_async
async def invoke(
    project: Project,
    ctx: click.Context,
    *,
    plugin_type: PluginType | None,
    dump: str,
    list_commands: bool,
    plugin_name: str,
    plugin_args: tuple[str, ...],
    install_plugins: InstallPlugins,
    containers: bool,
    print_var: tuple[str, ...],
) -> None:
    """Invoke a plugin's executable with specified arguments.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#invoke
    """  # noqa: D301
    tracker: Tracker = ctx.obj["tracker"]

    try:
        plugin_name, command_name = plugin_name.split(":")
    except ValueError:
        command_name = None

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
        reason=PluginInstallReason.AUTO,
    )

    invoker = invoker_factory(project, plugin)
    try:
        exit_code = await _invoke(
            invoker=invoker,
            plugin_args=plugin_args,
            session=session,
            dump=dump,
            command_name=command_name,
            containers=containers,
            print_var=print_var,
        )
    except Exception as invoke_err:
        tracker.track_command_event(CliEvent.failed)
        raise invoke_err  # noqa: TRY201

    if exit_code == 0:
        tracker.track_command_event(CliEvent.completed)
    else:
        tracker.track_command_event(CliEvent.failed)
    sys.exit(exit_code)


class _LogOutputHandler:
    """Output handler for parsing plugin logs in invoke command."""

    def __init__(self, logger, log_parser=None):  # noqa: ANN001, ANN204
        """Initialize the log output handler.

        Args:
            logger: Structured logger to write parsed logs to.
            log_parser: Name of the log parser to use for structured parsing.
        """
        self.logger = logger
        self.log_parser = log_parser
        from meltano.core.logging.parsers import get_parser_factory

        self._parser_factory = get_parser_factory()

    def writeline(self, line: str) -> None:
        """Write a line using structured logging if possible.

        Args:
            line: Log line to write.
        """
        line = line.rstrip()
        if not line:
            return

        # Try to parse the line if we have a parser configured
        if self.log_parser and (
            parsed_record := self._parser_factory.parse_line(
                line,
                self.log_parser,
            )
        ):
            # Log with parsed level and structured data
            extra = {**parsed_record.extra}
            if parsed_record.logger_name:
                extra["plugin_logger"] = parsed_record.logger_name

            self.logger.log(
                parsed_record.level,
                parsed_record.message,
                plugin_exception=parsed_record.exception,
                **extra,
            )
        else:
            # Fallback to simple logging
            self.logger.info(line)


async def _invoke(  # noqa: ANN202
    *,
    invoker: PluginInvoker,
    plugin_args: tuple[str, ...],
    session: Session,
    dump: str,
    command_name: str | None,
    containers: bool,
    print_var: tuple[str, ...],
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
            elif (
                containers
                and command_name is not None
                and command.container_spec is not None
            ):
                return await invoker.invoke_docker(
                    command_name,
                    *plugin_args,
                )
            else:
                # Capture stderr for log parsing
                handle = await invoker.invoke_async(
                    *plugin_args,
                    command=command_name,
                    stderr=asyncio.subprocess.PIPE,
                )

                # Get the log parser for structured logging
                log_parser = invoker.get_log_parser()

                # Set up stderr logger with log parsing
                stderr_logger = invoker.stderr_logger.bind(
                    stdio="stderr",
                    cmd_type="command",
                )

                # Create output handler for stderr
                stderr_out = _LogOutputHandler(stderr_logger, log_parser=log_parser)

                # Capture stderr output asynchronously
                stderr_future = asyncio.create_task(
                    capture_subprocess_output(handle.stderr, stderr_out),
                )

                with propagate_stop_signals(handle):
                    exit_code = await handle.wait()
                    # Wait for stderr capture to complete
                    await stderr_future

    except UnknownCommandError as err:
        raise click.BadArgumentUsage(str(err)) from err
    except AsyncSubprocessError as err:
        logger.error(await err.stderr)  # noqa: TRY400
        raise
    finally:
        session.close()

    return exit_code


def do_list_commands(plugin) -> None:  # noqa: ANN001
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


async def dump_file(invoker: PluginInvoker, file_id: str) -> None:
    """Dump file."""
    try:
        content = await invoker.dump(file_id)
    except FileNotFoundError as err:
        raise CliError(f"Could not find {file_id}") from err  # noqa: EM102, TRY003
    except Exception as err:
        raise CliError(f"Could not dump {file_id}: {err}") from err  # noqa: EM102, TRY003
    print(content)  # noqa: T201
