import os
import requests
import json
import functools
import csv
import asyncio
import logging

from tempfile import NamedTemporaryFile
from datetime import datetime
from requests.auth import HTTPBasicAuth
from elt.cli import DateWindow
from elt.utils import compose
from elt.db import db_open
from elt.error import ExceptionAggregator, SchemaError
from elt.schema import DBType, Schema
from elt.process import upsert_to_db_from_csv
import schema.ticket as ticket


USER = "{}/token".format(os.getenv("ZENDESK_EMAIL"))
TOKEN = os.getenv("ZENDESK_API_TOKEN")
ENDPOINT = os.getenv("ZENDESK_ENDPOINT")
PAGE_SIZE = 1000


def get_auth():
    return HTTPBasicAuth(USER, TOKEN)


def extract(args):
    window = DateWindow(args, formatter=datetime.timestamp)
    exporter = export_file(args, *window.formatted_range())
    importer = import_file(args, exporter)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(importer)
    loop.close()


@asyncio.coroutine
async def import_file(args, exporter):
    try:
        for csv_file in exporter:
            with db_open() as db:
                upsert_to_db_from_csv(db, csv_file,
                                      primary_key=ticket.PRIMARY_KEY,
                                      table_name=ticket.table_name(args),
                                      table_schema=args.schema,
                                      csv_options={
                                          'NULL': "'null'",
                                          'FORCE_NULL': "({columns})",
                                      })
    except GeneratorExit:
        logging.info("Import finished.")


def export_file(args, start_time, end_time):
    envelope = None

    def get_tickets(envelope):
        tickets_url = "{}/incremental/tickets.json".format(ENDPOINT)
        payload = {
            "start_time": start_time,
        }

        if envelope is not None:
            payload['start_time'] = envelope['end_time']

        return requests.get(tickets_url,
                            params=payload,
                            auth=get_auth())

    def finished(envelope):
        if envelope is None: return False

        return envelope['count'] < PAGE_SIZE and \
          envelope['end_time'] <= end_time

    while not finished(envelope):
        envelope = get_tickets(envelope).json()

        with NamedTemporaryFile(mode="w", delete=not args.nodelete) as f:
            f.write(json.dumps(envelope))
            logging.info("Wrote response at {}".format(f.name))

        try:
            schema = ticket.describe_schema(args)
            yield flatten_csv(args, schema, envelope['tickets'])
        except SchemaError as e:
            logging.warn(e)


def flatten_csv(args, schema, entries):
    """
    Flatten a list of objects according to the specfified schema.

    Returns the output filename
    """
    table_name = ticket.table_name(args)
    output_file = args.output_file or "tickets-{}.csv".format(datetime.utcnow().timestamp())
    flatten_entry = functools.partial(flatten, schema, table_name)

    header = entries[0]
    with open(output_file, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header.keys())
        writer.writeheader()
        writer.writerows(map(flatten_entry, entries))

    return output_file


def flatten(schema: Schema, table_name, entry):
    flat = {}
    results = ExceptionAggregator(SchemaError)

    for k, v in entry.items():
        column_key = (table_name, k)
        column = results.call(schema.__getitem__, column_key)

        if not column: continue
        db_type = column.data_type
        flat[k] = flatten_value(db_type, v)
        # print("{} -[{}]-> {}".format(v, db_type, flat[k]))

    results.raise_aggregate()

    return flat


def flatten_value(db_type: DBType, value):
    null = lambda x: x if x is not None else 'null'
    # X -> 'wx(q|w)'
    around = lambda w, x, q=None: ''.join((str(w), str(x), str(q or w)))
    quote = functools.partial(around, "'")
    array = compose(functools.partial(around, "{", q="}"),
                    ",".join,
                    functools.partial(map, str))

    strategies = {
        DBType.JSON: json.dumps,
        # [x0, ..., xN] -> '{x0, ..., xN}'
        DBType.ArrayOfInteger: array,
        DBType.ArrayOfLong: array,
        # [x0, ..., xN] -> '{'x0', ..., 'xN'}'
        DBType.ArrayOfString: compose(array,
                                      functools.partial(map, quote)),
    }

    strategy = strategies.get(db_type, null)

    return compose(null, strategy)(value)
