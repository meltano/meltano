"""Meltano Cloud `job` command."""

from __future__ import annotations

import typing as t
from http import HTTPStatus

import click
from aiohttp import ClientResponse

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import pass_context, run_async

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

DEFAULT_GET_PROJECTS_LIMIT = 125
MAX_PAGE_SIZE = 250


class JobsClient(MeltanoCloudClient):
    """A Meltano Cloud client with extensions for jobs."""

    def validate_response(self, response: ClientResponse) -> None:
        """Validate the response.

        Args:
            response: The response to validate.
        """
        if (
            response.status == HTTPStatus.BAD_REQUEST
            and response.content_type == "application/json"
        ):
            return
        super().validate_response(response)

    async def stop_execution(
        self,
        *,
        execution_id: str,
    ):
        """Stop an execution.

        Args:
            execution_id: The execution ID to stop.
        """
        trk = self.config.tenant_resource_key
        pid = self.config.internal_project_id
        async with self.authenticated():
            return await self._json_request(
                "DELETE",
                f"/jobs/v1/{trk}/{pid}/{execution_id}",
            )


@click.group("job", help="Interact with Meltano Cloud jobs.")
def job_group() -> None:
    """Interact with Meltano Cloud job executions."""


async def _stop_execution(
    config: MeltanoCloudConfig,
    *,
    execution_id: str,
) -> t.Any:
    async with JobsClient(config=config) as client:
        return await client.stop_execution(execution_id=execution_id)


@job_group.command("stop")
@click.option(
    "--execution-id",
    required=True,
    help="The execution ID to stop.",
)
@pass_context
@run_async
async def stop_execution(
    context: MeltanoCloudCLIContext,
    execution_id: str,
) -> None:
    """Stop a job execution."""
    result = await _stop_execution(
        context.config,
        execution_id=execution_id,
    )
    if "detail" in result:
        click.secho(result["detail"], fg="yellow", err=True)
    else:
        click.secho(f"Stopping execution {execution_id}...", fg="green", err=True)
