from __future__ import annotations

import base64
import hashlib
import socket
import threading
import typing as t
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from datetime import timezone as tz
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import pytest
import requests
import requests_mock as requests_mock_module

from meltano.core.cloud.auth import (
    CloudAuthService,
    _CallbackHTTPServer,
    generate_code_challenge,
    generate_code_verifier,
)
from meltano.core.cloud.config import CloudAuthConfig
from meltano.core.cloud.credentials import Credentials, CredentialsStore
from meltano.core.cloud.error import (
    CallbackServerError,
    CloudAuthenticationError,
    CloudNotAuthenticatedError,
)

if t.TYPE_CHECKING:
    from pathlib import Path

TOKEN_URL = "https://tenant.auth0.com/oauth/token"
REVOKE_URL = "https://tenant.auth0.com/oauth/revoke"
USER_INFO_URL = "https://tenant.auth0.com/userinfo"

TOKEN_RESPONSE = {
    "access_token": "new-access-token",
    "refresh_token": "new-refresh-token",
    "id_token": "new-id-token",
    "token_type": "Bearer",
    "expires_in": 86400,
    "scope": "openid profile email offline_access",
}


def free_port() -> int:
    """Find a port that is free at this moment."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class FakeBrowser:
    """Stands in for the user's browser during the login flow.

    Requests the authorization URL, then redirects back to the CLI's callback
    server with the given query parameters, the way Auth0 would.
    """

    def __init__(self, params: dict[str, str], *, echo_state: bool = True) -> None:
        self.params = params
        self.echo_state = echo_state
        self.authorize_url: str | None = None
        self.thread: threading.Thread | None = None

    def __call__(self, url: str) -> bool:
        self.authorize_url = url
        query = {key: value[0] for key, value in parse_qs(urlparse(url).query).items()}
        params = dict(self.params)
        if self.echo_state:
            params.setdefault("state", query["state"])

        callback = f"{query['redirect_uri']}?{urllib.parse.urlencode(params)}"
        self.thread = threading.Thread(target=self._visit, args=(callback,))
        self.thread.start()
        return True

    @staticmethod
    def _visit(url: str) -> None:
        try:
            with urllib.request.urlopen(url, timeout=10):
                pass
        except urllib.error.HTTPError as err:
            err.close()  # The callback server answers errors with a 400.

    def join(self) -> None:
        if self.thread is not None:
            self.thread.join(timeout=10)


@pytest.fixture
def config(tmp_path: Path) -> CloudAuthConfig:
    return CloudAuthConfig(
        domain="tenant.auth0.com",
        client_id="test-client-id",
        audience="https://api.example.com",
        callback_host="127.0.0.1",
        callback_ports=(free_port(),),
        login_link=None,
        login_timeout_seconds=10,
        credentials_path=tmp_path / "credentials.json",
    )


@pytest.fixture
def session() -> requests.Session:
    return requests.Session()


@pytest.fixture
def requests_mock(session: requests.Session) -> t.Iterator[requests_mock_module.Mocker]:
    with requests_mock_module.Mocker(session=session) as mocker:
        yield mocker


@pytest.fixture
def service(
    config: CloudAuthConfig,
    session: requests.Session,
) -> CloudAuthService:
    return CloudAuthService(
        config=config,
        store=CredentialsStore(config.credentials_path),
        session=session,
    )


class TestPKCE:
    def test_verifier_is_unique_and_long_enough(self) -> None:
        verifiers = {generate_code_verifier() for _ in range(10)}
        assert len(verifiers) == 10
        # RFC 7636 requires between 43 and 128 characters.
        assert all(43 <= len(verifier) <= 128 for verifier in verifiers)

    def test_challenge_matches_rfc_7636_example(self) -> None:
        # Appendix B of RFC 7636.
        verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        challenge = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
        assert generate_code_challenge(verifier) == challenge

    def test_challenge_is_unpadded_base64url_sha256(self) -> None:
        verifier = generate_code_verifier()
        expected = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest(),
        )
        assert generate_code_challenge(verifier) == expected.decode().rstrip("=")
        assert "=" not in generate_code_challenge(verifier)


class TestCallbackServer:
    def test_rejects_a_request_to_the_wrong_path(self) -> None:
        server = _CallbackHTTPServer(("127.0.0.1", 0), "/callback")
        port = server.server_address[1]
        thread = threading.Thread(target=server.handle_request)
        thread.start()
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/favicon.ico",
                    timeout=10,
                )
        finally:
            thread.join(timeout=10)
            server.server_close()

        assert exc_info.value.code == HTTPStatus.NOT_FOUND
        exc_info.value.close()
        assert server.result is None


class TestLogin:
    def test_login(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        credentials = service.login()
        browser.join()

        assert credentials.access_token == "new-access-token"
        assert credentials.refresh_token == "new-refresh-token"
        assert credentials.id_token == "new-id-token"
        # The session is persisted for later commands.
        assert CredentialsStore(service.config.credentials_path).get() == credentials

    def test_login_authorize_url(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        service.login()
        browser.join()

        query = {
            key: value[0]
            for key, value in parse_qs(urlparse(browser.authorize_url).query).items()
        }
        assert browser.authorize_url.startswith("https://tenant.auth0.com/authorize?")
        assert query["response_type"] == "code"
        assert query["code_challenge_method"] == "S256"
        assert query["client_id"] == "test-client-id"
        assert query["audience"] == "https://api.example.com"
        assert query["scope"] == "openid profile email offline_access"
        assert query["redirect_uri"].endswith("/callback")
        assert query["state"]
        assert query["code_challenge"]

    def test_login_exchanges_code_with_verifier(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        service.login()
        browser.join()

        body = parse_qs(requests_mock.last_request.text)
        authorize_query = parse_qs(urlparse(browser.authorize_url).query)
        assert body["grant_type"] == ["authorization_code"]
        assert body["code"] == ["auth-code"]
        assert body["client_id"] == ["test-client-id"]
        assert body["redirect_uri"] == authorize_query["redirect_uri"]
        # The verifier must hash to the challenge that was sent to Auth0.
        verifier = body["code_verifier"][0]
        assert generate_code_challenge(verifier) == authorize_query["code_challenge"][0]

    def test_login_reports_authorize_url(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)
        reported: list[tuple[str, bool]] = []

        def on_url(url: str, opened: bool) -> None:  # noqa: FBT001
            reported.append((url, opened))

        service.login(on_authorize_url=on_url)
        browser.join()

        assert reported == [(browser.authorize_url, True)]

    def test_login_without_browser(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)
        reported: list[tuple[str, bool]] = []

        def on_url(url: str, opened: bool) -> None:  # noqa: FBT001
            reported.append((url, opened))
            browser(url)  # The user opens the link themselves.

        service.login(open_browser=False, on_authorize_url=on_url)
        browser.join()

        assert reported[0][1] is False

    def test_login_rejects_mismatched_state(
        self,
        service: CloudAuthService,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        browser = FakeBrowser(
            {"code": "auth-code", "state": "forged"},
            echo_state=False,
        )
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        with pytest.raises(CloudAuthenticationError, match="did not match"):
            service.login()
        browser.join()

    def test_login_reports_auth0_error(
        self,
        service: CloudAuthService,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        browser = FakeBrowser(
            {
                "error": "access_denied",
                "error_description": "User did not consent",
            },
        )
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        with pytest.raises(CloudAuthenticationError, match="access_denied"):
            service.login()
        browser.join()

    def test_login_without_code(
        self,
        service: CloudAuthService,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        browser = FakeBrowser({})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        with pytest.raises(CloudAuthenticationError, match="did not include a code"):
            service.login()
        browser.join()

    def test_login_times_out(
        self,
        service: CloudAuthService,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service.config.login_timeout_seconds = 0.3
        monkeypatch.setattr("webbrowser.open_new_tab", lambda _url: True)

        with pytest.raises(CloudAuthenticationError, match="Timed out"):
            service.login()

    def test_login_reports_token_error(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(
            TOKEN_URL,
            status_code=403,
            json={"error": "invalid_grant", "error_description": "Bad code"},
        )
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        with pytest.raises(CloudAuthenticationError, match="Bad code"):
            service.login()
        browser.join()

    def test_login_fails_when_port_is_taken(
        self,
        service: CloudAuthService,
    ) -> None:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", service.config.callback_ports[0]))
            sock.listen(1)
            with pytest.raises(CallbackServerError, match="callback server"):
                service.login()

    def test_login_tries_each_configured_port(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        taken, free = service.config.callback_ports[0], free_port()
        service.config.callback_ports = (taken, free)
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        with socket.socket() as sock:
            sock.bind(("127.0.0.1", taken))
            sock.listen(1)
            service.login()
            browser.join()

        redirect_uri = parse_qs(urlparse(browser.authorize_url).query)["redirect_uri"]
        assert f":{free}/" in redirect_uri[0]


class TestSession:
    def test_get_credentials_when_logged_out(self, service: CloudAuthService) -> None:
        assert service.get_credentials() is None

    def test_require_credentials_when_logged_out(
        self,
        service: CloudAuthService,
    ) -> None:
        with pytest.raises(CloudNotAuthenticatedError, match="not logged in"):
            service.require_credentials()

    def test_require_credentials_when_logged_in(
        self,
        service: CloudAuthService,
    ) -> None:
        credentials = Credentials(
            access_token="at",
            expires_at=datetime.now(tz=tz.utc) + timedelta(hours=1),
        )
        service.store.set(credentials)
        assert service.require_credentials() == credentials

    def test_get_credentials_returns_valid_session(
        self,
        service: CloudAuthService,
    ) -> None:
        credentials = Credentials(
            access_token="at",
            expires_at=datetime.now(tz=tz.utc) + timedelta(hours=1),
        )
        service.store.set(credentials)
        assert service.get_credentials() == credentials

    def test_get_credentials_refreshes_expired_session(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        requests_mock.post(TOKEN_URL, json={**TOKEN_RESPONSE, "refresh_token": None})
        service.store.set(
            Credentials(
                access_token="old",
                refresh_token="rt",
                id_token="it",
                expires_at=datetime.now(tz=tz.utc) - timedelta(seconds=1),
            ),
        )

        credentials = service.get_credentials()

        assert credentials.access_token == "new-access-token"
        # Auth0 does not return a new refresh token unless rotation is enabled.
        assert credentials.refresh_token == "rt"
        assert parse_qs(requests_mock.last_request.text)["grant_type"] == [
            "refresh_token",
        ]
        # The refreshed session is persisted.
        assert CredentialsStore(service.config.credentials_path).get() == credentials

    def test_get_credentials_without_refresh(
        self,
        service: CloudAuthService,
    ) -> None:
        service.store.set(
            Credentials(
                access_token="old",
                refresh_token="rt",
                expires_at=datetime.now(tz=tz.utc) - timedelta(seconds=1),
            ),
        )
        assert service.get_credentials(refresh=False) is None

    def test_get_credentials_without_refresh_token(
        self,
        service: CloudAuthService,
    ) -> None:
        service.store.set(
            Credentials(
                access_token="old",
                expires_at=datetime.now(tz=tz.utc) - timedelta(seconds=1),
            ),
        )
        assert service.get_credentials() is None

    def test_get_credentials_when_refresh_fails(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        requests_mock.post(TOKEN_URL, status_code=401, json={"error": "invalid_grant"})
        service.store.set(
            Credentials(
                access_token="old",
                refresh_token="rt",
                expires_at=datetime.now(tz=tz.utc) - timedelta(seconds=1),
            ),
        )
        assert service.get_credentials() is None

    def test_refresh_without_refresh_token(self, service: CloudAuthService) -> None:
        with pytest.raises(CloudAuthenticationError, match="cannot be renewed"):
            service.refresh(Credentials(access_token="at"))

    def test_refresh_when_auth0_is_unreachable(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        requests_mock.post(TOKEN_URL, exc=requests.ConnectionError("refused"))
        with pytest.raises(CloudAuthenticationError, match="Unable to reach"):
            service.refresh(Credentials(access_token="at", refresh_token="rt"))

    def test_get_user_info(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        requests_mock.get(USER_INFO_URL, json={"email": "user@example.com"})
        credentials = Credentials(access_token="at")

        assert service.get_user_info(credentials)["email"] == "user@example.com"
        assert requests_mock.last_request.headers["Authorization"] == "Bearer at"

    def test_get_user_info_failure(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        requests_mock.get(USER_INFO_URL, status_code=401)
        with pytest.raises(CloudAuthenticationError, match="Unable to fetch"):
            service.get_user_info(Credentials(access_token="at"))


class TestLogout:
    def test_logout(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        requests_mock.post(REVOKE_URL, status_code=200)
        service.store.set(Credentials(access_token="at", refresh_token="rt"))

        assert service.logout() is True
        assert not service.config.credentials_path.exists()
        assert parse_qs(requests_mock.last_request.text)["token"] == ["rt"]

    def test_logout_when_logged_out(self, service: CloudAuthService) -> None:
        assert service.logout() is False

    def test_logout_without_revoking(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        service.store.set(Credentials(access_token="at", refresh_token="rt"))
        assert service.logout(revoke=False) is True
        assert not requests_mock.called

    def test_logout_when_revocation_fails(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        requests_mock.post(REVOKE_URL, exc=requests.ConnectionError("refused"))
        service.store.set(Credentials(access_token="at", refresh_token="rt"))

        # The local session is still cleared.
        assert service.logout() is True
        assert not service.config.credentials_path.exists()

    def test_browser_logout_url(self, service: CloudAuthService) -> None:
        assert service.browser_logout_url() == (
            "https://tenant.auth0.com/v2/logout?client_id=test-client-id"
        )


class TestMalformedTokenResponse:
    @pytest.mark.parametrize(
        "response",
        ({"json": {"token_type": "Bearer"}}, {"json": []}, {"text": "not json"}),
    )
    def test_refresh_rejects_response_without_token(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        response: dict[str, t.Any],
    ) -> None:
        requests_mock.post(TOKEN_URL, **response)
        with pytest.raises(CloudAuthenticationError):
            service.refresh(Credentials(access_token="at", refresh_token="rt"))

    def test_login_rejects_response_without_token(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(TOKEN_URL, json={"token_type": "Bearer"})
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        with pytest.raises(CloudAuthenticationError, match="no access token"):
            service.login()
        browser.join()


class TestConfidentialClient:
    """A confidential client authenticates with a secret as well as PKCE."""

    @pytest.fixture
    def service(self, service: CloudAuthService) -> CloudAuthService:
        service.config.client_secret = "test-client-secret"
        return service

    def test_login_sends_client_secret(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        service.login()
        browser.join()

        body = parse_qs(requests_mock.last_request.text)
        assert body["client_secret"] == ["test-client-secret"]
        # The code verifier is still sent: PKCE is not replaced by the secret.
        assert body["code_verifier"]

    def test_refresh_sends_client_secret(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        service.refresh(Credentials(access_token="at", refresh_token="rt"))
        assert parse_qs(requests_mock.last_request.text)["client_secret"] == [
            "test-client-secret",
        ]

    def test_revoke_sends_client_secret(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        requests_mock.post(REVOKE_URL, status_code=200)
        service.store.set(Credentials(access_token="at", refresh_token="rt"))
        service.logout()
        assert parse_qs(requests_mock.last_request.text)["client_secret"] == [
            "test-client-secret",
        ]

    def test_public_client_sends_no_secret(
        self,
        config: CloudAuthConfig,
        session: requests.Session,
        requests_mock: requests_mock_module.Mocker,
    ) -> None:
        # The default is a public client, which must not send a secret.
        assert config.client_secret is None
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        public = CloudAuthService(
            config=config,
            store=CredentialsStore(config.credentials_path),
            session=session,
        )
        public.refresh(Credentials(access_token="at", refresh_token="rt"))
        assert "client_secret" not in parse_qs(requests_mock.last_request.text)

    def test_secret_is_not_written_to_the_credentials_file(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)

        service.login()
        browser.join()

        assert "test-client-secret" not in service.config.credentials_path.read_text()


class TestLoginLink:
    def test_link_carries_only_the_per_login_parameters(
        self,
        service: CloudAuthService,
    ) -> None:
        service.config.login_link = "https://link.example.com/login"
        url = service._authorize_url(
            code_challenge="challenge",
            state="state",
            redirect_uri="http://127.0.0.1:9998/callback",
        )
        assert url.startswith("https://link.example.com/login?")
        assert parse_qs(urlparse(url).query) == {
            "code_challenge": ["challenge"],
            "state": ["state"],
            "redirect_uri": ["http://127.0.0.1:9998/callback"],
        }


class TestAudience:
    def _authorize_query(
        self,
        service: CloudAuthService,
        monkeypatch: pytest.MonkeyPatch,
    ) -> dict[str, str]:
        browser = FakeBrowser({"code": "auth-code"})
        monkeypatch.setattr("webbrowser.open_new_tab", browser)
        service.login()
        browser.join()
        return {
            key: value[0]
            for key, value in parse_qs(urlparse(browser.authorize_url).query).items()
        }

    def test_audience_is_sent_when_set(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        query = self._authorize_query(service, monkeypatch)
        assert query["audience"] == "https://api.example.com"

    @pytest.mark.parametrize("audience", ("", None))
    def test_audience_is_omitted_when_unset(
        self,
        service: CloudAuthService,
        requests_mock: requests_mock_module.Mocker,
        monkeypatch: pytest.MonkeyPatch,
        audience: str | None,
    ) -> None:
        # Logging in must not require an API to be registered with the
        # identity provider.
        service.config.audience = audience
        requests_mock.post(TOKEN_URL, json=TOKEN_RESPONSE)
        query = self._authorize_query(service, monkeypatch)
        assert "audience" not in query
