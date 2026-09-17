from __future__ import annotations

import base64
import json
import typing as t
from datetime import datetime, timedelta
from datetime import timezone as tz
from unittest import mock

import pytest

from meltano.cli import cli
from meltano.core.cloud.auth import CloudAuthService
from meltano.core.cloud.config import CloudAuthConfig
from meltano.core.cloud.credentials import Credentials
from meltano.core.cloud.error import CloudAuthenticationError

if t.TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner


def id_token(claims: dict[str, t.Any]) -> str:
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"


@pytest.fixture(autouse=True)
def cloud_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Point the CLI at a throwaway session, away from the real one."""
    monkeypatch.setenv("MELTANO_CLOUD_CREDENTIALS_PATH", str(tmp_path / "creds.json"))
    monkeypatch.setenv("MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS", "[]")


@pytest.fixture
def credentials() -> Credentials:
    return Credentials(
        access_token="at",
        refresh_token="rt",
        id_token=id_token({"email": "user@example.com"}),
        expires_at=datetime.now(tz=tz.utc) + timedelta(hours=1),
    )


class TestCloudAuthLogin:
    def test_login(self, cli_runner: CliRunner, credentials: Credentials) -> None:
        with (
            mock.patch.object(CloudAuthService, "get_credentials", return_value=None),
            mock.patch.object(
                CloudAuthService,
                "login",
                return_value=credentials,
            ) as login,
        ):
            result = cli_runner.invoke(cli, ("cloud", "auth", "login"))

        assert result.exit_code == 0, result.output
        assert "Successfully logged in to Meltano Cloud as user@example.com" in (
            result.stdout
        )
        assert login.call_args.kwargs["open_browser"] is True

    def test_login_no_browser(
        self,
        cli_runner: CliRunner,
        credentials: Credentials,
    ) -> None:
        with (
            mock.patch.object(CloudAuthService, "get_credentials", return_value=None),
            mock.patch.object(
                CloudAuthService,
                "login",
                return_value=credentials,
            ) as login,
        ):
            result = cli_runner.invoke(cli, ("cloud", "auth", "login", "--no-browser"))

        assert result.exit_code == 0, result.output
        assert login.call_args.kwargs["open_browser"] is False

    def test_login_when_already_logged_in(
        self,
        cli_runner: CliRunner,
        credentials: Credentials,
    ) -> None:
        with (
            mock.patch.object(
                CloudAuthService,
                "get_credentials",
                return_value=credentials,
            ),
            mock.patch.object(CloudAuthService, "login") as login,
        ):
            result = cli_runner.invoke(cli, ("cloud", "auth", "login"))

        assert result.exit_code == 0, result.output
        assert "Already logged in to Meltano Cloud as user@example.com" in result.stdout
        login.assert_not_called()

    def test_login_force(
        self,
        cli_runner: CliRunner,
        credentials: Credentials,
    ) -> None:
        with (
            mock.patch.object(
                CloudAuthService,
                "get_credentials",
                return_value=credentials,
            ),
            mock.patch.object(
                CloudAuthService,
                "login",
                return_value=credentials,
            ) as login,
        ):
            result = cli_runner.invoke(cli, ("cloud", "auth", "login", "--force"))

        assert result.exit_code == 0, result.output
        login.assert_called_once()

    def test_login_failure_is_reported(self, cli_runner: CliRunner) -> None:
        error = CloudAuthenticationError("Timed out waiting for you to log in")
        with (
            mock.patch.object(CloudAuthService, "get_credentials", return_value=None),
            mock.patch.object(CloudAuthService, "login", side_effect=error),
        ):
            result = cli_runner.invoke(cli, ("cloud", "auth", "login"))

        # `meltano.cli.main` turns a MeltanoError into a printed CLI error.
        assert result.exit_code == 1
        assert "Timed out waiting for you to log in" in str(result.exception)


class TestCloudAuthLogout:
    def test_logout(self, cli_runner: CliRunner) -> None:
        with mock.patch.object(
            CloudAuthService,
            "logout",
            return_value=True,
        ) as logout:
            result = cli_runner.invoke(cli, ("cloud", "auth", "logout"))

        assert result.exit_code == 0, result.output
        assert "Successfully logged out of Meltano Cloud." in result.stdout
        logout.assert_called_once()

    def test_logout_when_logged_out(self, cli_runner: CliRunner) -> None:
        with mock.patch.object(CloudAuthService, "logout", return_value=False):
            result = cli_runner.invoke(cli, ("cloud", "auth", "logout"))

        assert result.exit_code == 0, result.output
        assert "Not logged in to Meltano Cloud." in result.stdout

    def test_logout_web(self, cli_runner: CliRunner) -> None:
        with (
            mock.patch.object(CloudAuthService, "logout", return_value=True),
            mock.patch("webbrowser.open_new_tab", return_value=True) as open_tab,
        ):
            result = cli_runner.invoke(cli, ("cloud", "auth", "logout", "--web"))

        assert result.exit_code == 0, result.output
        assert open_tab.call_args.args[0].startswith(
            CloudAuthConfig().logout_url,
        )

    def test_logout_web_without_browser(self, cli_runner: CliRunner) -> None:
        with (
            mock.patch.object(CloudAuthService, "logout", return_value=True),
            mock.patch("webbrowser.open_new_tab", return_value=False),
        ):
            result = cli_runner.invoke(cli, ("cloud", "auth", "logout", "--web"))

        assert result.exit_code == 0, result.output
        assert CloudAuthConfig().logout_url in result.stdout


class TestCloudAuthStatus:
    def test_status_when_logged_out(self, cli_runner: CliRunner) -> None:
        with mock.patch.object(CloudAuthService, "get_credentials", return_value=None):
            result = cli_runner.invoke(cli, ("cloud", "auth", "status"))

        assert result.exit_code == 1
        assert "Not logged in to Meltano Cloud." in result.stdout

    def test_status(self, cli_runner: CliRunner, credentials: Credentials) -> None:
        with (
            mock.patch.object(
                CloudAuthService,
                "get_credentials",
                return_value=credentials,
            ),
            mock.patch.object(
                CloudAuthService,
                "get_user_info",
                return_value={"email": "verified@example.com"},
            ) as user_info,
        ):
            result = cli_runner.invoke(cli, ("cloud", "auth", "status"))

        assert result.exit_code == 0, result.output
        assert "Logged in to Meltano Cloud as verified@example.com" in result.stdout
        assert credentials.expires_at.isoformat() in result.stdout
        user_info.assert_called_once()

    def test_status_offline(
        self,
        cli_runner: CliRunner,
        credentials: Credentials,
    ) -> None:
        with (
            mock.patch.object(
                CloudAuthService,
                "get_credentials",
                return_value=credentials,
            ),
            mock.patch.object(CloudAuthService, "get_user_info") as user_info,
        ):
            result = cli_runner.invoke(cli, ("cloud", "auth", "status", "--offline"))

        assert result.exit_code == 0, result.output
        # Falls back to the claims of the stored ID token.
        assert "Logged in to Meltano Cloud as user@example.com" in result.stdout
        user_info.assert_not_called()
