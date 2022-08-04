"""A `CommandBlock` pattern supporting Meltano plugin's command like `dbt:run`, `dbt:docs` or `dbt:test`."""

from __future__ import annotations

import asyncio
from abc import ABCMeta, abstractmethod

import structlog

from meltano.core.db import project_engine
from meltano.core.elt_context import PluginContext
from meltano.core.logging import OutputLogger
from meltano.core.logging.utils import SubprocessOutputWriter
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import PluginInvoker, invoker_factory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.runner import RunnerError

from .singer import InvokerBase

logger = structlog.getLogger(__name__)


class PluginCommandBlock(metaclass=ABCMeta):
    """Basic PluginCommand interface specification."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin command block.

        In the case of a singer plugin this would most likely be the name of the plugin.
        ex. `dbt:run` name = dbt , command = run
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def command(self) -> str | None:
        """Command is the specific plugin command to use when invoking the plugin (if any)."""
        raise NotImplementedError

    @abstractmethod
    async def run(self) -> None:
        """Run the command."""
        raise NotImplementedError


class InvokerCommand(InvokerBase, PluginCommandBlock):
    """A basic PluginCommandBlock interface implementation that supports running plugin commands."""

    def __init__(
        self,
        name: str,
        log: SubprocessOutputWriter,
        block_ctx: dict,
        project: Project,
        plugins_service: ProjectPluginsService,
        plugin_invoker: PluginInvoker,
        command: str | None,
        command_args: tuple[str],
    ):
        """Configure and return a wrapped plugin invoker.

        Args:
            name: the name of the plugin/command.
            log: the OutputLogger instance to proxy output too.
            block_ctx: the block context.
            project: the project instance.
            plugins_service: the project plugins service.
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
        self._name = name
        self._command = command
        self._command_args = command_args
        self._log = log

    @property
    def name(self) -> str:
        """Name is the underlying name of the plugin/command.

        Returns:
            The name str.
        """
        return self._name

    @property
    def command(self) -> str | None:
        """Command is the specific plugin command to use when invoking the plugin.

        Returns:
            The command str if any.
        """
        return self._command

    @property
    def command_args(self) -> str | None:
        """Command args are the specific plugin command args to use when invoking the plugin (if any).

        Returns:
            The command args if any.
        """
        return self._command_args

    async def _start(self):
        invoke_args = (self.command_args,) if self.command_args else ()
        await self.start(*invoke_args)

    async def run(self) -> None:
        """Invoke a command capturing and logging produced output.

        Raises:
            RunnerError: if the command fails.
        """
        try:  # noqa: WPS501
            async with self.invoker.prepared(self.context.session):
                await self._start()

                self.stdout_link(self._log)
                self.stderr_link(self._log)

                await asyncio.wait(
                    [*self.proxy_io(), self.process_future],
                    return_when=asyncio.ALL_COMPLETED,
                )
        finally:
            self.context.session.close()
        exitcode = self.process_future.result()
        if exitcode:
            command = self.command or self.command_args[0]
            raise RunnerError(
                f"`{self.name} {command}` failed with exit code: {exitcode}"
            )


def plugin_command_invoker(
    plugin: ProjectPlugin,
    project: Project,
    command: str | None,
    command_args: list[str] | None = None,
    run_dir: str = None,
) -> InvokerCommand:
    """
    Make an InvokerCommand from a plugin.

    Args:
        plugin: Plugin to make command from.
        project: Project to use.
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

    _, session_maker = project_engine(project)
    session = session_maker()

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
