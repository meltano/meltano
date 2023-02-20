"""Log in to Meltano Cloud."""

from __future__ import annotations

import click

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.cli import cloud


@cloud.command
@click.pass_context
def login(ctx: click.Context) -> None:
    """Log in to Meltano Cloud.

    Args:
        ctx: the click Context
    """
    auth: MeltanoCloudAuth = ctx.obj["auth"]
    auth.login()
    user_info = auth.get_user_info_response().json()
    click.secho(f"Logged in as {user_info['preferred_username']}", fg="green")
