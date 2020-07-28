import os
import click
import subprocess
import psutil
import meltano
import logging
from pathlib import Path
from sqlalchemy import create_engine
from click_default_group import DefaultGroup

from . import cli
from .params import project
from .utils import CliError

from meltano.core.project import Project
from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.db import project_engine
from meltano.core.migration_service import MigrationService
from meltano.core.upgrade_service import UpgradeService, UpgradeError


@cli.group(cls=DefaultGroup, default="all", default_if_no_args=True)
@project()
@click.pass_context
def upgrade(ctx, project):
    engine, _ = project_engine(project)
    upgrade_service = UpgradeService(engine, project)
    ctx.obj["upgrade_service"] = upgrade_service


@upgrade.command()
@click.option("--pip_url", type=str, envvar="MELTANO_UPGRADE_PIP_URL")
@click.option("--force", is_flag=True, default=False, envvar="MELTANO_UPGRADE_FORCE")
@click.option("--skip-package", is_flag=True, default=False)
@click.pass_context
def all(ctx, pip_url, force, skip_package):
    project = ctx.obj["project"]
    upgrade_service = ctx.obj["upgrade_service"]

    try:
        if skip_package:
            upgrade_service.update_files()

            click.echo()
            upgrade_service.migrate_database()

            click.echo()
            upgrade_service.compile_models()

            if not os.getenv("MELTANO_PACKAGE_UPGRADED", False):
                click.echo()
                click.secho("Your Meltano project has been upgraded!", fg="green")
        else:
            package_upgraded = upgrade_service.upgrade_package(
                pip_url=pip_url, force=force
            )
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
    except UpgradeError as err:
        raise CliError(str(err)) from err


@upgrade.command()
@click.option("--pip_url", type=str, envvar="MELTANO_UPGRADE_PIP_URL")
@click.option("--force", is_flag=True, default=False, envvar="MELTANO_UPGRADE_FORCE")
@click.pass_context
def package(ctx, **kwargs):
    try:
        ctx.obj["upgrade_service"].upgrade_package(**kwargs)
    except UpgradeError as err:
        raise CliError(str(err)) from err


@upgrade.command()
@click.pass_context
def files(ctx):
    try:
        ctx.obj["upgrade_service"].update_files()
    except UpgradeError as err:
        raise CliError(str(err)) from err


@upgrade.command()
@click.pass_context
def database(ctx):
    try:
        ctx.obj["upgrade_service"].migrate_database()
    except UpgradeError as err:
        raise CliError(str(err)) from err


@upgrade.command()
@click.pass_context
def models(ctx):
    try:
        ctx.obj["upgrade_service"].compile_models()
    except UpgradeError as err:
        raise CliError(str(err)) from err
