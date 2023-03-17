from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from meltano.cloud.api.config import (
    MELTANO_CLOUD_APP_CLIENT_ID,
    MELTANO_CLOUD_BASE_AUTH_URL,
    MELTANO_CLOUD_BASE_URL,
    MeltanoCloudConfig,
)


class TestMeltanoCloudConfig:
    _val_prefix = "meltano-cloud-test-"

    @pytest.fixture(scope="function")
    def config_dict(self):
        return {
            "auth_callback_port": 9999,
            "base_url": MELTANO_CLOUD_BASE_URL,
            "base_auth_url": MELTANO_CLOUD_BASE_AUTH_URL,
            "app_client_id": MELTANO_CLOUD_APP_CLIENT_ID,
            "organization_id": f"{self._val_prefix}organization-id",
            "project_id": f"{self._val_prefix}project-id",
            "id_token": f"{self._val_prefix}id-token",
            "access_token": f"{self._val_prefix}access-token",
        }

    @pytest.fixture(scope="function")
    def config_path(self, tmp_path: Path, config_dict: dict):
        config_file_path = tmp_path / "meltano-cloud.json"
        with Path(config_file_path).open("w") as config_file:
            json.dump(config_dict, config_file)
        return config_file_path

    @pytest.fixture(scope="function")
    def subject(self, config_path: Path):
        return MeltanoCloudConfig.from_config_file(config_path)

    def config_assertions(self, config: MeltanoCloudConfig, suffix: str = ""):
        assert config.auth_callback_port == 9999
        assert config.base_url == f"{MELTANO_CLOUD_BASE_URL}{suffix}"
        assert config.base_auth_url == f"{MELTANO_CLOUD_BASE_AUTH_URL}{suffix}"
        assert config.app_client_id == f"{MELTANO_CLOUD_APP_CLIENT_ID}{suffix}"
        assert config.organization_id == f"{self._val_prefix}organization-id{suffix}"
        assert config.project_id == f"{self._val_prefix}project-id{suffix}"
        assert config.id_token == f"{self._val_prefix}id-token{suffix}"
        assert config.access_token == f"{self._val_prefix}access-token{suffix}"

    def test_from_config_file(self, config_path: Path):
        config = MeltanoCloudConfig.from_config_file(config_path)
        self.config_assertions(config)

    def test_env_var_override(
        self,
        monkeypatch: pytest.MonkeyPatch,
        subject: MeltanoCloudConfig,
    ):
        self.config_assertions(subject)
        monkeypatch.setenv("MELTANO_CLOUD_PROJECT_ID", "project-id-from-env-var")
        monkeypatch.setenv("MELTANO_CLOUD_APP_CLIENT_ID", "app-client-id-from-env-var")
        assert subject.project_id == "project-id-from-env-var"
        assert subject.app_client_id == "app-client-id-from-env-var"

    def test_refresh(
        self,
        subject: MeltanoCloudConfig,
        config_path: Path,
        config_dict: dict,
    ):
        self.config_assertions(subject)
        os.remove(config_path)
        with Path(config_path).open("w") as config_file:
            changed = {key: f"{val}-changed" for key, val in config_dict.items()}
            changed["auth_callback_port"] = 9999
            json.dump(changed, config_file)
        subject.refresh()
        self.config_assertions(subject, suffix="-changed")

    def test_write_to_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        subject: MeltanoCloudConfig,
        config_path: Path,
    ):
        self.config_assertions(subject)
        subject.organization_id = "organization-id-changed"
        subject.write_to_file()
        with Path(subject.config_path).open() as config_file:
            config = json.load(config_file)
            assert config["organization_id"] == "organization-id-changed"
