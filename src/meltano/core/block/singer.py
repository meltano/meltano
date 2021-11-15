"""
SingerBlock wraps singer plugins to implement the IOBlock interface.
"""

import asyncio
from asyncio import StreamWriter, Task
from asyncio.subprocess import Process
from typing import Optional

from click import Tuple
from meltano.core.logging import capture_subprocess_output
from meltano.core.logging.utils import SubprocessOutputWriter
from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.runner import RunnerError

from .ioblock import ConsumerBlock, IOBlock, ProducerBlock


class SingerBlock(IOBlock):
    def __init__(self, plugin_invoker: PluginInvoker, plugin_args):
        self.outputs = []  # callback ?
        self.err_outputs = []
        self.invoker: PluginInvoker = plugin_invoker
        self.plugin_args: Tuple[str] = plugin_args
        self.command_name = None

        self.producer: bool = self.invoker.plugin.type == PluginType.EXTRACTORS
        self.consumer: bool = self.invoker.plugin.type == PluginType.LOADERS

        self._handle: Process = None
        self._process_future: Task = None
        self._stdout_future: Task = None
        self._stderr_future: Task = None

    async def start(self):
        try:
            self._handle = await self.invoker.invoke_async(
                *self.plugin_args,
                command=self.command_name,
                stdout=asyncio.subprocess.PIPE,  # Singer messages
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            raise RunnerError(f"Cannot start extractor: {err}") from err

    async def stop(self):
        """Stop (kill) the underlying process and cancel output proxying."""
        self._handle.kill()
        await self.process_future
        self.proxy_stdout.cancel()
        self.proxy_stderr.cancel()
        self.invoker.cleanup()

    def proxy_stdout(self) -> Task:
        if self._handle is None:
            raise Exception("No IO to proxy, process not running")

        if self._stdout_future is None:
            self._stdout_future = asyncio.ensure_future(
                # forward subproc stdout to downstream (i.e. targets stdin, loggers)
                capture_subprocess_output(self._handle.stdout, *self.outputs)
            )
        return self._stdout_future

    def proxy_stderr(self) -> Task:
        if self._handle is None:
            raise Exception("No IO to proxy, process not running")

        if self._stderr_future is None:
            self._stderr_future = asyncio.ensure_future(
                capture_subprocess_output(self._handle.stderr, *self.err_outputs)
            )
        return self._stderr_future

    def proxy_io(self) -> (Task, Task):
        """Start proxying stdout AND stderr to the respectively linked destinations.

        Returns: proxy_stdout Task and proxy_stderr Task
        """
        stdout = self.proxy_stdout()
        stderr = self.proxy_stderr()
        return stdout, stderr

    @property
    def process_future(self) -> Task:
        if self._process_future is None:
            if self._handle is None:
                raise Exception("No process to wait, process not running running")
            self._process_future = asyncio.ensure_future(self._handle.wait())
        return self._process_future

    @property
    def stdin(self) -> Optional[StreamWriter]:
        return self._handle.stdin

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

    async def pre(self, block_ctx) -> None:
        """Pre triggers preparation of the underlying plugin."""
        await self.invoker.prepare(block_ctx.get("session"))

    async def post(self) -> None:
        """Post triggers reseting the underlying plugin config."""
        await self.invoker.cleanup()


class SingerProducer(SingerBlock, ProducerBlock):
    """SingerProducer is just a place holder class right now. Not sure we'll actually need them.

    TODO: remove me?
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SingerConsumer(SingerBlock, ConsumerBlock):
    """SingerConsumer is just a place holder class right now. Not sure we'll actually need them.

    TODO: remove me?
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
