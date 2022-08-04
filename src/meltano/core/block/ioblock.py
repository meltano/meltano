"""The actual `IOBlock` interface is one of the lower level blocks for use with various `BlockSet` implementations."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from asyncio import StreamWriter, Task

from meltano.core.logging.utils import SubprocessOutputWriter


class IOBlock(metaclass=ABCMeta):
    """The IOBlock interface is a basic block that Consumes, Produces, or Consume and Produces (Transforms) output.

    Underlying implementation could be subprocesses (ala Singer Plugins), or stream transformers, basically,
    any class that satisfies the IOBlock interface.
    """

    @property
    @abstractmethod
    def stdin(self) -> StreamWriter | None:
        """If a block requires input, return the StreamWriter that should be used for writes.

        Returns:
            StreamWriter
        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def consumer(self) -> bool:
        """Consumer indicates whether or not this block is a consumer and requires input."""
        raise NotImplementedError

    @property
    @abstractmethod
    def producer(self) -> bool:
        """Indicate whether or not this block is a producer of output."""
        raise NotImplementedError

    @property
    @abstractmethod
    def string_id(self) -> str:
        """Return a string identifier for this block."""
        raise NotImplementedError

    @property
    @abstractmethod
    def has_state(self) -> bool:
        """Indicate whether this block has persistent state between runs."""
        raise NotImplementedError

    @abstractmethod
    def stdout_link(self, dst: SubprocessOutputWriter) -> None:
        """Use stdout_link to instruct block to link/write stdout content to dst.

        Args:
            dst: SubprocessOutputWriter

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    @abstractmethod
    def stderr_link(self, dst: SubprocessOutputWriter) -> None:
        """Use stderr_link to instruct block to link/write stderr content to dst.

        Args:
            dst: SubprocessOutputWriter

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    @abstractmethod
    async def start(self) -> None:
        """Start the block.

        Whatever that might entail (spwaning a process, spinning up a async task that will handle transforms, etc)

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    @abstractmethod
    async def stop(self, kill: bool = True) -> None:
        """Stop a block.

        Args:
            kill: whether or not to send a SIGKILL. If false, a SIGTERM is sent.

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    @abstractmethod
    def proxy_stdout(self) -> Task:
        """Start proxying stdout to the linked stdout destinations.

        Returns: Future of the proxy task.
        """
        raise NotImplementedError

    @abstractmethod
    def proxy_stderr(self) -> Task:
        """Start proxying stderr to the linked stderr destinations.

        Returns: Future of the proxy task.
        """
        raise NotImplementedError

    @abstractmethod
    def proxy_io(self) -> tuple[Task, Task]:
        """Start proxying stdout AND stderr to the linked destinations.

        Returns:
            proxy_stdout Task and proxy_stderr Task
        """
        stdout = self.proxy_stdout()
        stderr = self.proxy_stderr()
        return stdout, stderr

    @abstractmethod
    async def pre(self, context: object) -> None:
        """Execute pre-start tasks.

        Args:
            context: invocation context to use for this execution.
        """

    @abstractmethod
    async def post(self) -> None:
        """Execute post-stop tasks."""

    @abstractmethod
    async def close_stdin(self) -> None:
        """Close the underlying stdin if the block is a consumer."""
