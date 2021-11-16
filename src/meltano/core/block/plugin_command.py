"""A "CommandBlock" pattern supporting Meltano plugin's command like `dbt:run`, `dbt:docs` or `dbt:test`."""
import asyncio

from meltano.core.logging.utils import SubprocessOutputWriter
from meltano.core.plugin_invoker import PluginInvoker

from .singer import InvokerBase

try:
    from typing import Protocol, Dict, Tuple, Optional  # noqa:  WPS433
except ImportError:
    from typing_extensions import Protocol  # noqa:  WPS433,WPS440


class PluginCommand(Protocol):
    """Basic PluginCommand interface specification."""

    name: str
    command: Optional[str]

    async def run(self) -> None:
        """Run the command."""
        ...


class InvokerCommand(InvokerBase):
    """A basic PluginCommmand interface implementation that supports running plugin commands."""

    def __init__(
        self,
        name: str,
        log: SubprocessOutputWriter,
        block_ctx: Dict,
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
            block_ctx=block_ctx, plugin_invoker=plugin_invoker, command=command
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
            self.stderr_ling(self._log)

            await asyncio.wait(
                self.proxy_io(),
                self.process_future,
                return_when=asyncio.ALL_COMPLETED,
            )

        exitcode = self.process_future.result()
        if exitcode:
            command = self.command or self.command_args[0]
            raise Exception(
                f"`{self.name} {command}` failed with exit code: {exitcode}"
            )
