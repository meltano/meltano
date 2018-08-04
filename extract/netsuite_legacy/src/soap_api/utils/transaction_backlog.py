import os
import logging
import psycopg2
import psycopg2.sql
import datetime

from elt.db import db_open

from soap_api.transaction import Transaction


def transaction_backlog(args):
    """
    Find a valid date range for extracting more Transaction records from Netsuite.

    Check if there is a need to extract more records from NetSuite and return
     the date range to use for fetching more Transaction records.

    If this is a new schema or no data have already been fetched (i.e. the
     regular extraction has not already run at least once) then do nothing.

    Otherwise, find the earliest modified date fetched and use it as a pivot
     date for creating a search date interval [start, end] with:
     end =  {earliest modified date in DB} + 1 day (interval's end is not inclusive)
     start = {earliest modified date in DB} - days provided in ards.days

    We re-fetch the earliest modified date in order to be sure that no records
     are missing between calls to transaction_backlog()
    """
    logging.info("Fetching Transaction BackLog")

    # Earliest last_modified_date for transactions in NetSuite
    # Used in order to stop the back filling job from going further back in time
    earliest_date_to_check = os.getenv('NETSUITE_EARLIEST_DATE')

    if args.days is None or int(args.days) <= 0:
        logging.info("This operation needs the --days option in order to run")
        logging.info("Missing arguments - aborting backlog")
        return None

    days = datetime.timedelta(days=args.days)

    # Fetch the earliest last_modified_date stored in the Transaction Table
    try:
        schema = psycopg2.sql.Identifier(args.schema)
        table = psycopg2.sql.Identifier(Transaction.schema.table_name(args))

        with db_open() as db:
            cur = db.cursor()
            query = psycopg2.sql.SQL("""
                    SELECT MIN(last_modified_date)
                    FROM {0}.{1}
            """).format(schema, table)

            cur.execute(query)
            result = cur.fetchone()

        if result is None or result[0] is None:
            # No data yet fetched -
            # Let the regular extraction run at least once
            logging.info("No data fetched yet - aborting backlog")
            return None

        last_modified_date = result[0].date()

        if last_modified_date.isoformat() <= earliest_date_to_check:
            # We have fetched everything - No need to keep on making requests
            return None
        else:
            end_time = last_modified_date + datetime.timedelta(days=1)
            start_time = last_modified_date - days
            return (start_time, end_time)
    except psycopg2.Error as err:
        logging.info("No schema created yet - aborting backlog")
        return None

