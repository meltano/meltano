"""Loging into managed meltano via Github Auth."""
from __future__ import annotations

import click

from meltano.core.login_service import GithubLoginService

from . import cli
from .utils import InstrumentedCmd


@cli.command(cls=InstrumentedCmd, short_help="Login to managed meltano.")
@click.pass_context
def login(ctx):
    """Login to managed meltano."""
    login_service = GithubLoginService()
    code = login_service.request_codes()
    click.echo("Logging to managed meltano using Github")
    click.echo("")
    click.echo("Open https://github.com/login/device in your browser")
    click.echo(f"Enter the following code: {code['user_code']}")
    pass
