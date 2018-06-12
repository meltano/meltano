import json
import logging

from collections import OrderedDict
from functools import partial
from elt.schema import Schema, Column, DBType


# (<type>, <format>): DBType
data_type_map = {
    ("string", None): DBType.String,
    ("string", "date-time"): DBType.Timestamp,
    ("boolean", None): DBType.Boolean,
    ("integer", None): DBType.Integer,
    ("number", None): DBType.Double,
    ("object", None): DBType.JSON,
}


def is_nullable(type_def) -> bool:
    # empty def means any valid JSON
    if not type_def:
        return True

    if 'anyOf' in type_def:
        type_def = type_def['anyOf'][1] # the nullable one

    return "null" in type_def['type']


def data_type(type_def) -> DBType:
    # empty def means any valid JSON
    if not type_def:
        return DBType.JSON

    if 'anyOf' in type_def:
        type_def = type_def['anyOf'][0] # the format one

    if isinstance(type_def['type'], list):
        non_null = lambda x: x != "null"
        _type = next(filter(non_null, type_def['type']))
    else:
        _type = type_def['type']

    _format = type_def.get('format', None)

    return data_type_map[(_type, _format)]


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
                      data_type=data_type.value,
                      is_nullable=is_nullable,
                      is_mapping_key=is_mapping_key)

    # streams → tables
    for stream in raw_schema['streams']:
        table_name = stream['stream']
        metadata = stream['metadata']

        # we can zip both these together to iterate on
        # (column_def, column_meta) which is a useful
        # shortcut (no need to check the breadcrumb)
        column_defs = stream['schema']['properties']
        *column_meta, table_meta = stream['metadata']

        mapping_keys = set(table_meta['metadata']['table-key-properties'])

        table_column = partial(schema_column, table_name)
        is_mapping_key = lambda col_def: col_def[0] in mapping_keys

        for col_def, col_meta in zip(column_defs.items(), column_meta):
            column_name = col_def[0]

            try:
                is_mapping_key = col_def[0] in mapping_keys
                schema.add_column(table_column(column_name,
                                               data_type(col_def[1]),
                                               is_nullable(col_def[1]),
                                               is_mapping_key))
            except:
                logging.error("Cannot parse column definition for {}: {}".format(table_name, col_def[0]))

    return schema


def load(schema_name: str, reader) -> Schema:
    return loads(schema_name, reader.read())
