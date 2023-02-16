"""Python client for the Meltano Cloud API."""

from __future__ import annotations

import types

from aiohttp import ClientResponse, ClientResponseError, ClientSession
from structlog import get_logger

from meltano import __version__
from meltano.cloud.client import models

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
        api_url: The API URL.
        api_key: The API key.
        _session: The client session.
    """

    def __init__(self, api_url: str, api_key: str) -> None:
        """Initialize the client.

        Args:
            api_url: The Cloud API URL.
            api_key: The Cloud API key.
        """
        self.api_url = api_url
        self.api_key = api_key
        self._session: ClientSession | None = None

    async def __aenter__(self) -> MeltanoCloudClient:
        """Enter the client context.

        Returns:
            The client.
        """
        self._session = ClientSession()
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

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make a request to the Meltano Cloud API.

        Args:
            method: The HTTP method.
            path: The API path.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response JSON.

        Raises:
            MeltanoCloudError: If the response status is not OK.
        """
        url = f"{self.api_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"Meltano Cloud CLI/v{__version__}",
            "Authorization": f"Bearer {self.api_key}",
        }
        logger.debug(
            "Making request",
            method=method,
            url=url,
            headers=headers,
            **kwargs,
        )

        async with self.session.request(
            method,
            url,
            headers=headers,
            **kwargs,
        ) as response:
            try:
                response.raise_for_status()
            except ClientResponseError as e:
                raise MeltanoCloudError(response) from e
            return await response.json()

    async def run_project(self, project_id: str, job_or_schedule: str) -> dict:
        """Run a Meltano project in Meltano Cloud.

        Args:
            project_id: The project identifier.
            job_or_schedule: The job or schedule identifier.

        Returns:
            The run details.
        """
        run_request = models.RunRequestData(job_or_schedule_id=job_or_schedule)
        return await self._request(
            "POST",
            f"/projects/{project_id}/runs",
            json=run_request.dict(),
        )
