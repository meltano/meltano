"""Configuration for authenticating with Meltano Cloud."""

from __future__ import annotations

import os
import typing as t
from dataclasses import KW_ONLY, dataclass, field
from pathlib import Path
from urllib.parse import urljoin

import platformdirs

from meltano.core.user_config import get_user_config_service

# The audience is the identifier of the Meltano API registered with the
# identity provider. Set it to an empty value to request no audience, which
# yields an access token that is only good for the /userinfo endpoint.
DEFAULT_AUTH_AUDIENCE = "https://app.meltano.com/api"

# NOTE: The domain and client ID are placeholders for the Meltano Cloud
# identity provider, and still need to be confirmed. Until they are, users must
# supply their own via the environment variables or user configuration keys
# documented below. An empty client ID makes `validate` report a clear error,
# rather than silently attempting a login against the wrong tenant.
DEFAULT_AUTH_DOMAIN = "identity.matatika.com"
DEFAULT_AUTH_CLIENT_ID = "OxWCH8ianlswOoKQ8i9X1cBg6cZ4NuwG"

# 'offline_access' is required for Auth0 to return a refresh token.
DEFAULT_AUTH_SCOPES = ("openid", "profile", "email", "offline_access")

# Auth0 requires an exact match for callback URLs, so the login flow uses a
# fixed port rather than an ephemeral one. Additional ports may be configured,
# but each one must be registered as an allowed callback URL in Auth0.
DEFAULT_CALLBACK_HOST = "localhost"
DEFAULT_CALLBACK_PORTS = (9999,)
DEFAULT_CALLBACK_PATH = "/callback"

# How long to wait for the user to complete the login flow in their browser.
DEFAULT_LOGIN_TIMEOUT_SECONDS = 300.0

ENV_VAR_PREFIX = "MELTANO_CLOUD_AUTH_"


def _env(name: str) -> str | None:
    """Read a setting from the environment.

    Args:
        name: The name of the setting, without the environment variable prefix.

    Returns:
        The value, which is an empty string when the variable is set but empty,
        or `None` when it is not set at all. Setting a variable to an empty
        value explicitly unsets that setting, rather than falling back to the
        default.
    """
    return os.environ.get(f"{ENV_VAR_PREFIX}{name.upper()}")


def _parse_ports(value: str) -> tuple[int, ...]:
    """Parse a comma-separated list of ports.

    Args:
        value: The comma-separated list of ports.

    Returns:
        The ports, in the order they were given.
    """
    return tuple(int(port.strip()) for port in value.split(",") if port.strip())


@dataclass(slots=True)
class CloudAuthConfig:
    """Auth0 configuration for the Meltano Cloud login flow.

    Values are resolved from, in order of precedence: the environment, the
    Meltano user configuration file, and the built-in defaults.
    """

    _: KW_ONLY
    domain: str = DEFAULT_AUTH_DOMAIN
    client_id: str = DEFAULT_AUTH_CLIENT_ID
    # Only set for a confidential client. A CLI is normally a public client,
    # which authenticates with PKCE alone and has no secret to keep.
    client_secret: str | None = None
    audience: str = DEFAULT_AUTH_AUDIENCE
    scopes: tuple[str, ...] = DEFAULT_AUTH_SCOPES
    callback_host: str = DEFAULT_CALLBACK_HOST
    callback_ports: tuple[int, ...] = DEFAULT_CALLBACK_PORTS
    callback_path: str = DEFAULT_CALLBACK_PATH
    login_timeout_seconds: float = DEFAULT_LOGIN_TIMEOUT_SECONDS
    credentials_path: Path = field(
        default_factory=lambda: (
            platformdirs.user_config_path("meltano") / "cloud" / "credentials.json"
        ),
    )

    @classmethod
    def from_env(cls, data: dict[str, t.Any] | None = None) -> CloudAuthConfig:
        """Create a configuration from the environment and user configuration.

        Args:
            data: The `cloud.auth` mapping from the user configuration file.
                Read from the user configuration file if not provided.

        Returns:
            The resolved configuration.
        """
        if data is None:
            cloud_config = get_user_config_service().config.cloud
            data = cloud_config.get("auth") or {}

        kwargs: dict[str, t.Any] = {}

        if ports := _env("callback_ports") or data.get("callback_ports"):
            kwargs["callback_ports"] = (
                _parse_ports(ports) if isinstance(ports, str) else tuple(ports)
            )

        if path := os.environ.get("MELTANO_CLOUD_CREDENTIALS_PATH") or data.get(
            "credentials_path",
        ):
            kwargs["credentials_path"] = Path(path).expanduser().resolve()

        return cls(**kwargs)

    @property
    def base_url(self) -> str:
        """The base URL of the Auth0 tenant."""
        return f"https://{self.domain}/"

    @property
    def authorize_url(self) -> str:
        """The Auth0 authorization endpoint."""
        return urljoin(self.base_url, "authorize")

    @property
    def token_url(self) -> str:
        """The Auth0 token endpoint."""
        return urljoin(self.base_url, "oauth/token")

    @property
    def revoke_url(self) -> str:
        """The Auth0 token revocation endpoint."""
        return urljoin(self.base_url, "oauth/revoke")

    @property
    def user_info_url(self) -> str:
        """The Auth0 user info endpoint."""
        return urljoin(self.base_url, "userinfo")

    @property
    def logout_url(self) -> str:
        """The Auth0 logout endpoint."""
        return urljoin(self.base_url, "v2/logout")

    @property
    def scope(self) -> str:
        """The requested OAuth scopes, as a space-separated string."""
        return " ".join(self.scopes)
