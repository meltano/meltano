"""User account management CLI."""

from __future__ import annotations

import click

from meltano.api.app import create_app

from . import cli
from .params import pass_project
from .utils import InstrumentedCmd, InstrumentedGroup


@cli.group(
    cls=InstrumentedGroup,
    invoke_without_command=True,
    short_help="Manage Meltano user accounts.",
)
@pass_project(migrate=True)
@click.pass_context
def user(ctx, project):
    """
    Manage Meltano user accounts.

    TIP: This command is only relevant when Meltano is run with authentication enabled.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#user
    """
    ctx.obj["project"] = project


@user.command(cls=InstrumentedCmd, short_help="Create a Meltano user account.")
@click.argument("username")
@click.argument("password")
@click.option(
    "--overwrite",
    "-f",
    is_flag=True,
    default=False,
    help="Update the user instead of creating a new one.",
)
@click.option(
    "--role",
    "-G",
    multiple=True,
    default=[],
    help="Add the user to the role. Meltano ships with two built-in roles: admin and regular.",
)
@click.pass_context
def add(ctx, username, password, role, **flags):
    """
    Create a Meltano user account.

    TIP: This command is only relevant when Meltano is run with authentication enabled.
    """
    app = create_app()

    from flask_security.utils import hash_password

    from meltano.api.security.identity import users

    try:
        with app.app_context():
            # make sure our User doesn't already exist
            if not flags["overwrite"] and users.get_user(username):
                raise Exception(
                    f"User '{username}' already exists. Use --overwrite to update it."
                )

            # make sure all roles exists
            roles = []
            for role_name in role:
                this_role = users.find_role(role_name)
                if not this_role:
                    raise Exception(f"Role '{role_name}' does not exists.")

                roles.append(this_role)

            current_user = users.get_user(username) or users.create_user(
                username=username
            )

            current_user.password = hash_password(password)
            current_user.roles = roles

            # for some reason the scoped_session doesn't trigger the commit
            users.db.session.commit()
    except Exception as err:
        click.secho(f"Could not create user '{username}': {err}", fg="red")
        raise click.Abort from err
