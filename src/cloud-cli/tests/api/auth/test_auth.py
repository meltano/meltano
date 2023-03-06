from __future__ import annotations

import json
from pathlib import Path

import pytest
from aioresponses import aioresponses

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig


class TestMeltanoCloudAuth:
    """Test the Meltano Cloud API Authentication."""

    @pytest.fixture
    def config(self, tmp_path: Path):
        return MeltanoCloudConfig.find(config_path=tmp_path / "meltano-cloud.json")

    @pytest.fixture
    def subject(self, monkeypatch: pytest.MonkeyPatch, config: MeltanoCloudConfig):
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_CALLBACK_PORT", 8080)
        monkeypatch.setenv("MELTANO_CLOUD_BASE_AUTH_URL", "http://meltano-cloud-test")
        monkeypatch.setenv("MELTANO_CLOUD_APP_CLIENT_ID", "meltano-cloud-test")
        return MeltanoCloudAuth(config=config)

    def test_login_url(self, subject: MeltanoCloudAuth):
        assert (
            subject.login_url
            == f"http://meltano-cloud-test/oauth2/authorize?client_id=meltano-cloud-test&response_type=token&scope=email+openid+profile&redirect_uri=http%3A%2F%2Flocalhost%3A8080"
        )

    def test_get_auth_header(
        self, subject: MeltanoCloudAuth, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(subject.config, "access_token", "meltano-cloud-test")
        assert subject.get_auth_header() == {
            "Authorization": "Bearer meltano-cloud-test"
        }

    async def test_logged_in_success(
        self, subject: MeltanoCloudAuth, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(subject.config, "access_token", "meltano-cloud-test")
        monkeypatch.setattr(subject.config, "id_token", "meltano-cloud-test")
        with aioresponses() as m:
            m.get(
                "http://meltano-cloud-test/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            assert await subject.logged_in() is True

    async def test_logged_in_no_tokens(
        self, subject: MeltanoCloudAuth, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(subject.config, "access_token", None)
        monkeypatch.setattr(subject.config, "id_token", None)
        with aioresponses() as m:
            m.get(
                "http://meltano-cloud-test/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            assert await subject.logged_in() is False

    async def test_logged_in_fail(
        self, subject: MeltanoCloudAuth, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(subject.config, "access_token", "meltano-cloud-test")
        monkeypatch.setattr(subject.config, "id_token", "meltano-cloud-test")
        with aioresponses() as m:
            m.get(
                "http://meltano-cloud-test/oauth2/userInfo",
                status=401,
            )
            assert await subject.logged_in() is False
