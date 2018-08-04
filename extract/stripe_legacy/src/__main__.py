import argparse

from sqlalchemy import DDL, event

from elt.cli import (
    parser_db_conn,
    parser_date_window,
    parser_output,
    parser_logging,
    DateWindow,
)
from elt.utils import setup_logging, setup_db
from elt.error import with_error_exit_code


def action_schema_apply():
    event.listen(
        Base.metadata,
        'before_create',
        DDL("CREATE SCHEMA IF NOT EXISTS {}".format(args.schema))
    )
    Base.metadata.create_all(engine)


def extract():
    date_window = DateWindow(args, formatter=lambda x: int(x.timestamp()))
    Extractor(args, *date_window.formatted_range()).load()


ACTIONS = {
    'export': extract,
    'apply_schema': action_schema_apply,
}


def parse():
    parser = argparse.ArgumentParser(
        description="Use the Stripe API to retrieve payment, data.")
    parser_db_conn(parser)
    parser_date_window(parser)
    parser_output(parser)
    parser_logging(parser)

    parser.add_argument(
        'action',
        type=str,
        choices=ACTIONS,
        default='export',
        help=("export: bulk export data into the output.\n"
              "apply_schema: export the schema into a schema file.")
    )
    return parser.parse_args()


args = parse()
if args.schema == 'stripe_githost':
    api_key_name = 'GITHOST_STRIPE_API_KEY_SK'
elif args.schema == 'stripe_about_gitlab':
    api_key_name = 'ABOUT_GITLAB_STRIPE_API_KEY_SK'
else:
    raise argparse.ArgumentError('schema must be one of: [stripe_githost, stripe_about_gitlab]')

# We import args in the schema file, thus it needs to be initialized before the import
from schema import Base
from export import Extractor, engine


def main():
    setup_logging(args)
    setup_db(args)
    action = with_error_exit_code(
        ACTIONS.get(args.action)
    )
    action()


main()
