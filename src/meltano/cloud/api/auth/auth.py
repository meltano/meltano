"""Authentication for Meltano Cloud."""

from __future__ import annotations

import asyncio
import sys
import tempfile
import typing as t
import webbrowser
from contextlib import asynccontextmanager
from functools import cached_property
from http import HTTPStatus
from pathlib import Path
from urllib.parse import urlencode, urljoin

import aiohttp
import click
import jinja2
from aiohttp import web

from meltano.cloud.api.config import MeltanoCloudConfig

if sys.version_info < (3, 9):
    import importlib_resources
else:
    from importlib import resources as importlib_resources

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
            },
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
            },
        )
        return urljoin(self.base_url, f"logout?{params}")

    @asynccontextmanager
    async def _callback_server(
        self,
        rendered_template_dir: Path,
    ) -> t.AsyncIterator[web.Application]:
        app = web.Application()
        resource_root = importlib_resources.files(__package__)

        async def callback_page(_):
            with importlib_resources.as_file(
                resource_root / "callback.jinja2",
            ) as template_file, (rendered_template_dir / "callback.html").open(
                "w",
            ) as rendered_template_file:
                rendered_template_file.write(
                    jinja2.Template(template_file.read_text()).render(
                        port=self.config.auth_callback_port,
                    ),
                )
            return web.FileResponse(rendered_template_file.name)

        async def handle_tokens(request: web.Request):
            self.config.id_token = request.query["id_token"]
            self.config.access_token = request.query["access_token"]
            self.config.write_to_file()
            return web.Response(status=HTTPStatus.NO_CONTENT)

        async def handle_logout(_):
            self.config.id_token = None
            self.config.access_token = None
            self.config.write_to_file()
            with importlib_resources.as_file(
                resource_root / "logout.html",
            ) as html_file:
                return web.FileResponse(html_file)

        app.add_routes(
            (
                web.get("/", callback_page),
                web.get("/tokens", handle_tokens),
                web.get("/logout", handle_logout),
            ),
        )
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.config.auth_callback_port)
        await site.start()
        try:
            yield app
        finally:
            await runner.cleanup()

    @asynccontextmanager
    async def callback_server(self) -> t.AsyncIterator[web.Application]:
        """Context manager to run callback server locally.

        Yields:
            The aiohttp web application.
        """
        with tempfile.TemporaryDirectory(prefix="meltano-cloud-") as tmpdir:
            async with self._callback_server(Path(tmpdir)) as app:
                yield app

    async def login(self) -> None:
        """Take user through login flow and get auth and id tokens."""
        if await self.logged_in():
            return
        async with self.callback_server():
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
        async with self.callback_server():
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

    @asynccontextmanager
    async def _get_user_info_response(self) -> t.AsyncIterator[aiohttp.ClientResponse]:
        async with aiohttp.ClientSession() as session, session.get(
            urljoin(self.base_url, "oauth2/userInfo"),
            headers=self.get_access_token_header(),
        ) as response:
            yield response

    async def get_user_info_response(self) -> aiohttp.ClientResponse:
        """Get user info.

        Returns:
            User info response
        """
        async with self._get_user_info_response() as response:
            return response

    async def get_user_info_json(self) -> dict:
        """Get user info as dict.

        Returns:
            User info json
        """
        async with self._get_user_info_response() as response:
            return await response.json()

    async def logged_in(self) -> bool:
        """Check if this instance is currently logged in.

        Returns:
            True if logged in, else False
        """
        return bool(
            self.has_auth_tokens()
            # Perform this check at the end to avoid
            # spamming our servers if logout fails
            and (await self.get_user_info_response()).ok,
        )

    def has_auth_tokens(self) -> bool:
        """Check if this instance has cached access and ID tokens.

        Returns:
            True if it has both tokens, else False
        """
        return bool(self.config.access_token and self.config.id_token)
