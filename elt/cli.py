import psycopg2
import getpass
import os
import datetime
import logging

from enum import Enum
from argparse import ArgumentParser


class OptionEnum(Enum):
    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other

    def __hash__(self):
        return hash(self.value)


class ActionEnum(Enum):
    @classmethod
    def from_str(cls, name):
        return cls[name.upper()]

    def __str__(self):
        return self.value[0]

    def __call__(self, args):
        return self.value[1](args)


class ExportOutput(OptionEnum):
    DB = "db"
    FILE = "file"


class Password:
    DEFAULT = 'PG_PASSWORD environment variable.'

    def __init__(self, value):
        if value == self.DEFAULT:
            value = os.getenv('PG_PASSWORD', None)
        if not value:
            value = getpass.getpass()
        self.value = value

    def __str__(self):
        return self.value


class LogLevel:
    LOG_LEVEL_STRINGS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

    def parse(value):
        log_level_int = getattr(logging, value, logging.INFO)
        # check the logging log_level_choices have not changed from our expected values
        assert isinstance(log_level_int, int)
        return log_level_int


class DateWindow:
    def parse_date(value):
        if value is None:
            return datetime.date.today()

        return datetime.datetime.strptime(value, "%Y-%m-%d")

    def __init__(self, args, formatter=datetime.datetime.isoformat):
        self.formatter = formatter

        if args.days is not None:
            today = datetime.date.today()
            days = lambda d: datetime.timedelta(days=d)

            # Tomorrow at 00:00:00 UTC
            self.end = datetime.datetime.combine(today + days(1),
                                                 datetime.time())

            # N days ago at 00:00:00 UTC
            self.start = datetime.datetime.combine(today - days(args.days),
                                                   datetime.time())
        else:
            self.start = DateWindow.parse_date(args.start)
            self.end = DateWindow.parse_date(args.end)

    def range(self):
        return (self.start, self.end)

    def formatted_range(self):
        return map(self.formatter, self.range())


def parser_db_conn(parser: ArgumentParser, required=True):
    current_user = os.getenv('USER')

    parser.add_argument('-S', '--schema', required=required,
                        help="Database schema to use.")

    parser.add_argument('-T', '--table', dest='table_name',
                        help="Table to import the data to.")

    parser.add_argument('-d', '--db', dest='database',
                        default=os.getenv('PG_DATABASE', current_user),
                        help="Database to import the data to.")

    parser.add_argument('-H', '--host', default=os.getenv('PG_ADDRESS', 'localhost'),
                        help="Database host address.")

    parser.add_argument('-p', '--port', default=os.getenv('PG_PORT', 5432),
                        help="Database port.")

    parser.add_argument('-u', '--user', default=os.getenv('PG_USERNAME', current_user),
                        help="Specifies the user to connect to the database with.")

    parser.add_argument('-W', '--password', type=Password, help='Specify password',
                        default=Password.DEFAULT)


def parser_date_window(parser: ArgumentParser):
    parser.add_argument('--days',
                        type=int,
                        help="Specify the number of preceding days from the current time to get incremental records for. Only used for lead records.")

    parser.add_argument('-b',
                        dest="start",
                        help="The start date in the isoformat of 2018-01-01. This will be formatted properly downstream.")

    parser.add_argument('-e',
                        dest="end",
                        help="The end date in the isoformat of 2018-02-01. This will be formatted properly downstream.")


def parser_output(parser: ArgumentParser):
    parser.add_argument('-o',
                        dest="output",
                        type=ExportOutput,
                        choices=list(ExportOutput),
                        default=ExportOutput.DB,
                        help="Specifies the output store for the extracted data.")

    parser.add_argument('--nodelete',
                        action='store_true',
                        help="If argument is provided, the CSV file generated will not be deleted.")

    parser.add_argument('-F', '--output-file',
                        dest="output_file",
                        help="Specifies the output to write the output to.")


def parser_logging(parser: ArgumentParser):
    parser.add_argument('--log-level',
                        dest="log_level",
                        type=LogLevel.parse,
                        default=logging.INFO,
                        help="Specifies the log level.")
