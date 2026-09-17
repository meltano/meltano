"""Errors raised while authenticating with Meltano Cloud."""

from __future__ import annotations

from meltano.core.error import MeltanoError


class MeltanoCloudError(MeltanoError):
    """Base class for all Meltano Cloud errors."""


class CloudAuthConfigurationError(MeltanoCloudError):
    """The Meltano Cloud authentication configuration is incomplete."""

    def __init__(self, setting: str, env_var: str) -> None:
        """Create a new exception.

        Args:
            setting: Name of the missing setting.
            env_var: Environment variable that can be used to set it.
        """
        super().__init__(
            f"No Meltano Cloud {setting} is configured",
            f"Set the '{env_var}' environment variable, or the "
            f"'cloud.auth.{setting}' key in your Meltano user configuration file",
        )


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
        port_list = ", ".join(str(port) for port in ports)
        super().__init__(
            f"Unable to start the login callback server on {host} (tried port(s) "
            f"{port_list})",
            "Free up the port, or set 'MELTANO_CLOUD_AUTH_CALLBACK_PORTS' to a port "
            "that is registered as a callback URL for the Meltano Cloud application",
        )
