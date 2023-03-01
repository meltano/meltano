from __future__ import annotations

import json
from pathlib import Path

import pytest

from meltano.cloud.api.config import (
    _MELTANO_CLOUD_APP_CLIENT_ID,
    _MELTANO_CLOUD_BASE_AUTH_URL,
    _MELTANO_CLOUD_BASE_URL,
    _MELTANO_CLOUD_RUNNERS_URL,
    MeltanoCloudConfig,
)


class TestMeltanoCloudConfig:
    _val_prefix = "meltano-cloud-test-"

    @pytest.fixture
    def subject(self):
        return MeltanoCloudConfig()

    @pytest.fixture
    def config_file(self, tmp_path: Path):
        with open(tmp_path / "meltano-cloud.json", "w+") as config_file:
            json.dump(
                {
                    "auth_callback_port": 9999,
                    "base_url": _MELTANO_CLOUD_BASE_URL,
                    "base_auth_url": _MELTANO_CLOUD_BASE_AUTH_URL,
                    "app_client_id": _MELTANO_CLOUD_APP_CLIENT_ID,
                    "runner_api_url": _MELTANO_CLOUD_RUNNERS_URL,
                    "runner_api_key": f"{self._val_prefix}api-key",
                    "runner_secret": f"{self._val_prefix}runner-secret",
                    "organization_id": f"{self._val_prefix}organization-id",
                    "project_id": f"{self._val_prefix}project-id",
                    "id_token": f"{self._val_prefix}id-token",
                    "access_token": f"{self._val_prefix}access-token",
                },
                config_file,
            )
            return tmp_path / "meltano-cloud.json"

    def config_assertions(self, config: MeltanoCloudConfig):
        assert config.auth_callback_port == 9999
        assert config.base_url == _MELTANO_CLOUD_BASE_URL
        assert config.base_auth_url == _MELTANO_CLOUD_BASE_AUTH_URL
        assert config.app_client_id == _MELTANO_CLOUD_APP_CLIENT_ID
        assert config.runner_api_url == _MELTANO_CLOUD_RUNNERS_URL
        assert config.runner_api_key == f"{self._val_prefix}api-key"
        assert config.runner_secret == f"{self._val_prefix}runner-secret"
        assert config.organization_id == f"{self._val_prefix}organization-id"
        assert config.project_id == f"{self._val_prefix}project-id"
        assert config.id_token == f"{self._val_prefix}id-token"
        assert config.access_token == f"{self._val_prefix}access-token"

    def test_from_config_file(self, config_file: Path):
        config = MeltanoCloudConfig.from_config_file(config_file)
        self.config_assertions(config)

    def test_env_var_override(self, monkeypatch: pytest.MonkeyPatch, config_file: Path):
        config = MeltanoCloudConfig.from_config_file(config_file)
        self.config_assertions(config)
        monkeypatch.setenv("MELTANO_CLOUD_PROJECT_ID", "project-id-from-env-var")
        monkeypatch.setenv("MELTANO_CLOUD_APP_CLIENT_ID", "app-client-id-from-env-var")
        assert config.project_id == "project_id-from-env-var"
        assert config.app_client_id == "app-client-id-from-env-var"

    def test_refresh(self, subject: MeltanoCloudConfig):
        # TODO:
        NotImplemented

    def test_write_to_file(self, subject: MeltanoCloudConfig):
        # TODO:
        NotImplemented
