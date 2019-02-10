import logging
import click
import psycopg2
import psycopg2.sql

from meltano.core.db import DB, project_engine
from meltano.core.project import Project
from . import cli
from .params import db_options


@cli.group()
def schema():
    pass


@schema.command()
@click.argument("schema")
@click.argument("roles", nargs=-1, required=True)
@db_options
def create(schema, roles, engine_uri):
    project = Project.find()
    engine, _ = project_engine(project, engine_uri)

    DB.ensure_schema_exists(engine, schema, grant_roles=roles)
