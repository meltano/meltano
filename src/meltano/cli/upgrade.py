import logging
import os
import subprocess
from pathlib import Path

import click
import meltano
import psutil
from click_default_group import DefaultGroup
from meltano.core.db import project_engine
from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.migration_service import MigrationService
from meltano.core.project import Project
from meltano.core.upgrade_service import UpgradeService
from sqlalchemy import create_engine

from . import cli
from .params import pass_project


@cli.group(cls=DefaultGroup, default="all", default_if_no_args=True)
@pass_project()
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


@upgrade.command()
@click.option("--pip_url", type=str, envvar="MELTANO_UPGRADE_PIP_URL")
@click.option("--force", is_flag=True, default=False, envvar="MELTANO_UPGRADE_FORCE")
@click.pass_context
def package(ctx, **kwargs):
    ctx.obj["upgrade_service"].upgrade_package(**kwargs)


@upgrade.command()
@click.pass_context
def files(ctx):
    ctx.obj["upgrade_service"].update_files()


@upgrade.command()
@click.pass_context
def database(ctx):
    ctx.obj["upgrade_service"].migrate_database()


@upgrade.command()
@click.pass_context
def models(ctx):
    ctx.obj["upgrade_service"].compile_models()
