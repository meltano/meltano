import json

from collections import OrderedDict
from functools import partial
from elt.schema import Schema


def loads(schema_name: str, raw: str) -> Schema:
    # we must use an OrderedDict to benefit from the
    # ordering of properties, see the `zip` below
    raw_schema = json.loads(raw, object_pairs_hook=OrderedDict)
    schema = Schema(schema_name)

    def schema_column(table_name,
                      column_name,
                      data_type,
                      is_nullable,
                      is_mapping_key):
        return Column(table_schema=schema_name,
                      table_name=table_name,
                      column_name=column_name,
                      data_type=str(data_type),
                      is_nullable=is_nullable,
                      is_mapping_key=is_mapping_key)

    # streams → tables
    for stream in raw_schema['streams'].items():
        table_name = stream['stream']
        metadata = stream['metadata']

        # we can zip both these together to iterate on
        # (column_def, column_meta) which can be useful
        column_defs = stream['schema']['properties']
        *column_meta, table_meta = stream['metadata']

        mapping_keys = set(table_meta['metadata']['table-key-properties'])

        table_column = partial(schema_column, table_name)
        is_mapping_key = lambda col_def: col_def[0] in mapping_keys

        for col_def, col_meta in zip(column_defs, column_meta):
            column_name = col_def[0]

            is_nullable = "null" in col_def[1]['type']
            is_mapping_key = col_def[0] in mapping_keys


        schema.add_column(table_column(
