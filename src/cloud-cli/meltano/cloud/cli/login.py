"""Login to or logout from Meltano Cloud."""

from __future__ import annotations

import asyncio
import typing as t

import click

from meltano.cloud.cli import cloud
from meltano.cloud.cli.base import pass_context

if t.TYPE_CHECKING:
    from meltano.cloud.cli.base import MeltanoCloudCLIContext


@cloud.command
@pass_context
def login(context: MeltanoCloudCLIContext) -> None:
    """Log in to Meltano Cloud."""
    asyncio.run(context.auth.login())
    user_info = asyncio.run(context.auth.get_user_info_json())
    click.secho(f"Logged in as {user_info['preferred_username']}", fg="green")


@cloud.command
@pass_context
def logout(context: MeltanoCloudCLIContext) -> None:
    """Log out of Meltano Cloud."""
    asyncio.run(context.auth.logout())
