"""Project Upgrade CLI."""

from __future__ import annotations

import os

import click

from meltano.core.db import project_engine
from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.upgrade_service import UpgradeService

from . import cli
from .params import pass_project
from .utils import InstrumentedCmd, InstrumentedDefaultGroup


@cli.group(
    cls=InstrumentedDefaultGroup,
    default="all",
    default_if_no_args=True,
    short_help="Upgrade Meltano and your entire project to the latest version.",
)
@pass_project()
@click.pass_context
def upgrade(ctx, project):
    """
    Upgrade Meltano and your entire project to the latest version.

    When called without arguments, this will:

    - Upgrade the meltano package\n
    - Update files managed by file bundles\n
    - Apply migrations to system database\n

    Read more at https://docs.meltano.com/reference/command-line-interface#upgrade
    """
    engine, _ = project_engine(project)
    upgrade_service = UpgradeService(engine, project)
    ctx.obj["upgrade_service"] = upgrade_service


@upgrade.command(  # noqa: WPS125
    cls=InstrumentedCmd,
    short_help="Upgrade Meltano and your entire project to the latest version.",
)
@click.option(
    "--pip_url", type=str, envvar="MELTANO_UPGRADE_PIP_URL", help="Meltano pip URL."
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    envvar="MELTANO_UPGRADE_FORCE",
    help="Force upgrade.",
)
@click.option(
    "--skip-package",
    is_flag=True,
    default=False,
    help="Skip updating the Meltano package.",
)
@click.pass_context
def all(ctx, pip_url, force, skip_package):
    """
    Upgrade Meltano and your entire project to the latest version.

    When called without arguments, this will:

    - Upgrade the meltano package\n
    - Update files managed by file bundles\n
    - Apply migrations to system database\n

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#upgrade
    """
    project = ctx.obj["project"]
    upgrade_service = ctx.obj["upgrade_service"]

    if skip_package:
        upgrade_service.update_files()

        click.echo()
        upgrade_service.migrate_database()

        click.echo()

        if not os.getenv("MELTANO_PACKAGE_UPGRADED", default=False):
            click.echo()
            click.secho("Your Meltano project has been upgraded!", fg="green")
    else:
        package_upgraded = upgrade_service.upgrade_package(pip_url=pip_url, force=force)
        if package_upgraded:
            # Shell out instead of calling `upgrade_service` methods to
            # ensure the latest code is used.
            click.echo()
            run = MeltanoInvoker(project).invoke(
                ["upgrade", "--skip-package"],
                env={"MELTANO_PACKAGE_UPGRADED": "true"},
            )

            if run.returncode == 0:
                click.echo()
                click.secho(
                    "Meltano and your Meltano project have been upgraded!",
                    fg="green",
                )
        else:
            click.echo(
                "Then, run `meltano upgrade --skip-package` to upgrade your project based on the latest version."
            )


@upgrade.command(cls=InstrumentedCmd, short_help="Upgrade the Meltano package only.")
@click.option(
    "--pip_url", type=str, envvar="MELTANO_UPGRADE_PIP_URL", help="Meltano pip URL."
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    envvar="MELTANO_UPGRADE_FORCE",
    help="Force upgrade.",
)
@click.pass_context
def package(ctx, **kwargs):
    """Upgrade the Meltano package only."""
    ctx.obj["upgrade_service"].upgrade_package(**kwargs)


@upgrade.command(
    cls=InstrumentedCmd, short_help="Update files managed by file bundles only."
)
@click.pass_context
def files(ctx):
    """Update files managed by file bundles only."""
    ctx.obj["upgrade_service"].update_files()


@upgrade.command(
    cls=InstrumentedCmd, short_help="Apply migrations to system database only."
)
@click.pass_context
def database(ctx):
    """Apply migrations to system database only."""
    ctx.obj["upgrade_service"].migrate_database()
