import logging

from xml.etree import ElementTree
from elt.schema import Schema, Column, DBType


def loads(schema_name: str, raw: str) -> Schema:
    tree = ElementTree.fromstring(raw)
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

    for table in
