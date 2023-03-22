"""Cloud Config CLI."""

from __future__ import annotations

import click

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.api.config import MeltanoCloudConfig
from meltano.cloud.cli.base import cloud


@cloud.group("config")
@click.pass_context
def config_(context: click.Context) -> None:  # noqa: WPS120
    """Meltano Cloud `config` command."""


class CloudConfigClient(MeltanoCloudClient):
    """Cloud Config Client."""

    def list_all(self):
        """List Cloud Config keys."""
        url = (
            "/secrets/v1/external/"
            f"{self.config.organization_id}/{self.config.project_id}"
        )
        with self.authenticated():
            with self._raw_request("GET", url) as response:
                return response

    def create(self, secret_name: str, secret_value: str):
        """Create new Cloud Config secret."""
        url = (
            "/secrets/v1/external/"
            f"{self.config.organization_id}/{self.config.project_id}"
        )
        body = {"name": secret_name.upper(), "value": secret_value}
        with self.authenticated():
            with self._raw_request("POST", url, body=body) as response:
                return response

    def update(self, secret_name: str, secret_value: str):
        """Update existing Cloud Config secret."""
        url = (
            "/secrets/v1/external/"
            f"{self.config.organization_id}/{self.config.project_id}"
            f"{secret_name.upper()}"
        )
        body = {"name": secret_name.upper(), "value": secret_value}
        with self.authenticated():
            with self._raw_request("PUT", url, body=body) as response:
                return response

    def delete(self, secret_name: str):
        """Delete Cloud Config secret."""
        url = (
            "/secrets/v1/external/"
            f"{self.config.organization_id}/{self.config.project_id}"
            f"{secret_name.upper()}"
        )
        with self.authenticated():
            with self._raw_request("DELETE", url) as response:
                return response


@config_.command("list")
@click.pass_context
def list_all(context: click.Context) -> None:
    """List all Cloud Config."""
    config: MeltanoCloudConfig = context.obj["config"]
    with CloudConfigClient(config=config) as client:
        click.echo("Listing Cloud Config...")
        response = client.list_all()
        for secret in response.json.items():
            click.echo(secret["name"], nl=True)


@config_.command()
@click.argument("secret_name", type=str, required=True)
@click.password_option()
@click.pass_context
def create(context: click.Context, secret_name: str, password) -> None:
    """Create new Cloud Config."""
    config: MeltanoCloudConfig = context.obj["config"]
    with CloudConfigClient(config=config) as client:
        client.create(secret_name=secret_name.upper(), secret_value=password)
        click.echo(f"Successfully created '{secret_name.upper()}'.")


@config_.command()
@click.argument("secret_name", type=str, required=True)
@click.password_option()
@click.pass_context
def update(context: click.Context, secret_name: str, password) -> None:
    """Update existing Cloud Config."""
    config: MeltanoCloudConfig = context.obj["config"]
    with CloudConfigClient(config=config) as client:
        client.update(secret_name=secret_name.upper(), secret_value=password)
        click.echo(f"Successfully updated '{secret_name.upper()}'.")


@config_.command()
@click.argument("secret_name", type=str, required=True)
@click.pass_context
def delete(context: click.Context, secret_name) -> None:
    """Delete existing Cloud Config."""
    config: MeltanoCloudConfig = context.obj["config"]
    with CloudConfigClient(config=config) as client:
        client.delete(secret_name=secret_name.upper())
        click.echo(f"Successfully deleted '{secret_name.upper()}'.")
