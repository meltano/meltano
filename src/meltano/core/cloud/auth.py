"""Authentication with Meltano Cloud.

Implements the OAuth 2.0 authorization code flow with PKCE (RFC 7636) against
Auth0, using a loopback redirect as described by RFC 8252 ("OAuth 2.0 for
Native Apps"). The browser is sent to the Auth0 Universal Login page, and the
resulting authorization code is caught by a short-lived HTTP server listening
on the loopback interface.
"""

from __future__ import annotations

import base64
import hashlib
import http.server
import secrets
import sys
import time
import typing as t
import webbrowser
from contextlib import contextmanager, suppress
from http import HTTPStatus
from urllib.parse import parse_qs, urlencode, urlparse

import requests
import structlog

from meltano.core.cloud.config import CloudAuthConfig
from meltano.core.cloud.credentials import Credentials, CredentialsStore
from meltano.core.cloud.error import (
    CallbackServerError,
    CloudAuthenticationError,
    CloudNotAuthenticatedError,
)

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from collections.abc import Callable, Iterator

logger = structlog.stdlib.get_logger(__name__)

# How long to wait between checks for the browser redirect.
POLL_INTERVAL_SECONDS = 0.2

# How long to wait for Auth0 to respond.
REQUEST_TIMEOUT_SECONDS = 30

