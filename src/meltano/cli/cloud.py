"""Meltano Cloud command."""

from __future__ import annotations

import typing as t
import webbrowser

import click

from meltano.cli.utils import InstrumentedCmd, InstrumentedGroup
from meltano.core.cloud.auth import CloudAuthService

if t.TYPE_CHECKING:
    from meltano.core.cloud.credentials import Credentials


@click.group(
    cls=InstrumentedGroup,
    name="cloud",
    short_help="Interact with Meltano Cloud.",
)
def cloud() -> None:
    """Interact with Meltano Cloud.

    Read more at https://docs.meltano.com/reference/command-line-interface#cloud
    """


@cloud.group(
    cls=InstrumentedGroup,
    name="auth",
    short_help="Authenticate with Meltano Cloud.",
)
def auth() -> None:
    """Authenticate with Meltano Cloud.

    Read more at https://docs.meltano.com/reference/command-line-interface#cloud
    """


def _echo_authorize_url(login_url: str, opened: bool) -> None:  # noqa: FBT001
    """Tell the user how to complete the login flow.

    Args:
        login_url: The Auth0 login URL.
        opened: Whether a browser was opened for the login URL.
    """
    if opened:
        click.echo("Opening your browser to log in to Meltano Cloud.")
        click.echo("If it did not open, visit the following link:")
    else:
        click.echo("Visit the following link to log in to Meltano Cloud:")

    click.secho(login_url, fg="green")
    click.echo()
    click.echo("Waiting for you to complete the login...")


def _describe(credentials: Credentials) -> str:
    """Describe the logged in user.

    Args:
        credentials: The credentials to describe.

    Returns:
        The user's email address, name, or subject claim.
    """
    claims = credentials.claims
    return claims.get("email") or claims.get("name") or claims.get("sub") or "unknown"


@auth.command(cls=InstrumentedCmd, short_help="Log in to Meltano Cloud.")
@click.option(
    "--no-browser",
    is_flag=True,
    default=False,
    help="Print the login URL instead of opening a browser.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Log in again even if you already have an active session.",
)
def login(*, no_browser: bool, force: bool) -> None:
    """Log in to Meltano Cloud.

    Opens the Meltano Cloud login page in your browser, and stores the
    resulting session for use by other Meltano Cloud commands.
    """
    service = CloudAuthService()

    if not force and (credentials := service.get_credentials()):
        click.secho(
            f"Already logged in to Meltano Cloud as {_describe(credentials)}.",
            fg="green",
        )
        click.echo("Use '--force' to log in again.")
        return

    credentials = service.login(
        open_browser=not no_browser,
        on_authorize_url=_echo_authorize_url,
    )
    click.secho(
        f"Successfully logged in to Meltano Cloud as {_describe(credentials)}.",
        fg="green",
    )


@auth.command(cls=InstrumentedCmd, short_help="Log out of Meltano Cloud.")
@click.option(
    "--web",
    is_flag=True,
    default=False,
    help="Also end the Meltano Cloud session in your browser.",
)
def logout(*, web: bool) -> None:
    """Log out of Meltano Cloud.

    Revokes the stored session and deletes it from this machine.
    """
    service = CloudAuthService()

    if not service.logout():
        click.echo("Not logged in to Meltano Cloud.")
        return

    if web:
        logout_url = service.browser_logout_url()
        if not webbrowser.open_new_tab(logout_url):
            click.echo("Visit the following link to complete logging out:")
            click.secho(logout_url, fg="green")

    click.secho("Successfully logged out of Meltano Cloud.", fg="green")


@auth.command(cls=InstrumentedCmd, short_help="Show the Meltano Cloud login status.")
@click.option(
    "--offline",
    is_flag=True,
    default=False,
    help="Do not contact Meltano Cloud to verify the stored session.",
)
def status(*, offline: bool) -> None:
    """Show whether you are logged in to Meltano Cloud, and as whom."""
    service = CloudAuthService()
    credentials = service.get_credentials()

    if credentials is None:
        click.secho("Not logged in to Meltano Cloud.", fg="yellow")
        click.echo("Run 'meltano cloud auth login' to log in.")
        raise click.exceptions.Exit(1)

    user = _describe(credentials)
    if not offline:
        user_info = service.get_user_info(credentials)
        user = user_info.get("email") or user_info.get("name") or user

    click.secho(f"Logged in to Meltano Cloud as {user}.", fg="green")
    if credentials.expires_at:
        click.echo(f"Session expires at:\t{credentials.expires_at.isoformat()}")
    click.echo(f"Credentials:\t\t{service.store.path}")
