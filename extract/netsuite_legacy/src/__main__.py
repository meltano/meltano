import argparse
import logging

from soap_api.netsuite_soap_client import NetsuiteClient
from soap_api.test import test_client
from soap_api.utils.extract_transaction_type import extract_transaction_type
from soap_api.utils.transaction_backlog import transaction_backlog

from elt.cli import parser_db_conn, parser_date_window, parser_output, parser_logging
from elt.utils import setup_logging, setup_db
from elt.db import db_open
from elt.schema import schema_apply
from elt.error import with_error_exit_code
from export import extract
from enum import Enum


def action_schema_apply(args):
    """
    Create or update the schema in our DW for all supported entities
    """
    supported_entity_classes = NetsuiteClient.supported_entity_classes()

    with db_open() as db:
        for entity in supported_entity_classes:
            schema = entity.schema.describe_schema(args)
            schema_apply(db, schema)


def action_export(args):
    """
    Extract the data for all supported entities and export them to our DW
    """

    # Initialize the SOAP client and fetch the wsdl
    client = NetsuiteClient()

    # Login
    if client.login():
        # Extract data for all supported Entities
        entities_to_export = client.export_supported_entities()

        extract(args, entities_to_export)

        # Extract the Transaction type and update the stored Transactions
        extract_transaction_type(args)
    else:
        logging.info("Could NOT login to NetSuite - Script Failed")


def action_extract_type(args):
    """
    Extract the type of transactions for a given date interval
      and update the stored Transactions with the fetched type.
    """
    extract_transaction_type(args)


def action_backlog(args):
    """
    Go back in time and fetch transactions not already fetched.
    """

    # Set the backlog range
    date_range = transaction_backlog(args)

    if date_range:
        args.days = None
        args.start = date_range[0].isoformat()
        args.end  = date_range[1].isoformat()

        # Initialize the SOAP client and fetch the wsdl
        client = NetsuiteClient()

        # Login
        if client.login():
            # Run the export script ONLY for Transactions
            entities_to_export = client.export_supported_entities(only_transactions=True)

            extract(args, entities_to_export)

            # Run the extract transaction type script for the same date interval
            extract_transaction_type(args)

            logging.info("Transaction BackLog completed Successfully")
        else:
            logging.info("Could NOT login to NetSuite - Script Failed")
    else:
        logging.info("Transaction BackLog completed Successfully: No more data to fetch")

def action_test(args):
    """
    Test the core aspects of NetSuite ELT:
     Init Client, fetch WSDL, check that credentials are set correctly and login,
     fetch single record, fetch all records for a simple entity,
     search with paging enabled and incrimentally fetch more records.
    """
    test_client(args)


class Action(Enum):
    EXPORT = ('export', action_export)
    APPLY_SCHEMA = ('apply_schema', action_schema_apply)
    TEST = ('test', action_test)
    EXTRACT_TYPE = ('extract_type', action_extract_type)
    BACKLOG = ('backlog', action_backlog)

    @classmethod
    def from_str(cls, name):
        return cls[name.upper()]

    def __str__(self):
        return self.value[0]

    def __call__(self, args):
        return self.value[1](args)


def parse():
    parser = argparse.ArgumentParser(
        description="Use the NetSuite API to retrieve account data.")

    parser_db_conn(parser)
    parser_date_window(parser)
    parser_output(parser)
    parser_logging(parser)

    parser.add_argument('action',
                        type=Action.from_str,
                        choices=list(Action),
                        default=Action.EXPORT,
                        help=("export: bulk export data into the output.\n"
                              "apply_schema: export the schema into a schema file.\n"
                              "test: test the netsuite client.\n"
                              "extract_type: extract the type for fetched Transactions.\n"
                              "backlog: fetch transactions not already fetched (requires --days arg)."))

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
