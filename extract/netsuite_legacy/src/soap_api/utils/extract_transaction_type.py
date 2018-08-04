import logging
import psycopg2
import psycopg2.sql

from elt.cli import DateWindow
from elt.db import db_open
from datetime import datetime

from soap_api.netsuite_soap_client import NetsuiteClient
from soap_api.transaction import Transaction


def extract_transaction_type(args):
    """
    Extract the Transaction {internalId, type} for a given date interval
      and update the stored Transactions with the fetched type.
    """
    transaction_types = {}
    window = DateWindow(args, formatter=datetime.date)
    start_time, end_time = window.formatted_range()

    logging.info("NetSuite Extract Transaction Types Started")
    logging.info("Date interval = [{},{}]".format(start_time, end_time))

    # Initialize the SOAP client and fetc the wsdl
    client = NetsuiteClient()

    # Login
    if client.login():
        entity = Transaction(client)

        # Fetch all the transaction types for the given date intervall
        response = entity.extract_type(start_time, end_time)

        while response is not None and response.status.isSuccess \
          and response.searchRowList is not None:

            #records = response.recordList.record
            records = response.searchRowList.searchRow

            for record in records:
                internal_id = record['basic']['internalId'][0]['searchValue']['internalId']
                trans_type = record['basic']['type'][0]['searchValue']

                transaction_types[internal_id] = trans_type

            response = entity.extract_type(start_time, end_time, response)

        # Update the Transactions in the DB
        schema = psycopg2.sql.Identifier(args.schema)
        table = psycopg2.sql.Identifier(Transaction.schema.table_name(args))

        with db_open() as db:
            cursor = db.cursor()
            update_query = psycopg2.sql.SQL("""
                    UPDATE {0}.{1}
                    SET transaction_type = data.transaction_type
                    FROM (VALUES %s) AS data (internal_id, transaction_type)
                    WHERE {0}.{1}.internal_id = data.internal_id
            """).format(
                schema,
                table,
            )

            psycopg2.extras.execute_values(cursor,
                update_query.as_string(db),
                [(int(id),type) for id, type in transaction_types.items() ],
                template=None,
                page_size=100
            )

        logging.info("Extraction of Transaction Types completed Successfully")
    else:
        logging.info("Could NOT login to NetSuite - Script Failed")
