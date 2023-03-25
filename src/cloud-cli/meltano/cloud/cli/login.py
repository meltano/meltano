"""Login to or logout from Meltano Cloud."""

from __future__ import annotations

import typing as t

import click

from meltano.cloud.cli.base import pass_context, run_async

if t.TYPE_CHECKING:
    from meltano.cloud.cli.base import MeltanoCloudCLIContext


@click.command
@pass_context
@run_async
async def login(context: MeltanoCloudCLIContext) -> None:
    """Log in to Meltano Cloud."""
    await context.auth.login()
    user_info = await context.auth.get_user_info_json()
    click.secho(f"Logged in as {user_info['preferred_username']}", fg="green")


@click.command
@pass_context
@run_async
async def logout(context: MeltanoCloudCLIContext) -> None:
    """Log out of Meltano Cloud."""
    await context.auth.logout()
