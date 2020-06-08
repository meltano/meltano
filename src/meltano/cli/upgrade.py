import os
import click
import subprocess
import psutil
import meltano
import logging
from pathlib import Path
from sqlalchemy import create_engine
from click_default_group import DefaultGroup

from meltano.core.project import Project
from meltano.core.db import project_engine
from meltano.core.migration_service import MigrationService
from meltano.core.upgrade_service import UpgradeService, UpgradeError
from . import cli
from .params import project, db_options


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
def all(ctx, **kwargs):
    try:
        ctx.obj["upgrade_service"].upgrade(**kwargs)
    except UpgradeError as up:
        click.secho(str(up), fg="red")
        raise click.Abort()


@upgrade.command()
@click.option("--pip_url", type=str, envvar="MELTANO_UPGRADE_PIP_URL")
@click.option("--force", is_flag=True, default=False, envvar="MELTANO_UPGRADE_FORCE")
@click.pass_context
def package(ctx, **kwargs):
    try:
        ctx.obj["upgrade_service"].upgrade_package(**kwargs)
    except UpgradeError as up:
        click.secho(str(up), fg="red")
        raise click.Abort()


@upgrade.command()
@click.pass_context
def files(ctx):
    try:
        ctx.obj["upgrade_service"].update_files()
    except UpgradeError as up:
        click.secho(str(up), fg="red")
        raise click.Abort()


@upgrade.command()
@click.pass_context
def database(ctx):
    try:
        ctx.obj["upgrade_service"].migrate_database()
    except UpgradeError as up:
        click.secho(str(up), fg="red")
        raise click.Abort()


@upgrade.command()
@click.pass_context
def models(ctx):
    try:
        ctx.obj["upgrade_service"].compile_models()
    except UpgradeError as up:
        click.secho(str(up), fg="red")
        raise click.Abort()
