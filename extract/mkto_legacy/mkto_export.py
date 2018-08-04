import argparse
import sys

from enum import Enum
from elt.schema import schema_apply
from elt.error import with_error_exit_code
from elt.utils import setup_logging, setup_db
from elt.db import db_open
from elt.cli import parser_db_conn, parser_date_window, parser_output, parser_logging
from mkto_tools.mkto_bulk import bulk_export
from mkto_tools.mkto_leads import describe_schema as describe_leads_schema
from mkto_tools.mkto_activities import describe_schema as describe_activities_schema
from mkto_tools.mkto_token import get_token
from config import MarketoSource, ExportType


schema_func_map = {
    MarketoSource.LEADS: describe_leads_schema,
    MarketoSource.ACTIVITIES: describe_activities_schema,
}


def action_token(args):
    print(get_token())


def action_schema_apply(args):
    schema = schema_func_map[args.source](args)
    with db_open() as db:
        schema_apply(db, schema)


class MarketoAction(Enum):
    EXPORT = ('export', bulk_export)
    APPLY_SCHEMA = ('apply_schema', action_schema_apply)
    TOKEN = ('token', action_token)

    @classmethod
    def from_str(cls, name):
        return cls[name.upper()]

    def __str__(self):
        return self.value[0]

    def __call__(self, args):
        return self.value[1](args)


@with_error_exit_code
def execute(args):
    args.action(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Use the Marketo Bulk Export to get Leads or Activities")

    parser_db_conn(parser, required=False)
    parser_date_window(parser)
    parser_output(parser)
    parser_logging(parser)

    parser.add_argument('action',
                        type=MarketoAction.from_str,
                        choices=list(MarketoAction),
                        default=MarketoAction.EXPORT,
                        help=("export: bulk export data into the output.\n"
                              "describe: export the schema into a schema file."))

    parser.add_argument('-s',
                        dest="source",
                        type=MarketoSource,
                        choices=list(MarketoSource),
                        required=True,
                        help="Specifies either leads or activies records.")

    parser.add_argument('-t',
                        dest="type",
                        type=ExportType,
                        choices=list(ExportType),
                        default=ExportType.CREATED,
                        help="Specifies either created or updated. Use updated for incremental pulls. Default is created.")

    args = parser.parse_args()
    setup_logging(args)
    setup_db(args)

    execute(args)
