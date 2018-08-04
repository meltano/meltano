import json
import functools
import csv
import asyncio
import logging

from tempfile import NamedTemporaryFile
from datetime import datetime
from elt.cli import DateWindow
from elt.db import db_open
from elt.utils import compose
from elt.error import ExceptionAggregator, Error
from elt.schema import DBType, Schema
from elt.process import upsert_to_db_from_csv

from soap_api.netsuite_soap_client import NetsuiteClient


def extract(args, entities_to_export):
    window = DateWindow(args, formatter=datetime.date)
    start_time, end_time = window.formatted_range()

    logging.info("NetSuit Extract Started")
    logging.info("Date interval = [{},{}]".format(start_time, end_time))

    loop = asyncio.get_event_loop()

    # Export data for the provided entities
    for entity in entities_to_export:
        logging.info("+ Extracting {}".format(entity.name_plural))
        exporter = export_file(args, entity, start_time, end_time)
        importer = import_file(args, exporter)

        loop.run_until_complete(importer)

    loop.close()


@asyncio.coroutine
async def import_file(args, exporter):
    try:
        for export_result in exporter:
            with db_open() as db:
                logging.info(" - Importing {}".format(export_result['entity'].name_plural))
                upsert_to_db_from_csv(db, export_result['file'],
                                      primary_key=export_result['entity'].schema.PRIMARY_KEY,
                                      table_name=export_result['entity'].schema.table_name(args),
                                      table_schema=args.schema,
                                      csv_options={
                                          'NULL': "'null'",
                                          'FORCE_NULL': "({columns})",
                                      })
    except GeneratorExit:
        logging.info("Import finished.")


def export_file(args, entity, start_time, end_time):
    response = entity.extract_incremental(start_time, end_time)

    while response is not None and response.status.isSuccess \
      and response.recordList is not None:
        transform_results = entity.transform(response.recordList.record)

        # The result of a transform may be multiple entities being updated with data
        # For each one returned, flatten the fetched data and yield the result
        for result in transform_results:
            with NamedTemporaryFile(mode="w", delete=not args.nodelete) as f:
                f.write(json.dumps(result['data']))
                logging.info("Wrote response at {}".format(f.name))

            try:
                yield flatten_csv(args, result['data'], result['entity'])
            except Error as e:
                logging.error(e)
                raise e

        response = entity.extract_incremental(start_time, end_time, response)


def flatten_csv(args, entries, entity):
    """
    Flatten a list of objects according to an entity's schema.

    Returns the entity for which the data are intended and the output filename
    """
    table_name = entity.schema.table_name(args)
    output_file = args.output_file or "{}-{}.csv".format(
                            entity.name_plural, datetime.utcnow().timestamp()
                        )
    flatten_entry = functools.partial(flatten,
                                      entity.schema.describe_schema(args),
                                      table_name)

    header = entries[0]
    with open(output_file, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header.keys())
        writer.writeheader()
        writer.writerows(map(flatten_entry, entries))

    return {'entity':entity, 'file': output_file}


def flatten(schema: Schema, table_name, entry):
    flat = {}
    results = ExceptionAggregator(KeyError)

    for k, v in entry.items():
        column_key = (table_name, k)
        db_type = results.call(schema.columns.__getitem__, column_key).data_type
        flat[k] = flatten_value(db_type, v)

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
