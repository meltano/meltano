import click
import logging

from . import cli
from .params import project
from flask_security.utils import hash_password
from meltano.api.app import create_app
from meltano.core.utils import identity


@cli.group(invoke_without_command=True)
@project(migrate=True)
@click.pass_context
def user(ctx, project):
    ctx.obj["project"] = project


@user.command()
@click.argument("username")
@click.argument("password")
@click.option("--overwrite", "-f", is_flag=True, default=False)
@click.option("--role", "-G", multiple=True)
@click.pass_context
def add(ctx, username, password, role=[], **flags):
    app = create_app()

    from meltano.api.security import users

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
                r = users.find_role(role_name)
                if not r:
                    raise Exception(f"Role '{role_name}' does not exists.")

                roles.append(r)

            current_user = users.get_user(username) or users.create_user(
                username=username
            )
            current_user.password = hash_password(password)
            current_user.roles = roles

            # for some reason the scoped_session doesn't trigger the commit
            users.db.session.commit()
    except Exception as err:
        click.secho(f"Could not create user '{username}': {err}", fg="red")
        click.Abort()
