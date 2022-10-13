"""Base Error classes."""

from __future__ import annotations

from asyncio.streams import StreamReader
from asyncio.subprocess import Process
from enum import Enum
from typing import Any


class ExitCode(int, Enum):  # noqa: D101
    OK = 0
    FAIL = 1
    NO_RETRY = 2


class MeltanoError(Exception):
    """Base class for all user-facing errors."""

    def __init__(
        self,
        reason: str,
        instruction: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize a MeltanoError.

        Args:
            reason: A short explanation of the error.
            instruction: A short instruction on how to fix the error.
            args: Additional arguments to pass to the base exception class.
            kwargs: Keyword arguments to pass to the base exception class.
        """
        self.reason = reason
        self.instruction = instruction
        super().__init__(reason, instruction, *args, **kwargs)


class Error(Exception):
    """Base exception for ELT errors."""

    def exit_code(self):  # noqa: D102
        return ExitCode.FAIL


class ExtractError(Error):
    """Error in the extraction process, like API errors."""

    def exit_code(self):  # noqa: D102
        return ExitCode.NO_RETRY


class AsyncSubprocessError(Exception):
    """Happens when an async subprocess exits with a resultcode != 0."""

    def __init__(
        self,
        message: str,
        process: Process,
        stderr: str | None = None,
    ):  # noqa: DAR101
        """Initialize AsyncSubprocessError."""
        self.process = process
        self._stderr: str | StreamReader | None = stderr or process.stderr
        super().__init__(message)

    @property
    async def stderr(self) -> str | None:
        """Return the output of the process to stderr."""
        if not self._stderr:  # noqa: DAR201
            return None
        elif not isinstance(self._stderr, str):
            stream = await self._stderr.read()
            self._stderr = stream.decode("utf-8")

        return self._stderr


class PluginInstallError(Exception):
    """Exception for when a plugin fails to install."""


class PluginInstallWarning(Exception):
    """Exception for when a plugin optional optional step fails to install."""


class EmptyMeltanoFileException(Exception):
    """Exception for empty meltano.yml file."""


class MeltanoConfigurationError(MeltanoError):
    """Exception for when Meltano is inproperly configured."""
