"""Base Error classes."""

from __future__ import annotations

from asyncio.streams import StreamReader
from asyncio.subprocess import Process
from enum import Enum


class ExitCode(int, Enum):
    OK = 0
    FAIL = 1
    NO_RETRY = 2


class Error(Exception):
    """Base exception for ELT errors."""

    def exit_code(self):
        return ExitCode.FAIL


class ExtractError(Error):
    """Error in the extraction process, like API errors."""

    def exit_code(self):
        return ExitCode.NO_RETRY


class AsyncSubprocessError(Exception):
    """Happens when an async subprocess exits with a resultcode != 0."""

    def __init__(
        self,
        message: str,
        process: Process,
        stderr: str | None = None,
    ):
        """Initialize AsyncSubprocessError."""
        self.process = process
        self._stderr: str | StreamReader | None = stderr or process.stderr
        super().__init__(message)

    @property
    async def stderr(self) -> str | None:
        """Return the output of the process to stderr."""
        if not self._stderr:
            return None
        elif not isinstance(self._stderr, str):
            stream = await self._stderr.read()
            self._stderr = stream.decode("utf-8")

        return self._stderr


class PluginInstallError(Exception):
    """Exception for when a plugin fails to install."""


class PluginInstallWarning(Exception):
    """Exception for when a plugin optional optional step fails to install."""
