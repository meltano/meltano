"""Authentication for Meltano Cloud."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.parse import urlencode

import click
import requests

from meltano.cloud.api.config import MeltanoCloudConfig

if sys.version_info <= (3, 8):
    from cached_property import cached_property
else:
    from functools import cached_property


class MeltanoCloudAuthError(Exception):
    """Raised when an API call returns a 403."""


class MeltanoCloudAuth:
    """Authentication methods for Meltano Cloud."""

    def __init__(self):
        """Initialize a MeltanoCloudAuth instance."""
        self.config = MeltanoCloudConfig.find()
        self.base_url = self.config.base_auth_url
        self.client_id = self.config.app_client_id

    @cached_property
    def login_url(self) -> str:
        """Get the oauth2 authorization URL.

        Returns:
            the oauth2 authorization URL.
        """
        query_params = urlencode(
            {
                "client_id": self.client_id,
                "response_type": "token",
                "scope": "email openid profile",
                "redirect_uri": f"http://localhost:{self.config.auth_callback_port}",
            }
        )
        return f"{self.base_url}/oauth2/authorize?{query_params}"

    def login(self) -> None:
        """Take user through login flow and get auth and id tokens."""
        if self.logged_in():
            return
        server = None
        try:
            click.echo("Logging in to Meltano Cloud.")
            click.echo("You will be directed to a web browser to complete login.")
            click.echo("If a web browser does not open, open the following link:")
            click.secho(self.login_url, fg="green")
            webbrowser.open_new_tab(self.login_url)
            server = subprocess.Popen(  # noqa: S607
                ["flask", "run", "--port", f"{self.config.auth_callback_port}"],
                env={
                    **os.environ,
                    "FLASK_APP": "callback_server.py",
                },
                cwd=Path(__file__).parent,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            while not self.logged_in():
                self.config.refresh()
                time.sleep(0.2)  # noqa: WPS432
        finally:
            if server:
                server.kill()

    def logout(self):
        """Log out.

        Raises:
            MeltanoCloudAuthError: when logout request returns error
        """
        response = requests.get(
            f"{self.base_url}/logout", params={"client_id": self.client_id}
        )
        if not response.ok:
            raise MeltanoCloudAuthError

    def get_auth_header(self) -> dict[str, str]:
        """Get the authorization header.

        Returns:
            the authorization header with bearer token.

        """
        return {"Authorization": f"Bearer {self.config.access_token}"}

    def get_user_info_response(self):
        """Get user info.

        Returns:
            requests.Response with user info in body.

        """
        return requests.get(
            f"{self.base_url}/oauth2/userInfo",
            headers=self.get_auth_header(),
        )

    def logged_in(self) -> bool:
        """Check if this instance is currently logged in.

        Returns:
            True if logged in, else False
        """
        return (
            self.config.access_token  # type: ignore
            and self.config.id_token
            and self.get_user_info_response().ok
        )
