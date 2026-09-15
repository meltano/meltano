from __future__ import annotations

import typing as t

import pytest

from meltano.core.cloud.config import CloudAuthConfig
from meltano.core.cloud.error import CloudAuthConfigurationError

if t.TYPE_CHECKING:
    from pathlib import Path


class TestCloudAuthConfig:
    def test_defaults(self) -> None:
        config = CloudAuthConfig.from_env(data={})
        assert config.domain
        assert config.scope == "openid profile email offline_access"
        assert config.callback_path == "/callback"

    def test_urls(self) -> None:
        config = CloudAuthConfig(domain="example.auth0.com")
        assert config.authorize_url == "https://example.auth0.com/authorize"
        assert config.token_url == "https://example.auth0.com/oauth/token"
        assert config.revoke_url == "https://example.auth0.com/oauth/revoke"
        assert config.user_info_url == "https://example.auth0.com/userinfo"
        assert config.logout_url == "https://example.auth0.com/v2/logout"

    @pytest.mark.parametrize(
        "domain",
        ("https://example.auth0.com", "example.auth0.com/", "http://example.auth0.com"),
    )
    def test_domain_is_normalized(self, domain: str) -> None:
        assert CloudAuthConfig(domain=domain).domain == "example.auth0.com"

    def test_callback_path_is_normalized(self) -> None:
        assert CloudAuthConfig(callback_path="cb").callback_path == "/cb"

    def test_from_user_config(self) -> None:
        config = CloudAuthConfig.from_env(
            data={
                "domain": "tenant.eu.auth0.com",
                "client_id": "from-file",
                "scopes": "openid email",
                "callback_ports": "8080, 8081",
                "timeout": "12.5",
            },
        )
        assert config.domain == "tenant.eu.auth0.com"
        assert config.client_id == "from-file"
        assert config.scopes == ("openid", "email")
        assert config.callback_ports == (8080, 8081)
        assert config.login_timeout_seconds == pytest.approx(12.5)

    def test_env_takes_precedence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_CLIENT_ID", "from-env")
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_DOMAIN", "env.auth0.com")
        config = CloudAuthConfig.from_env(
            data={"client_id": "from-file", "domain": "file.auth0.com"},
        )
        assert config.client_id == "from-env"
        assert config.domain == "env.auth0.com"

    def test_credentials_path_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "creds.json"
        monkeypatch.setenv("MELTANO_CLOUD_CREDENTIALS_PATH", str(path))
        assert CloudAuthConfig.from_env(data={}).credentials_path == path.resolve()

    def test_scopes_accept_a_list(self) -> None:
        config = CloudAuthConfig.from_env(data={"scopes": ["openid", "profile"]})
        assert config.scopes == ("openid", "profile")

    @pytest.mark.parametrize(
        ("kwargs", "setting"),
        (
            ({"client_id": ""}, "client_id"),
            ({"client_id": "abc", "domain": ""}, "domain"),
        ),
    )
    def test_validate_requires_settings(
        self,
        kwargs: dict[str, str],
        setting: str,
    ) -> None:
        config = CloudAuthConfig(**kwargs)
        with pytest.raises(CloudAuthConfigurationError, match=setting):
            config.validate()

    def test_validate_passes(self) -> None:
        CloudAuthConfig(client_id="abc", domain="example.auth0.com").validate()


class TestClientSecret:
    def test_no_secret_by_default(self) -> None:
        assert CloudAuthConfig.from_env(data={}).client_secret is None

    def test_secret_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_CLIENT_SECRET", "shh")
        assert CloudAuthConfig.from_env(data={}).client_secret == "shh"

    def test_secret_from_user_config(self) -> None:
        config = CloudAuthConfig.from_env(data={"client_secret": "shh"})
        assert config.client_secret == "shh"

    def test_validate_does_not_require_a_secret(self) -> None:
        # A public client authenticates with PKCE alone.
        CloudAuthConfig(client_id="abc", domain="example.auth0.com").validate()


class TestEmptyEnvVars:
    def test_empty_env_var_unsets_the_setting(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Setting a variable to an empty value must not fall back to the
        # default, so that the audience can be omitted entirely.
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_AUDIENCE", "")
        assert CloudAuthConfig.from_env(data={}).audience == ""

    def test_empty_env_var_overrides_the_user_config(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_AUDIENCE", "")
        config = CloudAuthConfig.from_env(data={"audience": "https://from-file"})
        assert config.audience == ""

    def test_unset_env_var_falls_back(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MELTANO_CLOUD_AUTH_AUDIENCE", raising=False)
        config = CloudAuthConfig.from_env(data={"audience": "https://from-file"})
        assert config.audience == "https://from-file"

    def test_empty_client_id_is_reported(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MELTANO_CLOUD_AUTH_CLIENT_ID", "")
        with pytest.raises(CloudAuthConfigurationError, match="client_id"):
            CloudAuthConfig.from_env(data={}).validate()
