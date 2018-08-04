import os
import logging
import argparse

from psycopg2 import OperationalError

from enum import Enum
from datetime import datetime

from elt.error import with_error_exit_code, Error
from elt.utils import setup_logging
from elt.cli import parser_logging

from db_extractor import DBExtractor


def action_export(args):
    if args.db_manifest == 'ci_stats':
        logging.info("Exporting {} Data for the past {} hours.".format(
                args.db_manifest,
                args.hours,
            )
        )
    else:
        logging.info("Exporting {} Data for the past {} days.".format(
                args.db_manifest,
                args.days,
            )
        )

    client = DBExtractor(args.db_manifest, args.days, args.hours)

    try:
        client.export()
        logging.info("Export completed Successfully.")
    except OperationalError as err:
        # Connections to the Version DB are refused once per day around 06:00
        # Don't fail the job if that's the case, just log the error and complete it
        if args.db_manifest == 'version' \
          and 'Connection refused' in str(err):
            logging.info("Export skipped due to Connection to Version DB refused.")
            logging.info("Error: {}".format(err))
        else:
            raise Error("DBExtractor.export() failed: {}".format(err))

def action_schema_apply(args):
    logging.info("Applying Schema")
    client = DBExtractor(args.db_manifest, args.days, args.hours)
    client.schema_apply()


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
        description="Extract Ping data (Version/CI Stats/Customers/Licenses).")

    parser.add_argument(
        '--db_manifest',
        required=True,
        choices=['version', 'customers', 'license', 'ci_stats'],
        help="Which DB manifest to use to get the export list."
    )

    parser.add_argument(
        '--run_after',
        type=int,
        choices=range(0, 24),
        help=("UTC hour after which the script can run.")
    )

    parser.add_argument(
        '--run_before',
        type=int,
        choices=range(1, 25),
        help=("UTC hour before which the script can run.")
    )

    parser.add_argument(
        '--days',
        type=int,
        help=("Specify the number of preceding days from the current time "
              "to get incremental records for (default=10). "
              "If not provided and ENV var PINGS_BACKFILL_DAYS is set, then "
              "it is used instead of the default value.")
    )

    parser.add_argument(
        '--hours',
        type=int,
        choices=range(1, 24),
        default=8,
        help=("Specify the number of preceding hours from the current time "
              "to get incremental records for (default=12). "
              "For special extractors with lots of results (like the ci_stats one).")
    )

    parser_logging(parser)

    parser.add_argument(
        'action',
        type=Action.from_str,
        choices=list(Action),
        default=Action.EXPORT,
        help=("export: export data into the Data Warehouse.\n"
              "apply_schema: create or update the schema in the DW.")
    )

    return parser.parse_args()


@with_error_exit_code
def execute(args):
    args.action(args)

def main():
    args = parse()
    setup_logging(args)

    # If environment var PINGS_BACKFILL_DAYS is set and no --days is provided
    #  then use it as the days param for the extractor
    backfill_days = os.getenv("PINGS_BACKFILL_DAYS")

    if args.days is None:
        if backfill_days and int(backfill_days) > 0:
            args.days = int(backfill_days)
        else:
            args.days = 10

    # If run_after and run_before arguments are provided, only run the
    #  extractor in the provided time window
    utc_hour = (datetime.utcnow()).hour

    if args.run_after and args.run_before \
      and not (args.run_after < utc_hour < args.run_before) :
        logging.info(
            'The Pings Extractor will not run: Only runs between'
            ' the hours of {}:00 UTC and {}:00 UTC.'.format(args.run_after,args.run_before)
        )
        return

    execute(args)


if __name__ == '__main__':
    main()
