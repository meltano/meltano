"""Python client for the Meltano Cloud API."""

from __future__ import annotations

import sys
import typing as t

from aiohttp import ClientResponse, ClientResponseError, ClientSession
from structlog import get_logger

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


class MeltanoCloudClient:
    """Client for the Meltano Cloud API.

    Attributes:
        _session: The client session.
    """

    CLOUD_RUNNERS_URL = "https://cloud-runners.meltano.com/v1"
    API_URL = "https://api.meltano.com/v1"

    def __init__(self) -> None:
        """Initialize the client."""
        self._session: ClientSession | None = None

    async def __aenter__(self) -> MeltanoCloudClient:
        """Enter the client context.

        Returns:
            The client.
        """
        self._session = ClientSession(
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"Meltano Cloud CLI/v{version('meltano')}",
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
            msg = "Client session is not open"
            raise RuntimeError(msg)
        return self._session

    async def _request(
        self,
        method: str,
        path: str,
        url: str | None = API_URL,
        **kwargs: t.Any,
    ) -> dict:
        """Make a request to the Meltano Cloud API.

        Args:
            method: The HTTP method.
            path: The API path.
            url: The API URL for this request, if different from the base URL.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response JSON.

        Raises:
            MeltanoCloudError: If the response status is not OK.
        """
        url = f"{url}{path}"
        logger.debug(
            "Making request",
            method=method,
            url=url,
            headers=kwargs.get("headers"),
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
            return await response.json()

    async def run_project(
        self,
        tenant_resource_key: str,
        project_id: str,
        environment: str,
        job_or_schedule: str,
        api_key: str,
        runner_secret: str,
    ) -> dict:
        """Run a Meltano project in Meltano Cloud.

        Args:
            tenant_resource_key: The tenant resource key.
            project_id: The project identifier.
            environment: The Meltano environment to run.
            job_or_schedule: The job or schedule identifier.
            api_key: The Cloud Runners API key.
            runner_secret: The runner secret.

        Returns:
            The run details.
        """
        return await self._request(
            "POST",
            f"/{tenant_resource_key}/{project_id}/{environment}/{job_or_schedule}",
            url=self.CLOUD_RUNNERS_URL,
            headers={
                "x-api-key": api_key,
                "meltano-runner-secret": runner_secret,
            },
        )
