"""Meltano Cloud `state` command."""

from __future__ import annotations

import json
import typing as t
from http import HTTPStatus
from io import BytesIO
from pathlib import Path

import click
import requests

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import pass_context
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from meltano.cloud.cli.base import MeltanoCloudCLIContext


class InvalidStateError(Exception):
    """Raised when provided state is not valid Meltano state."""


class StateCloudClient(MeltanoCloudClient):
    """Client for Meltano Cloud state API."""

    async def list_state(self):
        """List state IDs."""
        async with self.authenticated():
            response = await self._json_request(
                "GET",
                f"state/v1/{self.config.tenant_resource_key}"
                f"/{self.config.internal_project_id}",
            )
        return response

    async def get_state(self, state_id: str | None = None):
        """Get state for the given state ID."""
        async with self.authenticated():
            presigned_url = await self._json_request(
                "GET",
                f"state/v1/{self.config.tenant_resource_key}"
                f"/{self.config.internal_project_id}/{state_id}",
            )
        return requests.get(presigned_url)  # noqa: S113

    async def set_state(
        self,
        state_filepath: Path,
        state_id: str | None = None,
    ):
        """Create or replace state for the given state ID."""
        async with self.authenticated():
            presigned_post = await self._json_request(
                "PUT",
                f"state/v1/{self.config.tenant_resource_key}"
                f"/{self.config.internal_project_id}/{state_id}",
            )
        with open(state_filepath, "rb") as new_state:
            state_dict = json.load(new_state)
            new_state_dict = self.prepare_state(state_dict)
        prepared_state_bytes = BytesIO()
        prepared_state_bytes.write(json.dumps(new_state_dict).encode("utf-8"))
        prepared_state_bytes.seek(0)
        return requests.post(  # noqa: S113
            presigned_post["url"],
            data=presigned_post["fields"],
            files={"file": ("state.json", prepared_state_bytes)},
        )

    @staticmethod
    def prepare_state(state_dict: dict[t.Any, t.Any]) -> dict[t.Any, t.Any]:
        """Format given state to be Cloud-compatible, if necessary.

        Args:
            state_dict: the state to prepare

        Returns:
            Cloud-compatible state dict.
        """
        if ("complete" in state_dict and "singer_state" in state_dict["complete"]) or (
            "partial" in state_dict and "singer_state" in state_dict["partial"]
        ):
            return state_dict
        elif "singer_state" in state_dict:
            return {"complete": state_dict}
        raise InvalidStateError

    async def delete_state(self, state_id: str | None = None):
        """Delete state for the given state ID."""
        async with self.authenticated():
            response = await self._json_request(
                "DELETE",
                f"state/v1/{self.config.tenant_resource_key}"
                f"/{self.config.internal_project_id}/{state_id}",
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
@click.option(
    "--state-id",
    help="Identifier for the state to be deleted."
    "E.g. 'dev:tap-github-to-target-postgres",
    prompt=True,
)
@pass_context
@run_async
async def delete_state(context: MeltanoCloudCLIContext):  # noqa: D103
    async with StateCloudClient(config=context.config) as client:
        response = await client.delete_state()
        click.secho(response, fg="green")


@state_group.command("get")
@click.option(
    "--state-id",
    help="Identifier for the state to retrieve."
    "E.g. 'dev:tap-github-to-target-postgres",
    prompt=True,
)
@pass_context
@run_async
async def get_state(  # noqa: D103 E501 WPS463
    context: MeltanoCloudCLIContext,
    state_id: str,
):
    async with StateCloudClient(config=context.config) as client:
        response = await client.get_state(state_id=state_id)
        if response.status_code == HTTPStatus.NOT_FOUND:
            click.secho(f"No state found for {state_id}", fg="red")
            return
        click.echo(response.json())


@state_group.command("set")
@click.option(
    "--state-id",
    help="Identifier for the state to set. E.g. 'dev:tap-github-to-target-postgres",  # noqa: E501
    prompt=True,
)
@click.option(
    "--file-path",
    help="Path to file containing new state.",
    prompt=True,
)
@pass_context
@run_async
async def set_state(  # noqa: D103
    context: MeltanoCloudCLIContext,
    state_id: str,
    file_path: str,
):
    async with StateCloudClient(config=context.config) as client:
        await client.set_state(
            state_filepath=Path(file_path),
            state_id=state_id,
        )
        click.secho(f"Successfully set state for {state_id}")
