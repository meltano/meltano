import click
import importlib
import sys
import logging
import functools
import os
import json
import pandas as pd

from meltano.common.service import MeltanoService
from meltano.common.manifest_reader import ManifestReader
from meltano.common.manifest_writer import ManifestWriter
from meltano.common.manifest import Manifest
from meltano.common.db import DB
from meltano.common.utils import setup_db, pop_all
from meltano.schema import schema_apply
from meltano.cli.params import MANIFEST_TYPE


service = MeltanoService()
# print(service.auto_discover())


def build_extractor(name):
    try:
        # this should register the module
        importlib.import_module("extract.{}".format(name))
    except ImportError as e:
        logging.error("Cannot find the extractor {0}, you might need to install it (meltano-extract-{0})".format(name))

    schema = None
    extractor = service.create_extractor("com.meltano.extract.{}".format(name))
    return extractor


def build_loader(name):
    # this should register the module
    try:
        importlib.import_module("load.{}".format(name))
    except ImportError as e:
        logging.error("Cannot find the loader {0}, you might need to install it (meltano-load-{0})".format(name))

    schema = None
    loader = service.create_loader("com.meltano.load.{}".format(name))
    return loader


def meltano_entity_dataframes_to_json(result):
    json_export = [{'EntityName': entity['EntityName'],
               'DataFrame': entity['DataFrame'].to_json(orient='table')} for entity in result]

    return json.dumps(json_export)

def json_to_meltano_entity_dataframes(json_str):
    result = []

    json_import = json.loads(json_str)

    for entity in json_import:
        result.append(
              {
                'EntityName': entity['EntityName'],
                'DataFrame': pd.read_json(entity['DataFrame'], orient='table')
              }
            )

    return result


def db_options(func):
    @click.option('-S', '--schema',
                  required=True)

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
                  default=lambda: os.getenv('USER', ''),
                  help="Database to import the data to.")

    @click.option('-T', '--table', 'table_name',
                  help="Table to import the data to.")

    @click.option('-u', '--user',
                  envvar='PG_USERNAME',
                  default=lambda: os.getenv('USER', ''),
                  help="Specifies the user to connect to the database with.")
    @click.password_option(envvar='PG_PASSWORD')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = pop_all(("schema", "host", "port", "database", "table_name", "user", "password"), kwargs)
        DB.setup(**config)
        return func(*args, **kwargs)
    return wrapper


@click.group()
def root():
    pass


@root.command()
@click.argument('extractor')
def extract(extractor):
    extractor = build_extractor(extractor)

    logging.info("Extracting data...")

    result = extractor.extract()

    logging.info("Extraction complete.")

    json_export = meltano_entity_dataframes_to_json(result)
    print('{}'.format(json_export))

@root.command()
@click.argument('loader')
@click.option('--manifest',
              help="The db manifest yaml file")
def load(loader, manifest): #, manifest):
    # Get the results from the previous step
    json_import = ''

    logging.info("Waiting for data...")
    for line in sys.stdin:
        json_import += line

    result = json_to_meltano_entity_dataframes(json_import)

    # Dynamically instantiate the Loader
    loader = build_loader(loader)

    # Apply the schema defined in the manifest file
    logging.info("Applying schema defined in manifest {}...".format(manifest))

    loader.schema_apply(
        manifest=manifest
    )

    # Load the Data
    logging.info("Loading data...")

    for entity in result:
        logging.info('Loading entity: {}'.format(entity['EntityName']))

        loader.load(
            entity_name=entity['EntityName'],
            dataframe=entity['DataFrame']
        )

        # df = entity['DataFrame']
        # print('')
        # print('DataFrame Schema:')
        # print('')
        # print('{}'.format(df.dtypes))

        # print('')
        # print('DataFrame Values:')
        # print('')
        # print('{}'.format(df))

    logging.info("Load complete.")


@root.command()
@db_options
@click.argument('manifest', type=MANIFEST_TYPE)
def apply_schema(manifest):
    with DB.open() as db:
        schema_apply(db, manifest.as_schema())
