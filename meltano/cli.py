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
    schema = None
    stream = MeltanoStream(sys.stdout.fileno(), schema=schema)


@root.command()
@click.argument('loader')
def load(loader):
    # this should register the module
    try:
        importlib.import_module("meltano.load.{}".format(loader))
    except ImportError as e:
        logging.error("Cannot find the loader {0}, you might need to install it (meltano-load-{0})".format(loader))
        exit(1)

    schema = None
    stream = MeltanoStream(sys.stdin.fileno(), schema=schema)

    loader = service.create_loader("com.meltano.load.{}".format(loader), stream)

    logging.info("Waiting for data...")
    loader.receive()
    logging.info("Integration complete.")


def main():
    logging.basicConfig(level=logging.DEBUG)
    root()
