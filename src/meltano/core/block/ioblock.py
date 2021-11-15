"""The actual IOBlock interface is one of the lower level blocks for use with various BlockSet implementations."""

from asyncio import StreamWriter, Task
from typing import Optional, Protocol

from meltano.core.logging.utils import SubprocessOutputWriter


class IOBlock(Protocol):
    """The IOBlock interface is a basic block that Consumes, Produces, or Consume and Produces (Transforms) output.

    Underlying implementation could be subprocess (ala Singer Plugins), or stream transformers, basically,
    any class that satisfies the IOBlock interface.
    """

    stdin: Optional[StreamWriter]
    consumer: bool  # TODO: do we really need dedicated Producer/Consumer/Transformer blocks?
    producer: bool

    def stdout_link(self, dst: SubprocessOutputWriter) -> None:
        """Use stdout_link to instruct block to link/write stdout content to dst."""
        ...

    def stderr_link(self, dst: SubprocessOutputWriter) -> None:
        """Use stderr_link to instruct block to link/write stderr content to dst."""
        ...

    async def start(self) -> None:
        """Start the block.

        Whatever that might entail (spanning a process, spinning up a async task that will handle transforms, etc
        """
        ...

    async def stop(self) -> None:
        """Stop a block."""
        ...

    def proxy_stdout(self) -> Task:
        """Start proxying stdout to the linked stdout destinations.

        Returns: Future of the proxy task.
        """
        ...

    def proxy_stderr(self) -> Task:
        """Start proxying stderr to the linked stderr destinations.

        Returns: Future of the proxy task.
        """
        ...

    def proxy_io(self) -> (Task, Task):
        """Start proxying stdout AND stderr to the linked destinations.

        Returns: proxy_stdout Task and proxy_stderr Task
        """
        stdout = self.proxy_stdout()
        stderr = self.proxy_stderr()
        return stdout, stderr

    async def pre(self, block_ctx: dict) -> None:
        """Execute pre-start tasks.

        TODO: block_ctx should get passed in as part of initialization.
        TODO: consider switching to context manager/decarator
        """
        ...

    async def post(self) -> None:
        """Execute post-stop tasks.

        TODO: consider switching to context manager/decarator
        """
        ...
