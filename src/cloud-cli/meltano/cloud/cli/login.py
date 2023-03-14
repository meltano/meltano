"""Login to or logout from Meltano Cloud."""

from __future__ import annotations

import asyncio

import click

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.cli import cloud


@cloud.command
@click.pass_context
def login(ctx: click.Context) -> None:
    """Log in to Meltano Cloud."""  # noqa: DAR101
    auth: MeltanoCloudAuth = ctx.obj["auth"]
    asyncio.run(auth.login())
    user_info = asyncio.run(auth.get_user_info_json())
    click.secho(f"Logged in as {user_info['preferred_username']}", fg="green")


@cloud.command
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Log out of Meltano Cloud."""  # noqa: DAR101
    auth: MeltanoCloudAuth = ctx.obj["auth"]
    asyncio.run(auth.logout())
