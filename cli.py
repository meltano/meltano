import click
import os
from extract.fastly import FastlyExtractor
from extract.demo import DemoExtractor
from load.postgres.loader import PostgresLoader
from load.csv.loader import CsvLoader


@click.group()
def cli():
    pass


# TODO: to be generated from the file structure of /Extract/
EXTRACTOR_REGISTRY = {
    'fastly': FastlyExtractor,
    'demo': DemoExtractor
}

LOADER_REGISTRY = {
    'postgres': PostgresLoader,
    'csv': CsvLoader,
}


def run_extract(
        extractor_name,
        loader_name,
):
    """
    :param extractor_name:
    :param loader_name:
    :return:
    """
    click.echo(f"Loading and initializing extractor: {extractor_name}")
    extractor_class = EXTRACTOR_REGISTRY.get(extractor_name)
    if not extractor_class:
        raise Exception(
            f'Extractor {extractor_name} not found please specify one of the: {list(EXTRACTOR_REGISTRY.keys())}'
        )
    extractor = extractor_class()
    click.echo(f"Loading and initializing loader: {loader_name}")
    loader_class = LOADER_REGISTRY.get(loader_name)
    if not loader_class:
        raise Exception(
            f'Loader {loader_name} not found please specify one of the following: {list(LOADER_REGISTRY.keys())}'
        )
    click.echo("Starting extraction ... ")
    results = set()
    for entity in extractor.entities:
        loader = loader_class(
            extractor=extractor,
            entity_name=entity,
        )
        click.echo("Applying the schema ... ")
        loader.schema_apply()
        entity_dfs = extractor.extract(entity)
        for df in entity_dfs:
            click.echo("Got extractor results, loading them into the loader")
            results.add(loader.load(df=df, entity_name=entity))
    click.echo("Load done! Returning results ")
    return results


@cli.command()
@click.argument('extractor_name')
@click.option('--loader_name', default='postgres', help="Which loader should be used in this extraction")
# @click.option('-S', '--schema', required=True)
@click.option('-H', '--host',
              envvar='PG_ADDRESS',
              default='localhost',
              help="Database schema to use.")
@click.option('-p', '--port',
              type=int,
              envvar='PG_PORT',
              default=5432)
@click.option('-d', '-db', 'database',
              envvar='PG_DATABASE',
              help="Database to import the data to.")
@click.option('-u', '--username', envvar='PG_USERNAME',
              help="Specifies the user to connect to the database with.")
@click.password_option(envvar='PG_PASSWORD')
def extract(extractor_name, loader_name, host, port, database, username, password):
    run_extract(extractor_name, loader_name, host, port, database, username, password)


if __name__ == '__main__':
    cli()
