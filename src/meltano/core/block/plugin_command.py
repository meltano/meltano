"""A "CommandBlock" pattern supporting Meltano plugin's command like `dbt:run`, `dbt:docs` or `dbt:test`."""
import asyncio
from typing import Dict, List, Optional, Tuple

import structlog
from meltano.core.elt_context import PluginContext
from meltano.core.logging import OutputLogger
from meltano.core.logging.utils import SubprocessOutputWriter
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import PluginInvoker, invoker_factory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from sqlalchemy.orm import Session

from .singer import InvokerBase

try:
    from typing import Protocol, Dict, Tuple, Optional  # noqa:  WPS433
except ImportError:
    from typing_extensions import Protocol  # noqa:  WPS433,WPS440


logger = structlog.getLogger(__name__)


class PluginCommandBlock(Protocol):
    """Basic PluginCommand interface specification."""

    name: str
    command: Optional[str]

    async def run(self) -> None:
        """Run the command."""
        ...


class InvokerCommand(InvokerBase):
    """A basic PluginCommandBlock interface implementation that supports running plugin commands."""

    def __init__(
        self,
        name: str,
        log: SubprocessOutputWriter,
        block_ctx: Dict,
        project: Project,
        plugins_service: ProjectPluginsService,
        plugin_invoker: PluginInvoker,
        command: Optional[str],
        command_args: Tuple[str],
    ):
        """Configure and return a wrapped plugin invoker.

        Args:
            name: the name of the plugin/command.
            log: the OutputLogger instance to proxy output too.
            block_ctx: the block context.
            plugin_invoker: the plugin invoker.
            command: the command to invoke.
            command_args: any additional plugin args that should be used.
        """
        super().__init__(
            block_ctx=block_ctx,
            project=project,
            plugins_service=plugins_service,
            plugin_invoker=plugin_invoker,
            command=command,
        )
        self.name = name
        self.command = command
        self.command_args = command_args
        self._log = log

    async def run(self):
        """Invoke a command capturing and logging produced output.

        Raises:
            Exception if the command fails.
        """
        async with self.invoker.prepared(self.context.session):
            await self.start(self.command_args)

            self.stdout_link(self._log)
            self.stderr_link(self._log)

            await asyncio.wait(
                [*self.proxy_io(), self.process_future],
                return_when=asyncio.ALL_COMPLETED,
            )

        exitcode = self.process_future.result()
        if exitcode:
            command = self.command or self.command_args[0]
            raise Exception(
                f"`{self.name} {command}` failed with exit code: {exitcode}"
            )


def plugin_command_invoker(
    plugin: ProjectPlugin,
    project: Project,
    session: Session,
    command: Optional[str],
    command_args: Optional[List[str]] = None,
    run_dir: str = None,
) -> InvokerCommand:
    """
    Make an InvokerCommand from a plugin.

    Args:
        plugin: Plugin to make command from.
        project: Project to use.
        session: SQLAlchemy session to use.
        command: the command to invoke on the plugin i.e. `run` in dbt run.
        command_args: any additional command args that should be passed in during invocation.
        run_dir: Optional directory to run commands in.
    Returns:
        InvokerCommand
    """
    stderr_log = logger.bind(
        stdio="stderr",
        cmd_type="command",
    )
    output_logger = OutputLogger("run.log")
    invoker_log = output_logger.out(plugin.name, stderr_log)

    plugins_service = ProjectPluginsService(project)

    ctx = PluginContext(
        plugin=plugin,
        settings_service=PluginSettingsService(
            project,
            plugin,
            plugins_service=plugins_service,
        ),
        session=session,
    )

    invoker = invoker_factory(
        project,
        ctx.plugin,
        context=ctx,
        run_dir=run_dir,
        plugins_service=plugins_service,
        plugin_settings_service=ctx.settings_service,
    )
    return InvokerCommand(
        name=plugin.name,
        log=invoker_log,
        block_ctx=ctx,
        project=project,
        plugins_service=plugins_service,
        plugin_invoker=invoker,
        command=command,
        command_args=command_args,
    )
