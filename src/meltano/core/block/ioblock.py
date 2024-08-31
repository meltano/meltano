"""A low-level block type for use with `BlockSet` implementations."""

from __future__ import annotations

import typing as t
from abc import ABCMeta, abstractmethod

if t.TYPE_CHECKING:
    from asyncio import StreamWriter, Task

    from meltano.core.logging.utils import SubprocessOutputWriter


class IOBlock(metaclass=ABCMeta):
    """A block that consumes, produces, or both (i.e. transforms) output.

    Underlying implementation could be subprocesses (e.g. Singer Plugins), or
    stream transformers, or any class that satisfies the `IOBlock` interface.
    """

    @property
    @abstractmethod
    def stdin(self) -> StreamWriter | None:
        """Get the `StreamWriter` that should be used for writes, if any.

        Raises:
            NotImplementedError

        Returns:
            StreamWriter
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def consumer(self) -> bool:
        """Indicate whether this block is a consumer and requires input."""
        raise NotImplementedError

    @property
    @abstractmethod
    def producer(self) -> bool:
        """Indicate whether this block is a producer of output."""
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

        Whatever that might entail (spwaning a process, spinning up a async
        task that will handle transforms, etc).

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    @abstractmethod
    async def stop(self, *, kill: bool = True) -> None:
        """Stop a block.

        Args:
            kill: Whether to send a SIGKILL. If false, a SIGTERM is sent.

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
