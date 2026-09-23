"""Configuration for authenticating with Meltano Cloud."""

from __future__ import annotations

import os
import typing as t
from dataclasses import KW_ONLY, dataclass, field
from pathlib import Path
from urllib.parse import urljoin

import platformdirs

from meltano.core.user_config import get_user_config_service

# The Meltano Cloud API. It serves an index of the plugins that Meltano
# supports, maintains and tests, and the login asks Auth0 for a token that this
# same API accepts.
CLOUD_API_ROOT = "https://app.meltano.com/api"

# The identity provider is the one Meltano Cloud runs, so none of these are
# configurable: pointing the CLI elsewhere only makes a login that cannot
# succeed.
AUTH_DOMAIN = "identity.matatika.com"
AUTH_CLIENT_ID = "OxWCH8ianlswOoKQ8i9X1cBg6cZ4NuwG"

# Auth0 matches callback URLs exactly, so the login flow uses a fixed port
# rather than an ephemeral one. Both of these are registered for the Meltano
# CLI application; the second is tried when the first is already in use.
CALLBACK_HOST = "localhost"
CALLBACK_PORTS = (9999, 9998)
CALLBACK_PATH = "/callback"

# A short link to the authorization endpoint. It holds the authorization
# parameters that only the login uses. The CLI adds the client ID, which other
# requests also use, and the ones that can change on each login: the PKCE
# challenge, the state, and the redirect URI, which names the callback port
# that is free. The scopes that the link holds must include 'offline_access'
# for Auth0 to return a refresh token, and its audience must be the Meltano
# Cloud API. Change the link target when the domain above changes.
LOGIN_LINK = "https://link.meltano.com/login"

# How long to wait for the user to complete the login flow in their browser.
LOGIN_TIMEOUT_SECONDS = 300.0


@dataclass(slots=True)
class CloudAuthConfig:
    """Auth0 configuration for the Meltano Cloud login flow.

    Only the credentials path is resolved from the environment or the Meltano
    user configuration file. The rest describe the identity provider Meltano
    Cloud runs, and are fixed.
    """

    _: KW_ONLY
    domain: str = AUTH_DOMAIN
    client_id: str = AUTH_CLIENT_ID
    # Only set for a confidential client. A CLI is normally a public client,
    # which authenticates with PKCE alone and has no secret to keep.
    client_secret: str | None = None
    callback_host: str = CALLBACK_HOST
    callback_ports: tuple[int, ...] = CALLBACK_PORTS
    callback_path: str = CALLBACK_PATH
    login_link: str = LOGIN_LINK
    login_timeout_seconds: float = LOGIN_TIMEOUT_SECONDS
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
