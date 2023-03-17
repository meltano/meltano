"""Python client for the Meltano Cloud API."""

from __future__ import annotations

import json
import sys
import typing as t
from contextlib import asynccontextmanager, contextmanager, suppress
from urllib.parse import urljoin

from aiohttp import ClientResponse, ClientResponseError, ClientSession
from structlog import get_logger

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version

if t.TYPE_CHECKING:
    import types

__all__ = ["MeltanoCloudClient"]

logger = get_logger()


class MeltanoCloudError(Exception):
    """Base error for the Meltano Cloud API."""

    def __init__(self, response: ClientResponse) -> None:
        """Initialize the error.

        Args:
            response: The response that caused the error.
        """
        self.response = response
        super().__init__(response.reason)


class MeltanoCloudClient:  # noqa: WPS214
    """Client for the Meltano Cloud API.

    Attributes:
        _session: The client session.
    """

    def __init__(self, config: MeltanoCloudConfig | None = None) -> None:
        """Initialize the client.

        Args:
            config: the MeltanoCloudConfig to use
        """
        self._session: ClientSession | None = None
        self.config = config or MeltanoCloudConfig()
        self.auth = MeltanoCloudAuth()
        self.api_url = self.config.base_url

    async def __aenter__(self) -> MeltanoCloudClient:
        """Enter the client context.

        Returns:
            The client.
        """
        self._session = ClientSession()
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": f"Meltano Cloud CLI/v{version('meltano.cloud.cli')}",
            }
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Exit the client context.

        Args:
            exc_type: The exception type.
            exc_value: The exception value.
            traceback: The exception traceback.
        """
        await self.close()

    async def close(self) -> None:
        """Close the client."""
        if self._session:
            await self._session.close()
            self._session = None

    @property
    def session(self) -> ClientSession:
        """Get the client session.

        Returns:
            The client session.

        Raises:
            RuntimeError: If the client session is not open.
        """
        if not self._session or self._session.closed:
            raise RuntimeError("Client session is not open")
        return self._session

    @contextmanager
    def headers(self, headers: dict) -> t.Iterator[None]:
        """Update headers within, then reset.

        Args:
            headers: the headers to use

        Yields:
            None
        """
        self.session.headers.update(headers)
        yield
        for key in headers:
            with suppress(KeyError):
                del self.session.headers[key]

    @asynccontextmanager
    async def authenticated(self) -> t.AsyncIterator[None]:
        """Provide context for API calls which require authentication.

        Yields:
            None
        """
        if not await self.auth.logged_in():
            await self.auth.login()
        with self.headers(self.auth.get_auth_header()):
            yield

    async def _request(
        self,
        method: str,
        path: str,
        base_url: str | None = None,
        **kwargs,
    ) -> dict | str:
        """Make a request to the Meltano Cloud API.

        Args:
            method: The HTTP method.
            path: The API path.
            base_url: The base_url. Uses base url from config by default.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response JSON if response body is json,
            else the response content as a string.

        Raises:
            MeltanoCloudError: If the response status is not OK.
        """
        url = urljoin(base_url if base_url else self.api_url, path)
        logger.debug(
            "Making request",
            method=method,
            url=url,
        )

        async with self.session.request(
            method,
            url,
            **kwargs,
        ) as response:
            try:
                response.raise_for_status()
            except ClientResponseError as e:
                raise MeltanoCloudError(response) from e
            content = await response.content.read()
            decoded_content = content.decode()
            try:
                return json.loads(decoded_content)
            except json.JSONDecodeError:
                return decoded_content

    @staticmethod
    def construct_runner_path(
        tenant_resource_key: str,
        project_id: str,
        deployment: str,
        job_or_schedule: str,
    ) -> str:
        """Construct the Cloud Runners URL.

        Args:
            tenant_resource_key: The tenant resource key.
            project_id: The Meltano Cloud project ID.
            deployment: The name of the Meltano Cloud deployment in which to run.
            job_or_schedule: The name of the job or schedule to run.

        Returns:
            The Cloud Runners URL.
        """
        return (
            f"/run/v1/external/"
            f"{tenant_resource_key}/{project_id}/{deployment}/{job_or_schedule}"
        )

    async def run_project(
        self,
        tenant_resource_key: str,
        project_id: str,
        deployment: str,
        job_or_schedule: str,
    ):
        """Run a Meltano project in Meltano Cloud.

        Args:
            tenant_resource_key: The tenant resource key.
            project_id: The Meltano Cloud project ID.
            deployment: The name of the Meltano Cloud deployment in which to run.
            job_or_schedule: The name of the job or schedule to run.
        """
        async with self.authenticated():
            url = (
                "/run/v1/external/"
                f"{tenant_resource_key}/{project_id}/{deployment}/{job_or_schedule}"
            )
            await self._request(
                "POST",
                url,
            )
