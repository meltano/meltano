"""Meltano Cloud `state` command."""

from __future__ import annotations

import typing as t
from pathlib import Path

import click
from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import pass_context
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from meltano.cloud.cli.base import MeltanoCloudCLIContext


class StateCloudClient(MeltanoCloudClient):
    async def list_state(self):
        async with self.authenticated():
            response = await self._json_request(
                "GET",
                f"state/v1/{self.config.tenant_resource_key}/{self.config.internal_project_id}",
            )
        return response

    async def get_state(self, state_id: str | None = None):
        async with self.authenticated():
            presigned_url = await self._json_request(
                "GET",
                f"state/v1/{self.config.tenant_resource_key}/{self.config.internal_project_id}/{state_id}",
            )
        return presigned_url

    async def set_state(
        self,
        state_filepath: Path,
        state_id: str | None = None,
    ):
        async with self.authenticated():
            presigned_url = await self._json_request(
                "PUT",
                f"state/v1/{self.config.tenant_resource_key}/{self.config.internal_project_id}/{state_id}",
            )
        return presigned_url

    async def delete_state(self, state_id: str | None = None):
        async with self.authenticated():
            response = await self._json_request(
                "DELETE",
                f"state/v1/{self.config.tenant_resource_key}/{self.config.internal_project_id}/{state_id}",
            )
        return response


@click.group("state")
def state_group() -> None:
    """Interact with Meltano Cloud state."""


@state_group.command("list")
@pass_context
@run_async
async def list_state_ids(context: MeltanoCloudCLIContext):
    """List state IDs in Meltano Cloud project."""
    async with StateCloudClient(config=context.config) as client:
        response = await client.list_state()
        for state_id in response:
            click.secho(state_id, fg="green")


@state_group.command("delete")
@pass_context
@run_async
async def delete_state(context: MeltanoCloudCLIContext):
    async with StateCloudClient(config=context.config) as client:
        response = await client.delete_state()
        click.secho(response, fg="green")


@state_group.command("get")
@pass_context
@run_async
async def get_state(context: MeltanoCloudCLIContext):
    async with StateCloudClient(config=context.config) as client:
        response = await client.get_state("some-state-id")
        click.secho(response, fg="green")


@state_group.command("set")
@pass_context
@run_async
async def set_state(context: MeltanoCloudCLIContext):
    async with StateCloudClient(config=context.config) as client:
        response = await client.set_state("some-state-id")
        click.secho(response, fg="green")
