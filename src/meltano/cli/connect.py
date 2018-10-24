import click
from meltano.support.database_add_service import DatabaseAddService
from urllib.parse import urlparse
from . import cli


@cli.group()
def connect():
    pass


@connect.command()
@click.option("--name", prompt="Warehouse connection name")
@click.option("--host", prompt="Warehouse host")
@click.option("--database", prompt="Warehouse database")
@click.option("--schema", prompt="Warehouse schema")
@click.option("--username", prompt="Warehouse username")
@click.option(
    "--password", prompt="Warehouse password", hide_input=True, confirmation_prompt=True
)
def add(name, host, database, schema, username, password):
    database_add_service = DatabaseAddService()
    database_add_service.add(
        name=name,
        host=host,
        database=database,
        schema=schema,
        username=username,
        password=password,
    )
    click.secho("ENV file updated", fg="green")


@connect.command()
def list():
    database_add_service = DatabaseAddService()
    database_add_service.list()
