"""Client for the Meltano Cloud history API."""

from __future__ import annotations

import datetime
import typing as t
from http import HTTPStatus

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudExecution

__all__ = ["HistoryClient"]


class HistoryClient(MeltanoCloudClient):
    """Client for the Meltano Cloud history API."""

    MAX_PAGE_SIZE = 250

    async def get_execution_history(
        self,
        *,
        schedule: str | None = None,
        deployment: str | None = None,
        result: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        start_time: datetime.datetime | None = None,
    ):
        """Get the execution history for a Meltano Cloud project.

        Args:
            schedule: The name of the schedule to get the history for.
            deployment: The name of the deployment to get the history for.
            result: The result to filter on.
            page_size: The number of executions to return.
            page_token: The page token to use for pagination.
            start_time: The start time to use for filtering.

        Returns:
            The execution history.

        Raises:
            MeltanoCloudError: The Meltano Cloud API responded with an error.
        """
        params: dict[str, t.Any] = {
            "page_size": page_size,
            "page_token": page_token,
            "schedule": schedule,
            "deployment": deployment,
            "result": result,
            "start_time": start_time.isoformat() if start_time else None,
        }

        async with self.authenticated():
            url = (
                "/jobs/v1/"
                f"{self.config.tenant_resource_key}/"
                f"{self.config.internal_project_id}"
            )
            try:
                return await self._json_request(
                    "GET",
                    url,
                    params=self.clean_params(params),
                )
            except MeltanoCloudError as ex:
                if ex.response.status == HTTPStatus.UNPROCESSABLE_ENTITY:
                    ex.response.reason = "Unable to process request"
                    raise MeltanoCloudError(ex.response) from ex
                raise

    @classmethod
    async def get_history_list(
        cls,
        config: MeltanoCloudConfig,
        *,
        schedule_filter: str | None,
        deployment_filter: str | None,
        result_filter: str | None,
        start_time: datetime.datetime | None,
        limit: int,
    ) -> list[CloudExecution]:
        """Get a Meltano project execution history in Meltano Cloud.

        Args:
            config: The meltano config to use
            schedule_filter: Used to filter the history by schedule name.
            deployment_filter: Used to filter the history by deployment name.
            result_filter: Used to filter the history by result.
            start_time: Used to filter the history by start time.
            limit: The maximum number of history items to return.

        Returns:
            The execution history.
        """
        page_token = None
        page_size = min(limit, cls.MAX_PAGE_SIZE)
        results: list[CloudExecution] = []

        async with cls(config=config) as client:
            while True:
                response = await client.get_execution_history(
                    schedule=schedule_filter,
                    deployment=deployment_filter,
                    result=result_filter,
                    page_size=page_size,
                    page_token=page_token,
                    start_time=start_time,
                )

                results.extend(response["results"])

                if response["pagination"] and len(results) < limit:
                    page_token = response["pagination"]["next_page_token"]
                else:
                    break

        return results[:limit]
