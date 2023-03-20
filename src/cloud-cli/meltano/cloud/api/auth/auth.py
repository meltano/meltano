"""Authentication for Meltano Cloud."""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import typing as t
import webbrowser
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlencode, urljoin

import aiohttp
import click

from meltano.cloud.api.config import MeltanoCloudConfig

if sys.version_info <= (3, 8):
    from cached_property import cached_property
else:
    from functools import cached_property

LOGIN_STATUS_CHECK_DELAY_SECONDS = 0.2


class MeltanoCloudAuthError(Exception):
    """Raised when an API call returns a 403."""


class MeltanoCloudAuth:  # noqa: WPS214
    """Authentication methods for Meltano Cloud."""

    def __init__(self, config: MeltanoCloudConfig | None = None):
        """Initialize a MeltanoCloudAuth instance.

        Args:
            config: the MeltanoCloudConfig to use
        """
        self.config = config or MeltanoCloudConfig.find()
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

    @cached_property
    def logout_url(self) -> str:
        """Get the Meltano Cloud logout URL.

        Returns:
            the Meltano Cloud logout URL.
        """
        params = urlencode(
            {
                "client_id": self.client_id,
                "logout_uri": f"http://localhost:{self.config.auth_callback_port}/logout",  # noqa: E501)
            }
        )
        return urljoin(self.base_url, f"logout?{params}")

    @contextmanager
    def callback_server(self) -> t.Iterator[None]:
        """Context manager to run callback server locally.

        Yields:
            None
        """
        server = None
        try:
            server = subprocess.Popen(  # noqa: S607
                ("flask", "run", f"--port={self.config.auth_callback_port}"),
                env={
                    **os.environ,
                    "FLASK_APP": "callback_server.py",
                    "MELTANO_CLOUD_CONFIG_PATH": str(self.config.config_path),
                },
                cwd=Path(__file__).parent,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            yield
        finally:
            if server:
                server.kill()

    async def login(self) -> None:
        """Take user through login flow and get auth and id tokens."""
        if await self.logged_in():
            return
        with self.callback_server():
            click.echo("Logging in to Meltano Cloud.")
            click.echo("You will be directed to a web browser to complete login.")
            click.echo("If a web browser does not open, open the following link:")
            click.secho(self.login_url, fg="green")
            webbrowser.open_new_tab(self.login_url)
            while not await self.logged_in():
                self.config.refresh()
                await asyncio.sleep(LOGIN_STATUS_CHECK_DELAY_SECONDS)

    async def logout(self) -> None:  # noqa: WPS213
        """Log out."""
        if not await self.logged_in():
            click.secho("Not logged in.", fg="green")
            return
        with self.callback_server():
            click.echo("Logging out of Meltano Cloud.")
            click.echo("You will be directed to a web browser to complete logout.")
            click.echo("If a web browser does not open, open the following link:")
            click.secho(self.logout_url, fg="green")
            webbrowser.open_new_tab(self.logout_url)
            while await self.logged_in():
                self.config.refresh()
                await asyncio.sleep(LOGIN_STATUS_CHECK_DELAY_SECONDS)
        click.secho("Successfully logged out.", fg="green")

    def get_auth_header(self) -> dict[str, str]:
        """Get the authorization header.

        Used for authenticating to cloud API endpoints.

        Returns:
            Authorization header using ID token as bearer token.

        """
        return {"Authorization": f"Bearer {self.config.id_token}"}

    def get_access_token_header(self) -> dict[str, str]:
        """Get the access token header.

        Used for authenticating to auth endpoints.

        Returns:
            Authorization header using access token as bearer token.
        """
        return {"Authorization": f"Bearer {self.config.access_token}"}

    async def get_user_info_response(self) -> aiohttp.ClientResponse:
        """Get user info.

        Returns:
            User info response
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                urljoin(self.base_url, "oauth2/userInfo"),
                headers=self.get_access_token_header(),
            ) as response:
                return response

    async def get_user_info_json(self) -> dict:
        """Get user info as dict.

        Returns:
            User info json
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                urljoin(self.base_url, "oauth2/userInfo"),
                headers=self.get_access_token_header(),
            ) as response:
                return await response.json()

    async def logged_in(self) -> bool:
        """Check if this instance is currently logged in.

        Returns:
            True if logged in, else False
        """
        user_info_resp = await self.get_user_info_response()
        return bool(
            self.config.access_token and self.config.id_token and user_info_resp.ok
        )
