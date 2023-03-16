"""Configuration for Meltano Cloud."""

from __future__ import annotations

import json
import os
from pathlib import Path

import platformdirs

MELTANO_CLOUD_BASE_URL = "https://internal.api.meltano.cloud/"
MELTANO_CLOUD_BASE_AUTH_URL = "https://auth.meltano.cloud"
# Runner settings will be deprecated when runner API moves to standard auth scheme.
MELTANO_CLOUD_RUNNERS_URL = "https://cloud-runners.meltano.com/v1"
MELTANO_CLOUD_APP_CLIENT_ID = "45rpn5ep3g4qjut8jd3s4iq872"

USER_RW_FILE_MODE = 0o600


class InvalidMeltanoCloudConfigError(Exception):
    """Raised when provided configuration is invalid."""


class MeltanoCloudConfigFileNotFoundError(Exception):
    """Raised when Meltano Cloud config file is missing."""


class MeltanoCloudConfig:  # noqa: WPS214 WPS230
    """Configuration for Meltano Cloud client."""

    env_var_prefix = "MELTANO_CLOUD_"

    def __init__(
        self,
        auth_callback_port: int = 9999,
        base_url: str = MELTANO_CLOUD_BASE_URL,
        base_auth_url: str = MELTANO_CLOUD_BASE_AUTH_URL,
        app_client_id: str = MELTANO_CLOUD_APP_CLIENT_ID,
        runner_api_url: str = MELTANO_CLOUD_RUNNERS_URL,
        runner_api_key: str | None = None,
        runner_secret: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
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
            runner_api_url: URL for meltano cloud runner API.
            runner_api_key: Key for meltano cloud runner API.
            runner_secret: Secret token for meltano cloud runner API.
            organization_id: Organization ID to use in API requests.
            project_id: Meltano Cloud project ID to use in API requests.
            id_token: ID token for use in authentication.
            access_token: Access token for use in authentication.
            config_path: Path to the config file to use.
        """
        self.auth_callback_port = auth_callback_port
        self.base_url = base_url
        self.base_auth_url = base_auth_url
        self.app_client_id = app_client_id
        self.organization_id = organization_id
        self.project_id = project_id
        self.id_token = id_token
        # Runner settings will be deprecated when runner API
        # moves to standard auth scheme.
        self.runner_api_url = runner_api_url
        self.runner_api_key = runner_api_key
        self.runner_secret = runner_secret

        self.access_token = access_token
        self._config_path = Path(config_path).resolve() if config_path else None

    def __getattribute__(self, name):
        """Get config attribute.

        Args:
            name: name of the attribute to get

        Returns:
            the attribute value, using env var if set
        """
        return os.environ.get(
            f"{MeltanoCloudConfig.env_var_prefix}{name.upper()}"
        ) or super().__getattribute__(name)

    @property
    def config_path(self) -> Path:
        """Path to meltano cloud config file.

        Returns:
            The path to the config file being used.
        """
        if not self._config_path:
            self._config_path = self.find_config_path()

        return self._config_path

    @classmethod
    def find_config_path(cls) -> Path:  # noqa: WPS605
        """Find the path to meltano config file.

        Returns:
            The path to the first meltano cloud config file found.
        """
        dir_name = os.environ.get(f"{cls.env_var_prefix}CONFIG_DIR", "meltano-cloud")
        config_dir = Path(platformdirs.user_config_dir(dir_name)).resolve()
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
            return cls.from_config_file(config_path or cls.find_config_path())
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
            key: val for key, val in self.__dict__.items() if not key.startswith("_")
        }
        # Write the config file with the same permissions that an SSH private
        # key would typically have, since it contains secrets.
        with open(
            path_to_write,
            "w",
            opener=lambda path, flags: os.open(path, flags, USER_RW_FILE_MODE),
        ) as config:
            json.dump(config_to_write, config)
