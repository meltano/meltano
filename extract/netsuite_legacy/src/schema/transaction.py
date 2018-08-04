from elt.schema import Schema, Column, DBType

from schema.transaction_config import TRANSACTION_TYPES, COLUMN_MAPPINGS, RELATED_ENTITIES
from schema.utils import columns_from_mappings

PG_SCHEMA = 'netsuite'
PG_TABLE = 'transactions'
PRIMARY_KEY = 'internal_id' # TODO: confirm


def describe_schema(args) -> Schema:
    table_name = args.table_name or PG_TABLE
    table_schema = args.schema or PG_SCHEMA

    # curry the Column object
    def column(column_name, data_type, *,
               is_nullable=True,
               is_mapping_key=False):
        return Column(table_schema=table_schema,
                      table_name=table_name,
                      column_name=column_name,
                      data_type=data_type.value,
                      is_nullable=is_nullable,
                      is_mapping_key=is_mapping_key)

    return Schema(table_schema,
        [
          column("internal_id",      DBType.Long, is_mapping_key=True),
          column("transaction_type", DBType.String),
        ]  \
        + columns_from_mappings(column, COLUMN_MAPPINGS)  \
        + [ column("imported_at",    DBType.Timestamp) ]
    )


def table_name(args):
    return args.table_name or PG_TABLE

