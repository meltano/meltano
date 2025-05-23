"""`SingerBlock` wraps singer plugins to implement the `IOBlock` interface."""

from __future__ import annotations

import asyncio
import typing as t
from contextlib import suppress

from meltano.core.block.ioblock import IOBlock
from meltano.core.logging import capture_subprocess_output
from meltano.core.plugin import PluginType
from meltano.core.runner import RunnerError

if t.TYPE_CHECKING:
    from asyncio.subprocess import Process
    from collections.abc import Sequence

    from meltano.core.elt_context import PluginContext
    from meltano.core.logging.utils import SubprocessOutputWriter
    from meltano.core.plugin_invoker import PluginInvoker
    from meltano.core.project import Project

PRODUCERS = (PluginType.EXTRACTORS, PluginType.MAPPERS)
CONSUMERS = (PluginType.LOADERS, PluginType.MAPPERS)


class IOLinkError(Exception):
    """Raised when an IO link is not possible."""


class ProcessNotRunningError(Exception):
    """Raised when a process is not running."""


class InvokerBase:
    """Base class for creating IOBlock's built on top of existing Meltano plugins."""

    def __init__(
        self,
        block_ctx: PluginContext,
        project: Project,
        plugin_invoker: PluginInvoker,
        command: str | None,
    ):
        """Init a wrapped plugin invoker for use as an IOBlock or PluginCommandBlock.

        Args:
            block_ctx: Context that should be used for this instance to do
                things like obtaining project settings.
            project: The Meltano project this `InvokerBase` is for.
            plugin_invoker: The actual plugin invoker.
            command: The optional command to invoke.
        """
        self.context = block_ctx
        self.project = project

        self.invoker: PluginInvoker = plugin_invoker
        self._command: str | None = command

        self.outputs: list[SubprocessOutputWriter] = []
        self.err_outputs: list[SubprocessOutputWriter] = []

        self._process_handle: Process | None = None
        self._process_future: asyncio.Task | None = None
        self._stdout_future: asyncio.Task | None = None
        self._stderr_future: asyncio.Task | None = None

    @property
    def process_handle(self) -> Process:
        """Get the process handle for the underlying plugin.

        Returns:
            The process handle for the underlying plugin.
        """
        if self._process_handle is None:
            msg = f"Process is not running for {self.string_id}"
            raise ProcessNotRunningError(msg)

        return self._process_handle

    @property
    def command(self) -> str | None:
        """Get the command to use when invoking the plugin.

        Returns:
            The command to use when invoking the plugin.
        """
        return self._command

    @property
    def string_id(self) -> str:
        """Return a string identifier for this block.

        Returns:
            A string identifier for this block.
        """
        return self.invoker.plugin.name

    @property
    def consumer(self) -> bool: ...  # type: ignore[empty-body]  # noqa: D102

    async def start(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Invoke the process asynchronously.

        Args:
            args: arguments to pass to the process invoker.
            kwargs: keyword arguments to pass to the process invoker.

        Raises:
            RunnerError: If the plugin process can not start.
        """
        try:
            self._process_handle = await self.invoker.invoke_async(
                *args,
                command=self.command,
                **kwargs,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception as err:
            raise RunnerError(f"Cannot start plugin: {err}") from err  # noqa: EM102

    async def stop(self, *, kill: bool = True) -> None:
        """Stop (kill) the underlying process and cancel output proxying.

        Args:
            kill: whether to send a SIGKILL. If false, a SIGTERM is sent.
        """
        with suppress(ProcessLookupError):
            if kill:
                self.process_handle.kill()
            else:
                self.process_handle.terminate()
        await self.process_future
        if self._stdout_future is not None:
            self._stdout_future.cancel()
        if self._stderr_future is not None:
            self._stderr_future.cancel()

    def proxy_stdout(self) -> asyncio.Task:
        """Start proxying stdout to the linked stdout destinations.

        Returns:
            The stdout proxy future.
        """
        if self._stdout_future is None:
            outputs = self._merge_outputs(self.invoker.StdioSource.STDOUT, self.outputs)
            self._stdout_future = asyncio.ensure_future(
                # forward subproc stdout to downstream (i.e. targets stdin, loggers)
                capture_subprocess_output(self.process_handle.stdout, *outputs),
            )
        return self._stdout_future

    def proxy_stderr(self) -> asyncio.Task:
        """Start proxying stderr to the linked stderr destinations.

        Returns:
            The stderr proxy future.
        """
        if self._stderr_future is None:
            err_outputs = self._merge_outputs(
                self.invoker.StdioSource.STDERR,
                self.err_outputs,
            )
            self._stderr_future = asyncio.ensure_future(
                capture_subprocess_output(self.process_handle.stderr, *err_outputs),
            )
        return self._stderr_future

    def proxy_io(self) -> tuple[asyncio.Task, asyncio.Task]:
        """Start proxying stdout AND stderr to the respectively linked destinations.

        Returns:
            proxy_stdout asyncio.Task and proxy_stderr asyncio.Task
        """
        return self.proxy_stdout(), self.proxy_stderr()

    @property
    def process_future(self) -> asyncio.Task:
        """Return the future of the underlying process wait() call.

        Returns:
            The future of the underlying process wait() calls.
        """
        if self._process_future is None:
            self._process_future = asyncio.ensure_future(self.process_handle.wait())
        return self._process_future

    @property
    def stdin(self) -> asyncio.StreamWriter | None:
        """Return stdin of the underlying process.

        Returns:
            The stdin of the underlying process.
        """
        return self.process_handle.stdin

    async def close_stdin(self) -> None:
        """Close the underlying process stdin if the block is a consumer."""
        if self.consumer and self.process_handle.stdin is not None:
            self.process_handle.stdin.close()
            await self.process_handle.stdin.wait_closed()

    def stdout_link(self, dst: SubprocessOutputWriter) -> None:
        """Use stdout_link to instruct block to link/write stdout content to dst.

        Args:
            dst:  The destination stdout output should be written too.

        Raises:
            IOLinkError: If the IO is already in flight.
        """
        if self._stdout_future is None:
            self.outputs.append(dst)
        else:
            raise IOLinkError("IO capture already in flight")  # noqa: EM101

    def stderr_link(self, dst: SubprocessOutputWriter) -> None:
        """Use stderr_link to instruct block to link/write stderr content to dst.

        Args:
            dst:  The destination stderr output should be written too.

        Raises:
            IOLinkError: If the IO is already in flight.
        """
        if self._stderr_future is None:
            self.err_outputs.append(dst)
        else:
            raise IOLinkError("IO capture already in flight")  # noqa: EM101

    async def pre(self, context) -> None:  # noqa: ANN001
        """Pre triggers preparation of the underlying plugin.

        Args:
            context: The context with which to update the invoker
        """
        self.invoker.context = context
        await self.invoker.prepare(context.session)

    async def post(self) -> None:
        """Post triggers resetting the underlying plugin config."""
        with suppress(FileNotFoundError):
            # TODO: should we preserve these on a failure?
            # The invoker prepared context manager was able to clean up the configs
            await self.invoker.cleanup()

    def _merge_outputs(
        self,
        source: str,
        outputs: list[SubprocessOutputWriter],
    ) -> list[SubprocessOutputWriter]:
        if not self.invoker.output_handlers:
            return outputs

        merged_outputs = self.invoker.output_handlers.get(source, [])
        merged_outputs.extend(outputs)
        return merged_outputs


class SingerBlock(InvokerBase, IOBlock):
    """SingerBlock wraps singer plugins to implement the IOBlock interface."""

    def __init__(
        self,
        block_ctx: PluginContext,
        project: Project,
        plugin_invoker: PluginInvoker,
        plugin_args: Sequence[str],
    ):
        """Configure and return a Singer plugin wrapped as an IOBlock.

        Args:
            block_ctx: the block context.
            project:  the project to use to obtain project settings.
            plugin_invoker: the plugin invoker.
            plugin_args: any additional plugin args that should be used.
        """
        super().__init__(
            block_ctx=block_ctx,
            project=project,
            plugin_invoker=plugin_invoker,
            command=None,
        )
        self.plugin_args = plugin_args

    @property
    def producer(self) -> bool:
        """Whether this plugin is a producer.

        Currently if the underlying plugin is of type extractor, it is a producer.

        Returns:
            True if the underlying plugin is a producer, False otherwise.
        """
        return self.invoker.plugin.type in PRODUCERS

    @property
    def consumer(self) -> bool:
        """Whether this plugin is a consumer.

        Currently if the underlying plugin is of type loader, it is a consumer.

        Returns:
            True if the plugin is a consumer, False otherwise.
        """
        return self.invoker.plugin.type in CONSUMERS

    @property
    def has_state(self) -> bool:
        """Whether this plugin has state.

        Returns:
            bool indicating whether this plugin has state
        """
        return "state" in self.invoker.capabilities

    async def start(self) -> None:
        """Start the SingerBlock by invoking the underlying plugin.

        Raises:
            RunnerError: If the plugin can not start.
        """
        stream_buffer_size = self.project.settings.get("elt.buffer_size")
        line_length_limit = stream_buffer_size // 2

        stdin = asyncio.subprocess.PIPE if self.consumer else None
        try:
            self._process_handle = await self.invoker.invoke_async(
                limit=line_length_limit,
                stdin=stdin,  # Singer messages
                stdout=asyncio.subprocess.PIPE,  # Singer state
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            raise RunnerError(f"Cannot start plugin {self.string_id}: {err}") from err  # noqa: EM102

    async def stop(self, *, kill: bool = True) -> None:
        """Stop (kill) the underlying process and cancel output proxying.

        Args:
            kill: Whether to send a SIGKILL. If false, a SIGTERM is sent.
        """
        with suppress(ProcessLookupError):
            if kill:
                self.process_handle.kill()
            else:
                self.process_handle.terminate()
        await self.process_future
        if self._stdout_future is not None:
            self._stdout_future.cancel()
        if self._stderr_future is not None:
            self._stderr_future.cancel()
        with suppress(FileNotFoundError):
            # the invoker prepared context manager was able to clean up the configs
            await self.invoker.cleanup()
