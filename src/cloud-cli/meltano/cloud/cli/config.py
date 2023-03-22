"""Cloud Config CLI."""

from __future__ import annotations

import click

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.api.config import MeltanoCloudConfig
from meltano.cloud.cli.base import cloud


@cloud.group("config")
@click.pass_context
def config(context: click.Context) -> None:  # noqa: WPS120
    """Meltano Cloud `config` command."""


class CloudConfigClient(MeltanoCloudClient):
    """Cloud Config Client."""

    secrets_service_prefix = "/secrets/v1/"

    @property
    def _tenant_prefix(self):
        return f"{self.config.tenant_resource_key}/{self.config.project_id}/"

    def list_all(self):
        """List Cloud Config keys."""
        url = self.secrets_service_prefix + self._tenant_prefix
        with self.authenticated():
            with self._raw_request("GET", url) as response:
                return response

    def set_value(self, secret_name: str, secret_value: str):
        """Set Cloud Config secret."""
        url = self.secrets_service_prefix + self._tenant_prefix
        body = {"name": secret_name.upper(), "value": secret_value}
        with self.authenticated():
            with self._raw_request("POST", url, body=body) as response:
                return response

    def delete(self, secret_name: str):
        """Delete Cloud Config secret."""
        url = (
            self.secrets_service_prefix,
            self._tenant_prefix,
            f"{secret_name.upper()}",
        )
        with self.authenticated():
            with self._raw_request("DELETE", url) as response:
                return response


@config.group()
@click.pass_context
def env(context: click.Context) -> None:  # noqa: WPS120
    """Meltano Cloud `config` command."""


@env.command("list")
@click.pass_context
def list_all(context: click.Context) -> None:
    """List all Cloud Config."""
    cfg: MeltanoCloudConfig = context.obj["config"]
    with CloudConfigClient(config=cfg) as client:
        click.echo("Listing Cloud Config...")
        response = client.list_all()
        for secret in response.json.items():
            click.echo(secret["name"], nl=True)


@env.command("set")
@click.argument("secret_name", type=str, required=True)
@click.password_option()
@click.pass_context
def set_value(context: click.Context, secret_name: str, password) -> None:
    """Create new Cloud Config."""
    cfg: MeltanoCloudConfig = context.obj["config"]
    with CloudConfigClient(config=cfg) as client:
        client.set_value(secret_name=secret_name.upper(), secret_value=password)
        click.echo(f"Successfully created '{secret_name.upper()}'.")


@env.command()
@click.argument("secret_name", type=str, required=True)
@click.pass_context
def delete(context: click.Context, secret_name) -> None:
    """Delete existing Cloud Config."""
    cfg: MeltanoCloudConfig = context.obj["config"]
    with CloudConfigClient(config=cfg) as client:
        client.delete(secret_name=secret_name.upper())
        click.echo(f"Successfully deleted '{secret_name.upper()}'.")
