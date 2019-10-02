import logging
import click
import psycopg2
import psycopg2.sql

from meltano.core.db import DB, project_engine
from meltano.core.project import Project
from . import cli
from .params import project


@cli.group()
def schema():
    pass


@schema.command()
@click.argument("schema")
@click.argument("roles", nargs=-1, required=True)
@project()
def create(project, schema, roles):
    engine, _ = project_engine(project)

    DB.ensure_schema_exists(engine, schema, grant_roles=roles)
