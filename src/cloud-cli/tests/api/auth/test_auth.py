from __future__ import annotations

import typing as t
from http import HTTPStatus
from pathlib import Path

import pytest

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer


class TestMeltanoCloudAuth:
    """Test the Meltano Cloud API Authentication."""

    @pytest.fixture()
    def config(self, tmp_path: Path):
        path = tmp_path / "meltano-cloud.json"
        path.touch()
        return MeltanoCloudConfig(config_path=path)

    @pytest.fixture()
    def subject(
        self,
        monkeypatch: pytest.MonkeyPatch,
        config: MeltanoCloudConfig,
        httpserver_base_url: str,
    ):
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_CALLBACK_PORT", "8080")
        monkeypatch.setenv("MELTANO_CLOUD_BASE_AUTH_URL", httpserver_base_url)
        monkeypatch.setenv("MELTANO_CLOUD_APP_CLIENT_ID", "meltano-cloud-test")
        return MeltanoCloudAuth(config=config)

    def test_login_url(self, subject: MeltanoCloudAuth, httpserver_base_url: str):
        assert subject.login_url == (
            f"{httpserver_base_url}/oauth2/authorize?"  # noqa: WPS323
            "client_id=meltano-cloud-test&"
            "response_type=token&"
            "scope=email+openid+profile"
            "&redirect_uri=http%3A%2F%2Flocalhost%3A8080"
        )

    def test_get_auth_header(
        self,
        subject: MeltanoCloudAuth,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(subject.config, "id_token", "meltano-cloud-test")
        assert subject.get_auth_header() == {
            "Authorization": "Bearer meltano-cloud-test",
        }

    async def test_logged_in_success(
        self,
        subject: MeltanoCloudAuth,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(subject.config, "access_token", "meltano-cloud-test")
        monkeypatch.setattr(subject.config, "id_token", "meltano-cloud-test")
        assert await subject.logged_in() is True

    async def test_logged_in_no_tokens(
        self,
        subject: MeltanoCloudAuth,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(subject.config, "access_token", None)
        monkeypatch.setattr(subject.config, "id_token", None)
        assert await subject.logged_in() is False

    async def test_logged_in_fail(
        self,
        subject: MeltanoCloudAuth,
        monkeypatch: pytest.MonkeyPatch,
        httpserver: HTTPServer,
    ):
        monkeypatch.setattr(subject.config, "access_token", "meltano-cloud-test")
        monkeypatch.setattr(subject.config, "id_token", "meltano-cloud-test")
        httpserver.expect_oneshot_request("/oauth2/userInfo").respond_with_data(
            status=HTTPStatus.UNAUTHORIZED,
        )
        assert await subject.logged_in() is False
