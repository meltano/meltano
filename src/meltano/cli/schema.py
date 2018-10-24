import logging
import click
import psycopg2
import psycopg2.sql

from meltano.core.db import db_open
from . import cli
from .params import db_options


@cli.group()
@db_options
def schema():
    pass


@schema.command()
@click.argument("schema")
@click.argument("roles", nargs=-1, required=True)
def create(schema, roles):
    with db_open() as db:
        db.ensure_schema_exists(schema, grant_roles=roles)
