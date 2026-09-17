from __future__ import annotations

import typing as t

from meltano.core.cloud.config import CloudAuthConfig

if t.TYPE_CHECKING:
    from pathlib import Path

    import pytest


class TestCloudAuthConfig:
    def test_defaults(self) -> None:
        config = CloudAuthConfig.from_env(data={})
        assert config.domain
        assert config.client_id
        assert config.audience
        assert config.scope == "openid profile email offline_access"
        assert config.callback_path == "/callback"

    def test_urls(self) -> None:
        config = CloudAuthConfig(domain="example.auth0.com")
        assert config.authorize_url == "https://example.auth0.com/authorize"
        assert config.token_url == "https://example.auth0.com/oauth/token"
        assert config.revoke_url == "https://example.auth0.com/oauth/revoke"
        assert config.user_info_url == "https://example.auth0.com/userinfo"
        assert config.logout_url == "https://example.auth0.com/v2/logout"

    def test_callback_ports_from_user_config(self) -> None:
        config = CloudAuthConfig.from_env(data={"callback_ports": "8080, 8081"})
        assert config.callback_ports == (8080, 8081)

    def test_callback_ports_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_CALLBACK_PORTS", "9100,9101")
        assert CloudAuthConfig.from_env(data={}).callback_ports == (9100, 9101)

    def test_credentials_path_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "creds.json"
        monkeypatch.setenv("MELTANO_CLOUD_CREDENTIALS_PATH", str(path))
        assert CloudAuthConfig.from_env(data={}).credentials_path == path.resolve()

    def test_identity_settings_are_not_configurable(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # The tenant is the one Meltano Cloud runs, so pointing the CLI
        # elsewhere only makes a login that cannot succeed.
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_DOMAIN", "elsewhere.auth0.com")
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_CLIENT_ID", "someone-else")
        config = CloudAuthConfig.from_env(data={"domain": "from-file.auth0.com"})
        assert config.domain != "elsewhere.auth0.com"
        assert config.client_id != "someone-else"
