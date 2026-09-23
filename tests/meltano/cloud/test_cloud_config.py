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
        # Both are registered as callback URLs, so the second is a real fallback.
        assert config.callback_ports == (9999, 9998)

    def test_urls(self) -> None:
        config = CloudAuthConfig(domain="example.auth0.com")
        assert config.authorize_url == "https://link.meltano.com/login"
        assert config.token_url == "https://example.auth0.com/oauth/token"
        assert config.revoke_url == "https://example.auth0.com/oauth/revoke"
        assert config.user_info_url == "https://example.auth0.com/userinfo"
        assert config.logout_url == "https://link.meltano.com/logout"

    def test_credentials_path_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "creds.json"
        monkeypatch.setenv("MELTANO_CLOUD_CREDENTIALS_PATH", str(path))
        assert CloudAuthConfig.from_env(data={}).credentials_path == path.resolve()

    def test_only_the_credentials_path_is_configurable(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Every other value describes the identity provider Meltano Cloud
        # runs, so pointing the CLI elsewhere only makes a login that cannot
        # succeed.
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_DOMAIN", "elsewhere.auth0.com")
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_CALLBACK_PORTS", "9100")
        config = CloudAuthConfig.from_env(data={"client_id": "someone-else"})
        assert config.domain != "elsewhere.auth0.com"
        assert config.callback_ports != (9100,)
        assert config.client_id != "someone-else"
