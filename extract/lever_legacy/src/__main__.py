import argparse
import schema.candidate as candidate

from elt.cli import parser_db_conn, parser_date_window, parser_output, parser_logging
from elt.utils import setup_logging, setup_db
from elt.db import db_open
from elt.schema import schema_apply
from elt.error import with_error_exit_code
from export import extract
from enum import Enum


def action_export(args):
    extract(args)


def action_schema_apply(args):
    schema = candidate.describe_schema(args)
    with db_open() as db:
        schema_apply(db, schema)


class Action(Enum):
    EXPORT = ('export', action_export)
    APPLY_SCHEMA = ('apply_schema', action_schema_apply)

    @classmethod
    def from_str(cls, name):
        return cls[name.upper()]

    def __str__(self):
        return self.value[0]

    def __call__(self, args):
        return self.value[1](args)


def parse():
    parser = argparse.ArgumentParser(
        description="Use the Lever API to retrieve Application data.")

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

    parser.add_argument('--only_offers',
                        action='store_true',
                        help="Only export candidates that received an offer.")

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
