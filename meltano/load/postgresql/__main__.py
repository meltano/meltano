import asyncio
import sys
import argparse
import logging

from meltano.load.postgresql import PostgreSQLLoader
from elt import MeltanoService
from elt.schema import Schema
from elt.cli import parser_db_conn, parser_logging
from elt.utils import setup_logging, setup_db
from elt.stream import MeltanoStream


def parse():
    parser = argparse.ArgumentParser(
        description="Load data from stdin using PostgreSQL")

    parser_db_conn(parser)
    parser_logging(parser)

    parser.add_argument('manifest_file',
                        type=str,
                        help=("Manifest file to load."))

    return parser.parse_args()


def main(args):
    service = MeltanoService()
    # schema = service.load_schema(args.schema, args.manifest_file)
    schema = Schema(args.schema, [])

    # hardcode the schema at the moment, but this should be discovered at some point
    stream = MeltanoStream(sys.stdin.fileno(), schema=schema)
    loader = service.create_loader("com.meltano.load.postgresql", stream)

    logging.info("Waiting for data...")
    loader.receive()
    logging.info("Integration complete.")


if __name__ == '__main__':
    args = parse()

    setup_logging(args)
    setup_db(args)

    main(args)
