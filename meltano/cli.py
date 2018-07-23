import click
import importlib
import sys
import logging

from meltano.common.service import MeltanoService
from meltano.common.manifest_reader import ManifestReader
from meltano.common.manifest_writer import ManifestWriter
from meltano.common.manifest import Manifest

from meltano.stream import MeltanoStream


service = MeltanoService()
# print(service.auto_discover())

def load_extractor(name):
    # this should register the module
    try:
        importlib.import_module("meltano.extract.{}".format(name))
    except ImportError as e:
        logging.error("Cannot find the loader {0}, you might need to install it (meltano-load-{0})".format(name))

    schema = None
    stream = MeltanoStream(sys.stdout.fileno())
    extractor = service.create_extractor("com.meltano.extract.{}".format(name), stream.create_writer())
    return extractor


@click.group()
def root():
    pass


@root.command()
@click.argument('manifest')
def describe(manifest):
    reader = ManifestReader('describe')
    with open(manifest, 'r') as file:
        manifest = reader.load(file)
        print(manifest)


@root.command()
@click.argument('extractor')
@click.argument('output')
def discover(extractor, output):
    extractor = load_extractor(extractor)
    manifest = Manifest(output, extractor,
                        entities=extractor.discover_entities())

    with open(output + ".yaml", 'w') as out:
        writer = ManifestWriter(out)
        writer.write(manifest)


@root.command()
@click.argument('extractor')
def extract(extractor):
    extractor = load_extractor(extractor)

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
