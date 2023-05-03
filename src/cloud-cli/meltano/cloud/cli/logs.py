"""Meltano Cloud `logs` command."""

from __future__ import annotations

import sys
import typing as t
from contextlib import asynccontextmanager

import click

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import pass_context, run_async

if t.TYPE_CHECKING:
    from aiohttp import ClientResponse

    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.cli.base import MeltanoCloudCLIContext


class LogsClient(MeltanoCloudClient):
    """Meltano Cloud `logs` command client."""

    @asynccontextmanager
    async def stream_logs(
        self,
        execution_id: str,
    ) -> t.AsyncGenerator[ClientResponse, None]:
        """Stream logs from a Meltano Cloud execution.

        Args:
            execution_id: The execution identifier.

        Yields:
            The response object.
        """
        url = (
            "/logs/v1/"
            f"{self.config.tenant_resource_key}"
            f"/{self.config.internal_project_id}/{execution_id}"
        )

        async with self.authenticated():
            async with self._raw_request("GET", url) as response:
                yield response

    async def _get_logs_page(
        self,
        execution_id: str,
        page_token: str | None = None,
    ):
        """Get a page of logs.

        Args:
            execution_id: The execution identifier.
            page_token: The page token.

        Returns:
            The response.
        """
        url = (
            "/logs/v1/"
            f"{self.config.tenant_resource_key}"
            f"/{self.config.internal_project_id}/tail/{execution_id}"
        )
        params = {"page_token": page_token}
        return await self._json_request("GET", url, params=self.clean_params(params))

    async def get_logs(
        self,
        execution_id: str,
    ) -> t.AsyncGenerator[dict, None]:
        """Get the logs.

        Args:
            execution_id: The execution identifier.

        Returns:
            The response.
        """
        page_token = None
        async with self.authenticated():
            while True:
                response = await self._get_logs_page(execution_id, page_token)
                yield response

                pagination = response.get("pagination") or {}
                new_page_token = pagination.get("next_page_token")

                if not new_page_token or new_page_token == page_token:
                    break

                page_token = new_page_token


@click.group()
def logs() -> None:
    """Meltano Cloud `logs` command."""


async def print_logs(
    config: MeltanoCloudConfig,
    execution_id: str,
) -> None:
    """Print the logs.

    Args:
        execution_id: The execution identifier.
        config: the meltano config to use
    """
    async with LogsClient(config=config) as client:
        async for page in client.get_logs(execution_id):
            sys.stdout.writelines(f'{event["message"]}\n' for event in page["results"])
            sys.stdout.flush()


@logs.command("print")
@click.option("--execution-id", required=True)
@pass_context
@run_async
async def print_(context: MeltanoCloudCLIContext, execution_id: str) -> None:
    """Print the logs.

    Args:
        context: The Click context.
        execution_id: The execution identifier.
    """
    click.echo(f"Fetching logs for execution {execution_id}")
    await print_logs(context.config, execution_id)
