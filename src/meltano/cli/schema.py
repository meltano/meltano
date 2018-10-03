import os
import logging
import click
import psycopg2
import psycopg2.sql

from meltano.support.db import db_open
from . import cli
from .params import db_options


def ensure_schema_exists(db_conn, schema_name, grant_roles=()):
    """
    Make sure that the given schema_name exists in the database
    If not, create it

    :param db_conn: psycopg2 database connection
    :param schema_name: database schema
    """
    cursor = db_conn.cursor()
    schema_identifier = psycopg2.sql.Identifier(schema_name)
    group_identifiers = psycopg2.sql.SQL(",").join(
        map(psycopg2.sql.Identifier, grant_roles)
    )

    create_schema = psycopg2.sql.SQL("""
    CREATE SCHEMA IF NOT EXISTS {}
    """).format(schema_identifier)

    grant_select_schema = psycopg2.sql.SQL("""
    ALTER DEFAULT PRIVILEGES IN SCHEMA {} GRANT SELECT ON TABLES TO {}
    """).format(schema_identifier, group_identifiers)

    grant_usage_schema = psycopg2.sql.SQL("""
    GRANT USAGE ON SCHEMA {} TO {}
    """).format(schema_identifier, group_identifiers)

    cursor.execute(create_schema)
    cursor.execute(grant_select_schema)
    cursor.execute(grant_usage_schema)

    db_conn.commit()

    logging.info("Schema {} has been created successfully.".format(schema_name))
    for role in grant_roles:
        logging.info("Usage has been granted for role: {}.".format(role))


@cli.group()
@db_options
def schema():
    pass


@schema.command()
@click.argument("schema")
@click.argument("roles", nargs=-1, required=True)
def create(schema, roles):
    with db_open() as db:
        ensure_schema_exists(db, schema, grant_roles=roles)
