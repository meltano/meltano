"""Configuration for Meltano Cloud."""

from __future__ import annotations

import json
import os
import typing as t
from contextlib import suppress
from functools import cached_property
from pathlib import Path

import jwt
import platformdirs

from meltano.cloud.api.types import CloudConfigOrg, CloudConfigProject

MELTANO_CLOUD_BASE_URL = "https://internal.api.meltano.cloud/"
MELTANO_CLOUD_BASE_AUTH_URL = "https://auth.meltano.cloud"
MELTANO_CLOUD_APP_CLIENT_ID = "45rpn5ep3g4qjut8jd3s4iq872"

USER_RW_FILE_MODE = 0o600


class InvalidMeltanoCloudConfigError(Exception):
    """Provided configuration is invalid."""


class MeltanoCloudConfigFileNotFoundError(Exception):
    """Meltano Cloud config file is missing."""


class MeltanoCloudTenantAmbiguityError(Exception):
    """Logged in user has access to multiple tenants."""

    def __init__(self) -> None:
        """Initialize exception with message."""
        super().__init__(
            "Logged in Meltano user has multiple tenant resource keys. "
            "Set MELTANO_CLOUD_TENANT_RESOURCE_KEY to select one.",
        )


class NoMeltanoCloudTenantResourceKeyError(Exception):
    """Logged in user does not have access to any tenants."""

    def __init__(self) -> None:
        """Initialize exception with message."""
        super().__init__(
            "Logged in Meltano user has no tenant resource keys. "
            "Reach out to Meltano support to be assigned a tenant resource key.",
        )


class MeltanoCloudProjectAmbiguityError(Exception):
    """Logged in user has access to multiple projects."""

    def __init__(self) -> None:
        """Initialize exception with message."""
        super().__init__(
            "Logged in Meltano user has multiple projects. "
            "Set one as the default project using the "
            "`meltano cloud project use` command.",
        )


class NoMeltanoCloudProjectIDError(Exception):
    """Logged in user does not have any projects."""

    def __init__(self) -> None:
        """Initialize exception with message."""
        super().__init__(
            "No Meltano Cloud projects are available, or no project has been "
            "selected as the default. Set one as the default using the "
            "`meltano cloud project use` command.",
        )


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
        organizations_defaults: dict[str, CloudConfigOrg] | None = None,
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
            organizations_defaults: Default org settings.
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
        self.organizations_defaults = organizations_defaults

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
    def _trks_and_pids(self) -> list[str]:
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
        # NOTE: The ID 00000000000000000000000000 is used as a placeholder
        # within the Cognito custom attribute trk_and_pid, because the trk
        # part is the only significant part.
        ignore_ids = {"00000000000000000000000000"}
        return {perm.split("::")[1] for perm in self._trks_and_pids} - ignore_ids

    @property
    def internal_project_id(self) -> str:
        """Get the default Meltano Cloud project ID.

        Returns:
            The default Meltano Cloud project ID.

        Raises:
            NoMeltanoCloudProjectIDError: when ID token includes no project IDs.
            MeltanoCloudProjectAmbiguityError: when ID token includes more
                than one project ID.
        """
        org_default_project_id = self.internal_organization_default.get(
            "default_project_id",
        )
        if org_default_project_id:
            return org_default_project_id
        if len(self.internal_project_ids) > 1:
            raise MeltanoCloudProjectAmbiguityError
        try:
            pid = next(iter(self.internal_project_ids))
            self.internal_project_id = pid
            return pid
        except StopIteration:  # noqa: WPS329
            raise NoMeltanoCloudProjectIDError from None

    @internal_project_id.setter
    def internal_project_id(self, project_id: str) -> None:
        """Set the default Meltano Cloud project ID.

        Args:
            project_id: The Meltano Cloud project ID that should be used.
        """
        self.internal_organization_default["default_project_id"] = project_id
        self.write_to_file()

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
            raise MeltanoCloudTenantAmbiguityError
        try:
            return next(iter(self.tenant_resource_keys))
        except StopIteration:  # noqa: WPS329
            raise NoMeltanoCloudTenantResourceKeyError from None

    @property
    def internal_organization_default(self) -> CloudConfigOrg:
        """Get the current tenant resource key defaults for projects and deployments.

        Returns:
            The current tenant resource key default project and list of projects
        """
        if (
            self.organizations_defaults
            and self.tenant_resource_key in self.organizations_defaults
        ):
            return self.organizations_defaults[self.tenant_resource_key]

        new_org_defaults = CloudConfigOrg(default_project_id=None, projects_defaults={})

        self.internal_organization_default = new_org_defaults
        return new_org_defaults

    @internal_organization_default.setter
    def internal_organization_default(self, org_default: CloudConfigOrg) -> None:
        """Set the internal organization defaults and updates the config file.

        Args:
            org_default: the new default organization settings
        """
        if not self.organizations_defaults:
            self.organizations_defaults = {}

        self.organizations_defaults[self.tenant_resource_key] = org_default
        self.write_to_file()

    @property
    def internal_project_default(self) -> CloudConfigProject:
        """Get the current org projects default settings.

        Returns:
            The current project deployment defaults
        """
        org_default = self.internal_organization_default
        if self.internal_project_id in org_default["projects_defaults"]:
            return org_default["projects_defaults"][self.internal_project_id]

        new_project_config = CloudConfigProject(default_deployment_name=None)
        self.internal_project_default = new_project_config
        return new_project_config

    @internal_project_default.setter
    def internal_project_default(self, project_default: CloudConfigProject) -> None:
        """Set the current org projects default settings and update config file.

        Args:
            project_default: the new default project settings
        """
        org_default = self.internal_organization_default
        org_default["projects_defaults"][self.internal_project_id] = project_default
        self.internal_organization_default = org_default

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

        We gracefully handle the deprecation of previous config keys.

        Deprecated keys:
        - default_deployment_name
        - default_project_id

        Args:
            config_path: Path to the config file.

        Returns:
            A MeltanoCloudConfig
        """
        with Path(config_path).open(encoding="utf-8") as config_file:
            config_data = json.load(config_file)

            valid_keys = cls.__init__.__annotations__.keys()
            valid_config_data = {
                key: config_data[key] for key in valid_keys if key in config_data
            }
            return cls(**valid_config_data, config_path=config_path)

    @classmethod
    def find(cls, config_path: os.PathLike | str | None = None) -> MeltanoCloudConfig:
        """Initialize config from the first config file found.

        If no config file is found, one with default setting values
        is created in the user config directory.

        Args:
            config_path: the path to the config file to use, if any.

        Returns:
            A MeltanoCloudConfig
        """
        try:
            return cls.from_config_file(config_path or cls.user_config_path())
        except (FileNotFoundError, json.JSONDecodeError):
            config = cls()
            config.write_to_file()
            return config

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
            json.dump(config_to_write, config, indent=2)
