"""SingerBlock wraps singer plugins to implement the IOBlock interface."""

import asyncio
from asyncio import StreamWriter, Task
from asyncio.subprocess import Process
from typing import Dict, Optional, Tuple

from meltano.core.logging import capture_subprocess_output
from meltano.core.logging.utils import SubprocessOutputWriter
from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.runner import RunnerError

from .ioblock import IOBlock


class InvokerBase:  # noqa: WPS230
    """Base class for creating IOBlock's built on top of existing Meltano plugins."""

    def __init__(
        self,
        block_ctx,
        project: Project,
        plugins_service: ProjectPluginsService,
        plugin_invoker: PluginInvoker,
        command: Optional[str],
    ):
        """Configure and return a wrapped plugin invoker extendable for use as an IOBlock or PluginCommandBlock.

        Args:
            block_ctx: context that should be used for this instance to do things like obtaining project settings.
            project: that should be used to obtain the ProjectSettingsService.
            plugin_invoker: the actual plugin invoker.
            command: the optional command to invoke.
        """
        self.context = block_ctx
        self.project = project
        self.project_settings_service = ProjectSettingsService(
            self.project,
            config_service=plugins_service.config_service,
        )

        self.invoker: PluginInvoker = plugin_invoker
        self._command: Optional[str] = command

        self.outputs = []
        self.err_outputs = []

        self.process_handle: Process = None
        self._process_future: Task = None
        self._stdout_future: Task = None
        self._stderr_future: Task = None

    @property
    def command(self) -> Optional[str]:
        """Command is the specific plugin command to use when invoking the plugin (if any)."""
        return self._command

    @property
    def string_id(self) -> str:
        """Return a string identifier for this block."""
        return self.invoker.plugin.name

    async def start(self, *args, **kwargs):
        """Invoke the process asynchronously.

        Raises:
            RunnerError: If the plugin process can not start.
        """
        if self.command is None:
            raise RunnerError("No command to run")

        try:
            self.process_handle = await self.invoker.invoke_async(
                *args,
                command=self.command,
                **kwargs,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception as err:
            raise RunnerError(f"Cannot start plugin: {err}") from err

    async def stop(self, kill: bool = True):
        """Stop (kill) the underlying process and cancel output proxying.

        Args:
            kill: whether or not to send a SIGKILL. If false, a SIGTERM is sent.
        """
        if self.process_handle is None:
            return

        try:
            if kill:
                self.process_handle.kill()
            else:
                self.process_handle.terminate()
        except ProcessLookupError:
            # Process already stopped
            pass
        await self.process_future
        if self._stdout_future is not None:
            self._stdout_future.cancel()
        if self._stderr_future is not None:
            self._stderr_future.cancel()

    def proxy_stdout(self) -> Task:
        """Start proxying stdout to the linked stdout destinations.

        Raises:
            RunnerError: If the processes is not running and so - there is no IO to proxy.
        """
        if self.process_handle is None:
            raise RunnerError("No IO to proxy, process not running")

        if self._stdout_future is None:
            self._stdout_future = asyncio.ensure_future(
                # forward subproc stdout to downstream (i.e. targets stdin, loggers)
                capture_subprocess_output(self.process_handle.stdout, *self.outputs)
            )
        return self._stdout_future

    def proxy_stderr(self) -> Task:
        """Start proxying stderr to the linked stderr destinations.

        Raises:
            RunnerError: If the processes is not running and so - there is no IO to proxy.
        """
        if self.process_handle is None:
            raise Exception("No IO to proxy, process not running")

        if self._stderr_future is None:
            self._stderr_future = asyncio.ensure_future(
                capture_subprocess_output(self.process_handle.stderr, *self.err_outputs)
            )
        return self._stderr_future

    def proxy_io(self) -> Tuple[Task, Task]:
        """Start proxying stdout AND stderr to the respectively linked destinations.

        Raises:
            RunnerError: If the processes is not running and so - there is no IO to proxy.

        Returns: proxy_stdout Task and proxy_stderr Task
        """
        return self.proxy_stdout(), self.proxy_stderr()

    @property
    def process_future(self) -> Task:
        """Return the future of the underlying process wait() call."""
        if self._process_future is None:
            if self.process_handle is None:
                raise Exception("No process to wait, process not running running")
            self._process_future = asyncio.ensure_future(self.process_handle.wait())
        return self._process_future

    @property
    def stdin(self) -> Optional[StreamWriter]:
        """Return stdin of the underlying process."""
        if self.process_handle is None:
            return None
        return self.process_handle.stdin

    def stdout_link(self, dst: SubprocessOutputWriter):
        """Use stdout_link to instruct block to link/write stdout content to dst.

        Args:
            dst:  The destination stdout output should be written too.
        """
        if self._stdout_future is None:
            self.outputs.append(dst)
        else:
            raise Exception("IO capture already in flight")

    def stderr_link(self, dst: SubprocessOutputWriter):
        """Use stderr_link to instruct block to link/write stderr content to dst.

        Args:
            dst:  The destination stderr output should be written too.
        """
        if self._stderr_future is None:
            self.err_outputs.append(dst)
        else:
            raise Exception("IO capture already in flight")

    async def pre(self, context: Dict) -> None:
        """Pre triggers preparation of the underlying plugin."""
        await self.invoker.prepare(context.get("session"))

    async def post(self) -> None:
        """Post triggers resetting the underlying plugin config."""
        try:
            await self.invoker.cleanup()
        except FileNotFoundError:
            # TODO: should we preserve these on a failure ?
            # the invoker prepared context manager was able to clean up the configs
            pass


class SingerBlock(InvokerBase, IOBlock):
    """SingerBlock wraps singer plugins to implement the IOBlock interface."""

    def __init__(
        self,
        block_ctx: Dict,
        project: Project,
        plugins_service: ProjectPluginsService,
        plugin_invoker: PluginInvoker,
        plugin_args: Tuple[str],
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
            plugins_service=plugins_service,
            plugin_invoker=plugin_invoker,
            command=None,
        )
        self.plugin_args = plugin_args

    @property
    def producer(self) -> bool:
        """Whether or not this plugin is a producer.

        Currently if the underlying plugin is of type extractor, it is a producer.
        """
        return self.invoker.plugin.type == PluginType.EXTRACTORS

    @property
    def consumer(self) -> bool:
        """Whether or not this plugin is a consumer.

        Currently if the underlying plugin is of type loader, it is a consumer.
        """
        return self.invoker.plugin.type == PluginType.LOADERS

    async def start(self):
        """Start the SingerBlock by invoking the underlying plugin.

        Raises:
            RunnerError: If the plugin can not start.
        """
        stream_buffer_size = self.project_settings_service.get("elt.buffer_size")
        line_length_limit = stream_buffer_size // 2

        stdin = None
        if self.consumer:
            stdin = asyncio.subprocess.PIPE

        try:
            self.process_handle = await self.invoker.invoke_async(
                limit=line_length_limit,
                stdin=stdin,  # Singer messages
                stdout=asyncio.subprocess.PIPE,  # Singer state
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            raise RunnerError(f"Cannot start plugin {self.string_id}: {err}") from err

    async def stop(self, kill: bool = True):
        """Stop (kill) the underlying process and cancel output proxying.

        Args:
            kill: whether or not to send a SIGKILL. If false, a SIGTERM is sent.
        """
        if self.process_handle is None:
            return

        try:
            if kill:
                self.process_handle.kill()
            else:
                self.process_handle.terminate()
        except ProcessLookupError:
            # Process already stopped
            pass

        await self.process_future
        if self._stdout_future is not None:
            self._stdout_future.cancel()
        if self._stderr_future is not None:
            self._stderr_future.cancel()
        try:
            await self.invoker.cleanup()
        except FileNotFoundError:
            # the invoker prepared context manager was able to clean up the configs
            pass
