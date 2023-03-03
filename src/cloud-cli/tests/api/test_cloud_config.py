from __future__ import annotations

import json
import os
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

    @pytest.fixture(scope="function")
    def config_dict(self):
        return {
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
        }

    @pytest.fixture(scope="function")
    def config_file(self, tmp_path: Path, config_dict: dict):
        with open(tmp_path / "meltano-cloud.json", "w+") as config_file:
            json.dump(
                config_dict,
                config_file,
            )
        return tmp_path / "meltano-cloud.json"

    @pytest.fixture(scope="function")
    def subject(self, config_file: Path):
        return MeltanoCloudConfig.from_config_file(config_file)

    def config_assertions(self, config: MeltanoCloudConfig, suffix: str = ""):
        assert config.auth_callback_port == 9999
        assert config.base_url == f"{_MELTANO_CLOUD_BASE_URL}{suffix}"
        assert config.base_auth_url == f"{_MELTANO_CLOUD_BASE_AUTH_URL}{suffix}"
        assert config.app_client_id == f"{_MELTANO_CLOUD_APP_CLIENT_ID}{suffix}"
        assert config.runner_api_url == f"{_MELTANO_CLOUD_RUNNERS_URL}{suffix}"
        assert config.runner_api_key == f"{self._val_prefix}api-key{suffix}"
        assert config.runner_secret == f"{self._val_prefix}runner-secret{suffix}"
        assert config.organization_id == f"{self._val_prefix}organization-id{suffix}"
        assert config.project_id == f"{self._val_prefix}project-id{suffix}"
        assert config.id_token == f"{self._val_prefix}id-token{suffix}"
        assert config.access_token == f"{self._val_prefix}access-token{suffix}"

    def test_from_config_file(self, config_file: Path):
        config = MeltanoCloudConfig.from_config_file(config_file)
        self.config_assertions(config)

    def test_env_var_override(
        self, monkeypatch: pytest.MonkeyPatch, subject: MeltanoCloudConfig
    ):
        self.config_assertions(subject)
        monkeypatch.setenv("MELTANO_CLOUD_PROJECT_ID", "project-id-from-env-var")
        monkeypatch.setenv("MELTANO_CLOUD_APP_CLIENT_ID", "app-client-id-from-env-var")
        assert subject.project_id == "project-id-from-env-var"
        assert subject.app_client_id == "app-client-id-from-env-var"

    def test_refresh(
        self, subject: MeltanoCloudConfig, config_file: Path, config_dict: dict
    ):
        self.config_assertions(subject)
        os.remove(config_file)
        with open(config_file, "w+") as _config_file:
            changed = {key: f"{val}-changed" for key, val in config_dict.items()}
            changed.update({"auth_callback_port": 9999})
            json.dump(
                changed,
                _config_file,
            )
        subject.refresh()
        self.config_assertions(subject, suffix="-changed")

    def test_write_to_file(
        self, monkeypatch: pytest.MonkeyPatch, subject: MeltanoCloudConfig
    ):
        self.config_assertions(subject)
        subject.organization_id = "organization-id-changed"
        subject.write_to_file()
        with open(subject.config_path) as _config_file:
            config = json.load(_config_file)
            assert config["organization_id"] == "organization-id-changed"
