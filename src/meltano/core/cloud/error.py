"""Errors raised while authenticating with Meltano Cloud."""

from __future__ import annotations

from meltano.core.error import MeltanoError


class MeltanoCloudError(MeltanoError):
    """Base class for all Meltano Cloud errors."""


class CloudAuthenticationError(MeltanoCloudError):
    """Authentication with Meltano Cloud failed."""

    def __init__(self, reason: str, instruction: str | None = None) -> None:
        """Create a new exception.

        Args:
            reason: A short explanation of the failure.
            instruction: A short instruction on how to fix the failure.
        """
        super().__init__(
            reason,
            instruction or "Run 'meltano cloud auth login' to try again",
        )


class CloudNotAuthenticatedError(MeltanoCloudError):
    """No usable Meltano Cloud session is available."""

    def __init__(self) -> None:
        """Create a new exception."""
        super().__init__(
            "You are not logged in to Meltano Cloud",
            "Run 'meltano cloud auth login' to log in or register for Meltano Cloud",
        )


class CallbackServerError(MeltanoCloudError):
    """The local OAuth callback server could not be started."""

    def __init__(self, host: str, ports: tuple[int, ...]) -> None:
        """Create a new exception.

        Args:
            host: Host the callback server tried to bind to.
            ports: Ports the callback server tried to bind to.
        """
        port_list = " and ".join(str(port) for port in ports)
        plural = "s" if len(ports) > 1 else ""
        super().__init__(
            f"Unable to start the login callback server on {host}, because port"
            f"{plural} {port_list} {'are' if len(ports) > 1 else 'is'} in use",
            f"Free up {'one of those ports' if len(ports) > 1 else 'the port'} "
            "and run 'meltano cloud auth login' again",
        )
