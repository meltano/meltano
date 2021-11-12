from asyncio import StreamWriter, Task
from typing import Protocol

from meltano.core.logging.utils import SubprocessOutputWriter


class IOBlock(Protocol):
    """The IOBlock interface is a basic block that Consumes, Produces, or Consume and Produces (Transforms) output.

    Underlying implementation could be subprocess (ala Singer Plugins), or stream transformers, basically,
    any class that satisfies the IOBlock interface.
    """

    stdin: StreamWriter
    requires_input: bool  # TODO: do we really need dedicated Producer/Consumer/Transformer blocks?
    has_output: bool  # TODO: these two vars could become "is consumer" "is producer" vars?

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
        """Start proxying stderr to the linked stdout destinations.

        Returns: Future of the proxy task.
        """
        ...

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


class ProducerBlock(IOBlock):
    pass


class ConsumerBlock(IOBlock):
    pass


class TransformerBlock(IOBlock):
    pass
