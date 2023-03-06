from __future__ import annotations

import json
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from meltano.cloud.api.auth import callback_server
from meltano.cloud.api.config import MeltanoCloudConfig


class TestMeltanoCloudAuthCallbackServer:
    """Test the Meltano Cloud Auth Callback Server."""

    @pytest.fixture(scope="function")
    def config(self, tmp_path: Path):
        return MeltanoCloudConfig(config_path=tmp_path / "meltano-cloud.json")

    @pytest.fixture(scope="function")
    def subject(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        config: MeltanoCloudConfig,
    ):
        monkeypatch.setenv("MELTANO_CLOUD_CONFIG_PATH", str(config.config_path))
        return callback_server.APP

    @pytest.fixture
    def client(self, subject: Flask):
        return subject.test_client()

    def test_callback_page(self, client: FlaskClient):
        response = client.get("/")
        assert (
            b'<p id="start-message">Logging in to Meltano Cloud...</p>' in response.data
        )

    def test_handle_tokens(
        self, subject: Flask, client: FlaskClient, config: MeltanoCloudConfig
    ):
        response: TestResponse = client.get(
            "/tokens?id_token=meltano-cloud-testing&access_token=meltano-cloud-testing"
        )
        config.refresh()
        assert response.status_code == 204
        assert config.access_token == "meltano-cloud-testing"
        assert config.id_token == "meltano-cloud-testing"
        with open(config.config_path) as config_file:
            config_on_disk = json.load(config_file)
        assert config_on_disk["access_token"] == "meltano-cloud-testing"
        assert config_on_disk["id_token"] == "meltano-cloud-testing"

    def test_handle_logout(
        self, subject: Flask, client: FlaskClient, config: MeltanoCloudConfig
    ):
        config.access_token = "meltano-cloud-testing"
        config.id_token = "meltano-cloud-testing"
        config.write_to_file()
        response: TestResponse = client.get("/logout")
        assert response.status_code == 204
        config.refresh()
        assert config.id_token is None
        assert config.access_token is None
        with open(config.config_path) as config_file:
            config_on_disk = json.load(config_file)
        assert config_on_disk.get("access_token") is None
        assert config_on_disk.get("id_token") is None
