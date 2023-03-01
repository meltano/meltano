"""Configuration for Meltano Cloud."""

from __future__ import annotations

import json
import os
from pathlib import Path

import platformdirs

_MELTANO_CLOUD_BASE_URL = "https://api.meltano.cloud/v1"
_MELTANO_CLOUD_BASE_AUTH_URL = "https://auth.meltano.cloud"
_MELTANO_CLOUD_RUNNERS_URL = "https://cloud-runners.meltano.com/v1"
_MELTANO_CLOUD_APP_CLIENT_ID = ""


class InvalidMeltanoCloudConfigError(Exception):
    """Raised when provided configuration is invalid."""


class MeltanoCloudConfigFileNotFoundError(Exception):
    """Raised when Meltano Cloud config file is missing."""


class MeltanoCloudConfig:  # noqa: WPS214 WPS230
    """Configuration for Meltano Cloud client."""

    env_var_prefix = "MELTANO_CLOUD_"
    config_file_search_path = (
        Path("./meltano_cloud.json"),
        Path(Path.home(), ".meltano_cloud.json"),
        Path(Path.home(), ".config", "meltano_cloud", "config.json"),
    )

    def __init__(
        self,
        auth_callback_port: int = 9999,
        base_url: str = _MELTANO_CLOUD_BASE_URL,
        base_auth_url: str = _MELTANO_CLOUD_BASE_AUTH_URL,
        app_client_id: str = _MELTANO_CLOUD_APP_CLIENT_ID,
        runner_api_url: str = _MELTANO_CLOUD_RUNNERS_URL,
        runner_api_key: str | None = None,
        runner_secret: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
        id_token: str | None = None,
        access_token: str | None = None,
        config_path: Path | None = None,
    ):
        """Initialize a MeltanoCloudConfig instance.

        Args:
            auth_callback_port: port to run auth callback server at.
            base_url: the base URL for Meltano API to interact with.
            base_auth_url: the base URL for the Meltano Auth API to authenticate with.
            app_client_id: the client ID to pass to oauth2 endpoints
            organization_id: the organization ID to use in API requests.
            project_id: the project ID to use in API requests.
            id_token: id token for use in authentication.
            access_token: access token for use in authentication.
            config_path: the path to the config file to use.
        """
        self.auth_callback_port = auth_callback_port
        self.base_url = base_url
        self.base_auth_url = base_auth_url
        self.app_client_id = app_client_id
        self.organization_id = organization_id
        self.project_id = project_id
        self.id_token = id_token
        self.runner_api_url = runner_api_url
        self.runner_api_key = runner_api_key
        self.runner_secret = runner_secret
        self.access_token = access_token
        self._config_path = config_path

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

    @staticmethod
    def find_config_path() -> Path:  # noqa: WPS605
        """Find the path to meltano config file.

        Returns:
            The path to the first meltano cloud config file found.
        """
        config_dir = Path(platformdirs.user_config_dir("meltano-cloud"))
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.json"

    @classmethod
    def from_config_file(cls, config_file: Path) -> MeltanoCloudConfig:
        """Initialize the configuration from a config file.

        Args:
            config_file: the path to the config file.

        Returns:
            A MeltanoCloudConfig
        """
        with open(config_file, encoding="utf-8") as config_f:
            config = json.load(config_f)
            return cls(**config)

    @classmethod
    def find(cls) -> MeltanoCloudConfig:
        """Initialize config from the first config file found.

        If no config file is found, one with default setting values
        is created in the user config directory.

        Returns:
            A MeltanoCloudConfig
        """
        try:
            return cls.from_config_file(cls.find_config_path())
        except FileNotFoundError:
            config = cls()
            config.write_to_file()
            return config

    def refresh(self) -> None:
        """Reread config from config file."""
        with open(self.config_path, encoding="utf-8") as config_f:
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
        with open(path_to_write, "w+", encoding="utf-8") as config:
            json.dump(config_to_write, config)
