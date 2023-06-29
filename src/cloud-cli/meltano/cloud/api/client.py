"""Python client for the Meltano Cloud API."""

from __future__ import annotations

import json
import sys
import typing as t
from contextlib import asynccontextmanager, contextmanager, suppress
from http import HTTPStatus
from urllib.parse import urljoin

from aiohttp import ClientResponse, ClientResponseError, ClientSession
from structlog import get_logger

from meltano.cloud import __version__ as version
from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig

if t.TYPE_CHECKING:
    import types

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

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


class MeltanoCloudClient:  # noqa: WPS214, WPS230
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
        self.auth = MeltanoCloudAuth(self.config)
        self.api_url = self.config.base_url
        self.version = version
        self._within_authenticated: bool = False

    async def __aenter__(self) -> Self:
        """Enter the client context.

        Returns:
            The client.
        """
        self._session = ClientSession()
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": f"Meltano Cloud CLI/v{self.version}",
            },
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

        Authorization and ID tokens may be out-of-date. In this case, requests made
        within the context which get a 403 response will cause re-authentication, and
        the request will be remade.

        This context manager is not reentrant.

        Yields:
            None
        """
        if not self.auth.has_auth_tokens():
            await self.auth.login()
        self._within_authenticated = True
        with self.headers(self.auth.get_auth_header()):
            yield
        self._within_authenticated = False

    @staticmethod
    def clean_params(params: dict) -> dict:
        """Remove None values from params.

        Args:
            params: The params to clean.

        Returns:
            The cleaned params.
        """
        return {k: v for k, v in params.items() if v is not None}

    @asynccontextmanager
    async def _raw_request(
        self,
        method: str,
        path: str,
        base_url: str | None = None,
        **kwargs: t.Any,
    ) -> t.AsyncGenerator[ClientResponse, None]:
        """Make a request to the Meltano Cloud API.

        Args:
            method: The HTTP method.
            path: The API path.
            base_url: The base_url. Uses base url from config by default.
            **kwargs: Additional keyword arguments to pass to the request.

        Yields:
            The response object.

        Raises:
            MeltanoCloudError: If the response status is not OK.
        """
        url = urljoin(base_url if base_url else self.api_url, path)
        logger.debug("Making Cloud CLI HTTP request", method=method, url=url)
        async with self.session.request(method, url, **kwargs) as response:
            if (
                response.status != HTTPStatus.FORBIDDEN
                or not self._within_authenticated
            ):
                try:
                    response.raise_for_status()
                except ClientResponseError as e:
                    raise MeltanoCloudError(response) from e
                yield response
                return

        logger.debug(
            "Authentication failed with a 403, retrying after login",
            method=method,
            url=url,
        )
        await self.auth.login()
        self.session.headers.update(self.auth.get_auth_header())
        async with self.session.request(method, url, **kwargs) as response:
            try:
                response.raise_for_status()
            except ClientResponseError as e:
                raise MeltanoCloudError(response) from e
            yield response

    async def _json_request(
        self,
        method: str,
        path: str,
        base_url: str | None = None,
        **kwargs: t.Any,
    ) -> dict[str, t.Any] | list[t.Any] | str | int | float | None:
        """Make a request to the Meltano Cloud API.

        Args:
            method: The HTTP method.
            path: The API path.
            base_url: The base_url. Uses base url from config by default.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response JSON if response body is json,
            else the response content as a string.
        """
        async with self._raw_request(method, path, base_url, **kwargs) as response:
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
        deployment: str,
        job_or_schedule: str,
    ):
        """Run a Meltano project in Meltano Cloud.

        Args:
            deployment: The name of the Meltano Cloud deployment in which to run.
            job_or_schedule: The name of the job or schedule to run.

        Raises:
            MeltanoCloudError: The Meltano Cloud API responded with an error.
        """
        async with self.authenticated():
            try:
                url = (
                    "/run/v1/external/"
                    f"{self.config.tenant_resource_key}/"
                    f"{self.config.internal_project_id}/"
                    f"{deployment}/{job_or_schedule}"
                )
                await self._json_request("POST", url)
            except MeltanoCloudError as ex:
                if ex.response.status == HTTPStatus.BAD_REQUEST:
                    ex.response.reason = (
                        f"Unable to find schedule named {job_or_schedule!r} "
                        f"within a deployment named {deployment!r}"
                    )
                    raise MeltanoCloudError(ex.response) from ex
                raise
