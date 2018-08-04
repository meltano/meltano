import argparse
import asyncio

from elt.cli import ActionEnum, parser_db_conn, parser_date_window, parser_output, parser_logging
from elt.utils import setup_logging, setup_db
from elt.db import db_open
from elt.schema import schema_apply
from elt.error import with_error_exit_code
from schema import describe_schema
from enum import Enum
from extract import Extractor


def action_export(args):
    schema = describe_schema(args)
    files = Extractor(schema, args).extract()


def action_schema_apply(args):
    schema = describe_schema(args)
    with db_open() as db:
        schema_apply(db, schema)


class Action(ActionEnum):
    EXPORT = ('export', action_export)
    APPLY_SCHEMA = ('apply_schema', action_schema_apply)


def parse():
    parser = argparse.ArgumentParser(
        description="Use the Zendesk Ticket API to retrieve ticket data.")

    parser_db_conn(parser)
    parser_date_window(parser)
    parser_output(parser)
    parser_logging(parser)

    parser.add_argument('action',
                        type=Action.from_str,
                        choices=list(Action),
                        default=Action.EXPORT,
                        help=("export: bulk export data into the output.\n"
                              "apply_schema: export the schema into a schema file."))

    return parser.parse_args()

@with_error_exit_code
def execute(args):
    args.action(args)

def main():
    args = parse()
    setup_logging(args)
    setup_db(args)
    execute(args)

main()
