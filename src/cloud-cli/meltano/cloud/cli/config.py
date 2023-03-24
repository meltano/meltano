"""Meltano Cloud config CLI."""

from __future__ import annotations

import typing as t

import click

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import pass_context, run_async

if t.TYPE_CHECKING:
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

MAX_PAGE_SIZE = 250


@click.group("config")
def config() -> None:
    """Configure Meltano Cloud project settings and secrets."""


class ConfigCloudClient(MeltanoCloudClient):
    """Meltano Cloud config Client."""

    secrets_service_prefix = "/secrets/v1/"

    @property
    def _tenant_prefix(self) -> str:
        return f"{self.config.tenant_resource_key}/{self.config.internal_project_id}/"

    async def list_items(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
    ):
        """List Meltano Cloud config keys."""
        params: dict[str, t.Any] = {
            "page_size": page_size,
            "page_token": page_token,
        }
        async with self.authenticated():
            return await self._json_request(
                "GET",
                self.secrets_service_prefix + self._tenant_prefix,
                params=self.clean_params(params),
            )

    async def set_value(self, secret_name: str, secret_value: str):
        """Set Meltano Cloud config secret."""
        async with self.authenticated():
            return await self._json_request(
                "PUT",
                self.secrets_service_prefix + self._tenant_prefix,
                json={"name": secret_name, "value": secret_value},
            )

    async def delete(self, secret_name: str):
        """Delete Meltano Cloud config secret."""
        async with self.authenticated():
            return await self._json_request(
                "DELETE",
                self.secrets_service_prefix + self._tenant_prefix + secret_name,
            )


@config.group()
def env() -> None:
    """Configure Meltano Cloud environment variable secrets."""


@env.command("list")
@click.option(
    "--limit",
    required=False,
    type=int,
    default=10,
    help="The maximum number of history items to display.",
)
@pass_context
@run_async
async def list_items(
    context: MeltanoCloudCLIContext,
    limit: int,
) -> None:
    """List Meltano Cloud config items."""
    page_token = None
    page_size = min(limit, MAX_PAGE_SIZE)
    results: list[dict[str, str]] = []

    async with ConfigCloudClient(config=context.config) as client:
        while True:
            response = await client.list_items(
                page_token=page_token,
                page_size=page_size,
            )

            results.extend(response["results"])

            if response["pagination"] and len(results) < limit:
                page_token = response["pagination"]["next_page_token"]
            else:
                break

    for secret in results[:limit]:
        click.echo(secret["name"])


@env.command("set")
@click.argument("secret_name", type=str, required=True)
@click.password_option("--value")
@pass_context
@run_async
async def set_value(
    context: MeltanoCloudCLIContext,
    secret_name: str,
    value: str,
) -> None:
    """Create a new Meltano Cloud config item."""
    async with ConfigCloudClient(config=context.config) as client:
        await client.set_value(secret_name=secret_name, secret_value=value)
        click.echo(f"Successfully set config item {secret_name!r}.")


@env.command()
@click.argument("secret_name", type=str, required=True)
@pass_context
@run_async
async def delete(
    context: MeltanoCloudCLIContext,
    secret_name,
) -> None:
    """Delete an existing Meltano Cloud config item."""
    async with ConfigCloudClient(config=context.config) as client:
        await client.delete(secret_name=secret_name)
        click.echo(f"Successfully deleted config item {secret_name!r}.")