SUCCESS_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Meltano Cloud</title>
    <style>
      body {
        background: #101010;
        color: #f5f5f5;
        font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        margin: 0;
        text-align: center;
      }
      h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
      p { color: #a0a0a0; }
    </style>
  </head>
  <body>
    <main>
      <h1>You are logged in to Meltano Cloud</h1>
      <p>You can close this tab and return to your terminal.</p>
    </main>
  </body>
</html>
"""

FAILURE_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Meltano Cloud</title>
  </head>
  <body>
    <main>
      <h1>Login failed</h1>
      <p>Return to your terminal for details.</p>
    </main>
  </body>
</html>
"""


def generate_code_verifier() -> str:
    """Generate a PKCE code verifier.

    Returns:
        A high-entropy cryptographic random string, as described by RFC 7636.
    """
    return secrets.token_urlsafe(64)


def generate_code_challenge(code_verifier: str) -> str:
    """Derive the S256 PKCE code challenge for a code verifier.

    Args:
        code_verifier: The code verifier to derive the challenge from.

    Returns:
        The base64url-encoded SHA-256 digest of the code verifier, without
        padding.
    """
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """Handles the browser redirect back from Auth0."""

    server: _CallbackHTTPServer

    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        """Capture the query parameters of the authorization response."""
        parsed = urlparse(self.path)
        if parsed.path != self.server.callback_path:
            self._respond(HTTPStatus.NOT_FOUND, "")
            return

        params = {
            key: values[0] for key, values in parse_qs(parsed.query).items() if values
        }
        self.server.result = params

        if "error" in params:
            self._respond(HTTPStatus.BAD_REQUEST, FAILURE_PAGE)
        else:
            self._respond(HTTPStatus.OK, SUCCESS_PAGE)

    def _respond(self, status: HTTPStatus, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(encoded)

    @override
    def log_message(self, format: str, *args: t.Any) -> None:
        """Send the request log to the Meltano logger instead of stderr.

        Args:
            format: The printf-style format string.
            args: The values to interpolate into the format string.
        """
        logger.debug("Login callback request", request=format % args)


class _CallbackHTTPServer(http.server.HTTPServer):
    """An HTTP server that captures a single authorization response."""

    def __init__(
        self,
        server_address: tuple[str, int],
        callback_path: str,
    ) -> None:
        """Create a new callback server.

        Args:
            server_address: The address to bind to.
            callback_path: The path Auth0 will redirect to.
        """
        super().__init__(server_address, _CallbackHandler)
        self.callback_path = callback_path
        self.result: dict[str, str] | None = None


class CloudAuthService:
    """Authenticates the Meltano CLI with Meltano Cloud."""

    def __init__(
        self,
        config: CloudAuthConfig | None = None,
        store: CredentialsStore | None = None,
        session: requests.Session | None = None,
    ) -> None:
        """Create a new authentication service.

        Args:
            config: The Auth0 configuration to use. Read from the environment
                and user configuration file if not provided.
            store: The credentials store to use. Defaults to the credentials
                file described by the configuration.
            session: The `requests` session to use for calls to Auth0.
        """
        self.config = config or CloudAuthConfig.from_env()
        self.store = store or CredentialsStore(self.config.credentials_path)
        self.session = session or requests.Session()

    def login(
        self,
        *,
        open_browser: bool = True,
        on_authorize_url: Callable[[str, bool], None] | None = None,
    ) -> Credentials:
        """Log in to Meltano Cloud.

        Directs the user to the Auth0 login page, waits for them to complete
        the login flow, then exchanges the resulting authorization code for a
        session, which is written to the credentials store.

        Args:
            open_browser: Whether to open the login page in a browser.
            on_authorize_url: Called with the login URL, and whether a browser
                was opened for it, so that the caller can tell the user how to
                complete the flow.

        Returns:
            The new credentials.

        Raises:
            CloudAuthenticationError: If the login flow did not complete.
        """
        code_verifier = generate_code_verifier()
        state = secrets.token_urlsafe(32)

        with self._callback_server() as server:
            redirect_uri = self._redirect_uri(server.server_address[1])
            login_url = self._authorize_url(
                code_challenge=generate_code_challenge(code_verifier),
                state=state,
                redirect_uri=redirect_uri,
            )
            opened = open_browser and webbrowser.open_new_tab(login_url)
            if on_authorize_url is not None:
                on_authorize_url(login_url, opened)
            params = self._wait_for_callback(server)

        if error := params.get("error"):
            description = params.get("error_description", "No description was given")
            reason = f"Meltano Cloud login failed: {error}"
            raise CloudAuthenticationError(reason, description)

        if not secrets.compare_digest(params.get("state", ""), state):
            reason = "The Meltano Cloud login response did not match the request"
            instruction = (
                "This can happen if more than one login is in progress at once. "
                "Run 'meltano cloud auth login' again"
            )
            raise CloudAuthenticationError(reason, instruction)

        if not (code := params.get("code")):
            reason = "The Meltano Cloud login response did not include a code"
            raise CloudAuthenticationError(reason)

        credentials = self._exchange_code(
            code=code,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,
        )
        self.store.set(credentials)
        return credentials

    def logout(self, *, revoke: bool = True) -> bool:
        """Log out of Meltano Cloud.

        Args:
            revoke: Whether to also revoke the refresh token with Auth0.

        Returns:
            Whether a session was ended.
        """
        credentials = self.store.get()
        if credentials is None:
            return False

        if revoke and credentials.refresh_token:
            self._revoke(credentials.refresh_token)

        self.store.clear()
        return True

    def browser_logout_url(self) -> str:
        """Get the URL that ends the Auth0 session in the user's browser.

        Returns:
            The Auth0 logout URL.
        """
        query = urlencode({"client_id": self.config.client_id})
        return f"{self.config.logout_url}?{query}"

    def get_credentials(self, *, refresh: bool = True) -> Credentials | None:
        """Get the stored credentials, refreshing them if needed.

        This is the entry point for other Meltano Cloud commands: it returns a
        session whose access token is ready to be used, or `None` if the user
        is not logged in.

        Args:
            refresh: Whether to refresh an expired access token.

        Returns:
            The credentials, or `None` if the user is not logged in.
        """
        credentials = self.store.get()
        if credentials is None:
            return None

        if not credentials.is_expired:
            return credentials

        if not refresh or not credentials.refresh_token:
            logger.debug("Meltano Cloud access token is expired and cannot be renewed")
            return None

        try:
            credentials = self.refresh(credentials)
        except CloudAuthenticationError as err:
            logger.debug("Unable to refresh Meltano Cloud session", error=str(err))
            return None

        return credentials

    def require_credentials(self) -> Credentials:
        """Get the stored credentials, refreshing them if needed.

        Returns:
            The credentials.

        Raises:
            CloudNotAuthenticatedError: If the user is not logged in.
        """
        if credentials := self.get_credentials():
            return credentials
        raise CloudNotAuthenticatedError

    def refresh(self, credentials: Credentials) -> Credentials:
        """Renew an access token using a refresh token.

        Args:
            credentials: The credentials to refresh.

        Returns:
            The refreshed credentials, which have been written to the store.

        Raises:
            CloudAuthenticationError: If the session could not be refreshed.
        """
        if not credentials.refresh_token:
            reason = "The Meltano Cloud session cannot be renewed"
            raise CloudAuthenticationError(reason)

        data = self._token_request(
            {
                "grant_type": "refresh_token",
                "client_id": self.config.client_id,
                "refresh_token": credentials.refresh_token,
            },
        )
        refreshed = credentials.with_token_response(data)
        self.store.set(refreshed)
        return refreshed

    def get_user_info(self, credentials: Credentials) -> dict[str, t.Any]:
        """Get the profile of the logged in user from Auth0.

        Args:
            credentials: The credentials to authenticate with.

        Returns:
            The user profile.

        Raises:
            CloudAuthenticationError: If the profile could not be fetched.
        """
        try:
            response = self.session.get(
                self.config.user_info_url,
                headers=credentials.auth_header,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            reason = f"Unable to fetch your Meltano Cloud profile: {err}"
            raise CloudAuthenticationError(reason) from err

    def _authorize_url(
        self,
        *,
        code_challenge: str,
        state: str,
        redirect_uri: str,
    ) -> str:
        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "redirect_uri": redirect_uri,
            "scope": self.config.scope,
            "state": state,
        }
        if self.config.audience:
            # Without an audience, Auth0 issues an opaque access token for the
            # /userinfo endpoint only, which is all the login flow itself needs.
            params["audience"] = self.config.audience

        return f"{self.config.authorize_url}?{urlencode(params)}"

    def _redirect_uri(self, port: int) -> str:
        return f"http://{self.config.callback_host}:{port}{self.config.callback_path}"

    @contextmanager
    def _callback_server(self) -> Iterator[_CallbackHTTPServer]:
        """Run the loopback server that catches the Auth0 redirect.

        Yields:
            The running callback server.

        Raises:
            CallbackServerError: If no configured port could be bound.
        """
        server: _CallbackHTTPServer | None = None
        for port in self.config.callback_ports:
            try:
                server = _CallbackHTTPServer(
                    ("127.0.0.1", port),
                    self.config.callback_path,
                )
            except OSError as err:  # noqa: PERF203
                logger.debug(
                    "Unable to bind login callback server",
                    port=port,
                    error=str(err),
                )
            else:
                break

        if server is None:
            raise CallbackServerError(
                self.config.callback_host,
                self.config.callback_ports,
            )

        try:
            yield server
        finally:
            server.server_close()

    def _wait_for_callback(self, server: _CallbackHTTPServer) -> dict[str, str]:
        """Serve requests until Auth0 redirects back, or the wait times out.

        Args:
            server: The running callback server.

        Returns:
            The query parameters of the authorization response.

        Raises:
            CloudAuthenticationError: If the login flow timed out.
        """
        server.timeout = POLL_INTERVAL_SECONDS
        deadline = time.monotonic() + self.config.login_timeout_seconds

        while server.result is None:
            if time.monotonic() >= deadline:
                reason = "Timed out waiting for you to log in to Meltano Cloud"
                instruction = "Run 'meltano cloud auth login' to try again"
                raise CloudAuthenticationError(reason, instruction)
            server.handle_request()

        return server.result

    def _exchange_code(
        self,
        *,
        code: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> Credentials:
        data = self._token_request(
            {
                "grant_type": "authorization_code",
                "client_id": self.config.client_id,
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": redirect_uri,
            },
        )
        return Credentials.from_token_response(data)

    def _token_request(self, payload: dict[str, str]) -> dict[str, t.Any]:
        """Call the Auth0 token endpoint.

        Args:
            payload: The form body to send.

        Returns:
            The decoded response.

        Raises:
            CloudAuthenticationError: If the request failed.
        """
        if self.config.client_secret:
            # Auth0 requires client authentication for a confidential client,
            # in addition to the PKCE code verifier.
            payload = {**payload, "client_secret": self.config.client_secret}

        try:
            response = self.session.post(
                self.config.token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as err:
            reason = (
                "Unable to reach Meltano Cloud authentication at "
                f"{self.config.token_url}: {err}"
            )
            raise CloudAuthenticationError(reason) from err

        if not response.ok:
            raise CloudAuthenticationError(self._token_error_reason(response))

        try:
            data = response.json()
        except ValueError as err:
            reason = "The Meltano Cloud authentication response could not be read"
            raise CloudAuthenticationError(reason) from err

        if not isinstance(data, dict) or not data.get("access_token"):
            reason = "The Meltano Cloud authentication response had no access token"
            raise CloudAuthenticationError(reason)

        return data

    @staticmethod
    def _token_error_reason(response: requests.Response) -> str:
        details = ""
        with suppress(ValueError):
            body = response.json()
            details = body.get("error_description") or body.get("error") or ""
        suffix = f": {details}" if details else ""
        return f"Meltano Cloud authentication failed{suffix}"

    def _revoke(self, refresh_token: str) -> None:
        """Revoke a refresh token, ignoring any failure.

        Args:
            refresh_token: The refresh token to revoke.
        """
        try:
            payload = {"client_id": self.config.client_id, "token": refresh_token}
            if self.config.client_secret:
                payload["client_secret"] = self.config.client_secret

            self.session.post(
                self.config.revoke_url,
                data=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as err:
            # The local session is cleared either way, so a failure to revoke
            # the token should not fail the logout.
            logger.debug("Unable to revoke Meltano Cloud refresh token", error=str(err))
