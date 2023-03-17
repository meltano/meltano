"""Configuration for Meltano Cloud."""

from __future__ import annotations

import json
import os
import sys
import typing as t
from contextlib import suppress
from pathlib import Path

import jwt
import platformdirs

if sys.version_info <= (3, 8):
    from cached_property import cached_property
else:
    from functools import cached_property
MELTANO_CLOUD_BASE_URL = "https://internal.api.meltano.cloud/"
MELTANO_CLOUD_BASE_AUTH_URL = "https://auth.meltano.cloud"
MELTANO_CLOUD_APP_CLIENT_ID = "45rpn5ep3g4qjut8jd3s4iq872"

USER_RW_FILE_MODE = 0o600


class InvalidMeltanoCloudConfigError(Exception):
    """Raised when provided configuration is invalid."""


class MeltanoCloudConfigFileNotFoundError(Exception):
    """Raised when Meltano Cloud config file is missing."""


class MeltanoCloudTenantAmbiguityError(Exception):
    """Raised when currently logged in user belongs to multiple tenants."""


class NoMeltanoCloudTenantResourceKeyError(Exception):
    """Raised when currently logged in user does not belong to any tenants."""


class MeltanoCloudProjectAmbiguityError(Exception):
    """Raised when currently logged in user belongs to multiple projects."""


class NoMeltanoCloudProjectIDError(Exception):
    """Raised when currently logged in user does not have any projects."""


class MeltanoCloudConfig:  # noqa: WPS214 WPS230
    """Configuration for Meltano Cloud client."""

    env_var_prefix = "MELTANO_CLOUD_"

    def __init__(
        self,
        *,
        auth_callback_port: int = 9999,
        base_url: str = MELTANO_CLOUD_BASE_URL,
        base_auth_url: str = MELTANO_CLOUD_BASE_AUTH_URL,
        app_client_id: str = MELTANO_CLOUD_APP_CLIENT_ID,
        id_token: str | None = None,
        access_token: str | None = None,
        config_path: os.PathLike | str | None = None,
    ):
        """Initialize a MeltanoCloudConfig instance.

        The configuration file is by default stored in the `meltano-cloud`
        directory in the user's config directory. The directory can be
        overridden by setting the `MELTANO_CLOUD_CONFIG_DIR` environment
        variable.

        Args:
            auth_callback_port: Port to run auth callback server at.
            base_url: Base URL for Meltano API to interact with.
            base_auth_url: Base URL for the Meltano Auth API to authenticate with.
            app_client_id: Client ID for oauth2 endpoints.
            id_token: ID token for use in authentication.
            access_token: Access token for use in authentication.
            config_path: Path to the config file to use.
        """
        self.auth_callback_port = auth_callback_port
        self.base_url = base_url
        self.base_auth_url = base_auth_url
        self.app_client_id = app_client_id
        self.id_token = id_token
        self.access_token = access_token
        self.config_path = (
            Path(config_path).resolve() if config_path else self.user_config_path()
        )

    def __getattribute__(self, name: str) -> str | None:
        """Get config attribute.

        Args:
            name: name of the attribute to get

        Returns:
            the attribute value, using env var if set
        """
        return os.environ.get(
            f"{MeltanoCloudConfig.env_var_prefix}{name.upper()}",
        ) or super().__getattribute__(name)

    @staticmethod
    def decode_jwt(token: str) -> dict[str, t.Any]:
        """Decode a JWT without verifying.

        Args:
            token: the jwt to decode

        Returns:
            The decoded jwt.
        """
        return jwt.decode(token, options={"verify_signature": False})

    @cached_property
    def _trks_and_pids(self) -> t.List[str]:
        """Get tenant resource keys and project ids from id token.

        Returns:
            List of trks and pids in the form '<trk>::<jpid>`

        """
        with suppress(jwt.DecodeError):
            decoded = self.decode_jwt(self.id_token)  # type: ignore
            trks_and_pids = decoded.get("custom:trk_and_pid")
            if trks_and_pids:
                return [perm.strip() for perm in trks_and_pids.split(",")]
        return []

    @property
    def tenant_resource_keys(self) -> set[str]:
        """Get the tenant resource keys from the ID token.

        Returns:
            The tenant resource keys found in the ID token.

        """
        return {perm.split("::")[0] for perm in self._trks_and_pids}

    @property
    def internal_project_ids(self) -> set[str]:
        """Get the internal project IDs from the ID token.

        Returns:
            The internal project IDs found in the ID token.

        """
        return {perm.split("::")[1] for perm in self._trks_and_pids}

    @property
    def internal_project_id(self) -> str:
        """Get the internal project ID.

        Returns:
            Internal project ID.

        Raises:
            NoMeltanoCloudProjectIDError: when ID token includes no project IDs.
            MeltanoCloudProjectAmbiguityError: when ID token includes more
                than one project ID.
        """
        if len(self.internal_project_ids) > 1:
            raise MeltanoCloudProjectAmbiguityError(
                "Logged in Meltano user has multiple projects. Set MELTANO_CLOUD_INTERNAL_PROJECT_ID env var to select project."  # noqa: E501
            )
        try:
            return next(iter(self.internal_project_ids))
        except IndexError:
            raise NoMeltanoCloudProjectIDError(
                "Logged in Meltano user has no projects."
            )

    @property
    def tenant_resource_key(self) -> str:
        """Get the tenant resource key.

        Returns:
            The tenant resource key.

        Raises:
            NoMeltanoCloudTenantResourceKeyError: when ID token includes no
                tenant resource keys.
            MeltanoCloudTenantAmbiguityError: when ID token includes more
                than one tenant resource key.
        """
        if len(self.tenant_resource_keys) > 1:
            raise MeltanoCloudTenantAmbiguityError(
                "Logged in Meltano user has multiple tenant resource keys. Set MELTANO_CLOUD_TENANT_RESOURCE_KEY to select one."  # noqa: E501
            )
        try:
            return next(iter(self.tenant_resource_keys))
        except IndexError:
            raise NoMeltanoCloudTenantResourceKeyError(
                "Logged in Meltano user has no tenant resource keys. Reach out to Meltano support to be assigned a tenant resource key."  # noqa: E501
            )

    @staticmethod
    def user_config_path() -> Path:  # noqa: WPS605
        """Find the path to meltano config file.

        Returns:
            The path to the first meltano cloud config file found.
        """
        config_dir = Path(platformdirs.user_config_dir("meltano-cloud")).resolve()
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    @classmethod
    def from_config_file(cls, config_path: os.PathLike | str) -> MeltanoCloudConfig:
        """Initialize the configuration from a config file.

        Args:
            config_path: Path to the config file.

        Returns:
            A MeltanoCloudConfig
        """
        with Path(config_path).open(encoding="utf-8") as config_file:
            return cls(**json.load(config_file), config_path=config_path)

    def refresh(self) -> None:
        """Reread config from config file."""
        with Path(self.config_path).open(encoding="utf-8") as config_f:
            self.__dict__.update(json.load(config_f))

    def write_to_file(self, config_path: Path | None = None) -> None:
        """Persist this config to its config file.

        Args:
            config_path: Path to write config to. Uses self.config_path if not provided.
        """
        path_to_write = config_path or self.config_path
        config_to_write = {
            key: val
            for key, val in self.__dict__.items()
            if not key.startswith("_") and key != "config_path"
        }
        # Write the config file with the same permissions that an SSH private
        # key would typically have, since it contains secrets.
        with open(
            path_to_write,
            "w",
            opener=lambda path, flags: os.open(path, flags, USER_RW_FILE_MODE),
        ) as config:
            json.dump(config_to_write, config)
