import click
import importlib
import sys
import logging

from meltano.common.service import MeltanoService
from meltano.stream import MeltanoStream


service = MeltanoService()
# print(service.auto_discover())

@click.group()
def root():
    pass


@root.command()
@click.argument('extractor')
def extract(extractor):
    # this should register the module
    try:
        importlib.import_module("meltano.extract.{}".format(extractor))
    except ImportError as e:
        logging.error("Cannot find the loader {0}, you might need to install it (meltano-load-{0})".format(extractor))

    schema = None
    stream = MeltanoStream(sys.stdout.fileno())
    extractor = service.create_extractor("com.meltano.extract.{}".format(extractor), stream.create_writer())

    logging.info("Extracting data...")
    extractor.run()
    logging.info("Extraction complete.")



@root.command()
@click.argument('loader')
def load(loader):
    # this should register the module
    try:
        importlib.import_module("meltano.load.{}".format(loader))
    except ImportError as e:
        logging.error("Cannot find the loader {0}, you might need to install it (meltano-load-{0})".format(loader))

    schema = None
    stream = MeltanoStream(sys.stdin.fileno())
    loader = service.create_loader("com.meltano.load.{}".format(loader), stream.create_reader())

    logging.info("Waiting for data...")
    loader.run()
    logging.info("Integration complete.")


def main():
    logging.basicConfig(level=logging.DEBUG)
    root()
