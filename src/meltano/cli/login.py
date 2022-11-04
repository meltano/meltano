"""Loging into managed meltano via Github Auth."""
import click

from .utils import InstrumentedCmd

from . import cli

from meltano.core.login_service import GithubLoginService


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
