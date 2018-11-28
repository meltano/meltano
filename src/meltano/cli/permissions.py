import logging
import click
import sys

from meltano.core.permissions import grant_permissions, SpecLoadingError
from . import cli


@cli.group()
def permissions():
    """Database permission related commands."""
    pass


@permissions.command()
@click.option(
    "--db",
    help="The type of the target DB the specifications file is for.",
    type=click.Choice(["postgres", "snowflake"]),
    required=True,
)
@click.option("--spec", help="The specifications file path.", required=True)
@click.option("--dry", help="Do not actually run, just check.", is_flag=True)
def grant(db, spec, dry):
    """Grant the permissions provided in --spec specification file."""
    try:
        if not dry:
            click.secho("Error: Only dry runs are supported at the moment", fg="red")
            sys.exit(1)

        sql_commands = grant_permissions(db, spec, dry_run=dry)

        click.secho()
        if dry:
            click.secho("SQL Commands generated for given spec file:")
        else:
            click.secho("!! SQL Commands that were excecuted: !!")

        for command in sql_commands:
            click.secho(f"{command};", fg="green")
            click.secho()
    except SpecLoadingError as exc:
        for line in str(exc).splitlines():
            click.secho(line, fg="red")
        sys.exit(1)
