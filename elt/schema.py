import logging
import psycopg2
import psycopg2.sql
import psycopg2.extras

from typing import Sequence, Callable, Set
from enum import Enum
from collections import OrderedDict, namedtuple
from elt.error import ExceptionAggregator, InapplicableChangeError


class DBType(str, Enum):
    Date = 'date'
    String = 'character varying'
    Double = 'real'
    Integer = 'integer'
    Long = 'bigint'
    Boolean = 'boolean'
    Timestamp = 'timestamp without time zone'
    JSON = 'json'
    ArrayOfInteger = Integer + '[]'
    ArrayOfLong = Long + '[]'
    ArrayOfString = String + '[]'
    UUID = 'UUID'
    ArrayOfUUID = UUID + '[]'


class SchemaDiff(Enum):
    COLUMN_OK = 1
    COLUMN_CHANGED = 2
    COLUMN_MISSING = 3
    TABLE_MISSING = 4


Column = namedtuple('Column', [
    'table_schema',
    'table_name',
    'column_name',
    'data_type',
    'is_nullable',
    'is_mapping_key',
])


class Schema:
    def table_key(column: Column):
        return column.table_name

    def column_key(column: Column):
        return (column.table_name, column.column_name)

    def __init__(self, name, columns: Sequence[Column] = [], primary_key_name='__row_id'):
        self.name = name
        self.tables = set()
        self.primary_key_name = primary_key_name
        self.columns = OrderedDict()

        for column in columns:
            self.tables.add(Schema.table_key(column))
            self.columns[Schema.column_key(column)] = column

    def add_table(self, column: Column):
        self.tables.add(Schema.table_key(column))

    def column_diff(self, column: Column) -> Set[SchemaDiff]:
        table_key = Schema.table_key(column)
        column_key = Schema.column_key(column)

        if table_key not in self.tables:
            return {SchemaDiff.TABLE_MISSING, SchemaDiff.COLUMN_MISSING}

        if column_key not in self.columns:
            return {SchemaDiff.COLUMN_MISSING}

        db_col = self.columns[column_key]
        if column.data_type != db_col.data_type \
          or column.is_nullable != db_col.is_nullable:
            return {SchemaDiff.COLUMN_CHANGED}

        return {SchemaDiff.COLUMN_OK}


def db_schema(db_conn, schema_name, primary_key_name='__row_id') -> Schema:
    """
    :db_conn: psycopg2 db_connection
    :schema: database schema
    """
    cursor = db_conn.cursor()

    cursor.execute("""
    SELECT table_schema, table_name, column_name, udt_name::regtype as data_type, is_nullable = 'YES', NULL as is_mapping_key
    FROM information_schema.columns
    WHERE table_schema = %s
    ORDER BY ordinal_position;
    """, (schema_name,))

    columns = map(Column._make, cursor.fetchall())
    return Schema(schema_name, columns, primary_key_name=primary_key_name)


def ensure_schema_exists(db_conn, schema_name):
    """
    Make sure that the given schema_name exists in the database
    If not, create it

    :db_conn: psycopg2 db_connection
    :schema: database schema
    """
    cursor = db_conn.cursor()

    create_schema = psycopg2.sql.SQL("CREATE SCHEMA IF NOT EXISTS {0}").format(
        psycopg2.sql.Identifier(schema_name)
    )
    cursor.execute(create_schema)
    db_conn.commit()


def schema_apply(db_conn, target_schema: Schema):
    """
    Tries to apply the schema from the Marketo API into
    upon the data warehouse.

    :db_conn:        psycopg2 database connection.
    :target_schema:  Schema to apply.

    Returns True when successful.
    """
    ensure_schema_exists(db_conn, target_schema.name)

    schema = db_schema(db_conn, target_schema.name,
                       primary_key_name=target_schema.primary_key_name)

    results = ExceptionAggregator(InapplicableChangeError)
    schema_cursor = db_conn.cursor()

    for name, col in target_schema.columns.items():
        results.call(schema_apply_column, schema_cursor, schema, col)

    results.raise_aggregate()

    # commit if there are no failure
    db_conn.commit()


def schema_apply_column(db_cursor, schema: Schema, column: Column) -> Set[SchemaDiff]:
    """
    Apply the schema to the current database connection
    adapting tables as it goes. Currently only supports
    adding new columns.

    :cursor: A database connection
    :column: the column to apply
    """
    diff = schema.column_diff(column)
    identifier = (
        psycopg2.sql.Identifier(column.table_schema),
        psycopg2.sql.Identifier(column.table_name),
    )

    if SchemaDiff.COLUMN_CHANGED in diff:
        raise InapplicableChangeError(diff)

    if SchemaDiff.TABLE_MISSING in diff:
        stmt = "CREATE TABLE {}.{} ({} SERIAL PRIMARY KEY)"
        sql = psycopg2.sql.SQL(stmt).format(
            *identifier,
            psycopg2.sql.Identifier(schema.primary_key_name)
        )
        logging.debug("Creating table {}.{}".format(*identifier))
        db_cursor.execute(sql)
        schema.add_table(column)

    if SchemaDiff.COLUMN_OK not in diff:
        logging.debug("[{}]: {}".format(column.column_name, diff))

    if SchemaDiff.COLUMN_MISSING in diff:
        stmt = "ALTER TABLE {}.{} ADD COLUMN {} %s"
        if not column.is_nullable:
            stmt += " NOT NULL"

        sql = psycopg2.sql.SQL(stmt % column.data_type).format(
            *identifier,
            psycopg2.sql.Identifier(column.column_name),
        )
        db_cursor.execute(sql)

        if column.is_mapping_key:
            constraint = "{table}_{column}_mapping_key".format(table=column.table_name,
                                                               column=column.column_name)

            stmt = "ALTER TABLE {}.{} ADD CONSTRAINT {} UNIQUE ({})"
            sql = psycopg2.sql.SQL(stmt).format(
                *identifier,
                psycopg2.sql.Identifier(constraint),
                psycopg2.sql.Identifier(column.column_name),
            )
            db_cursor.execute(sql)

    return diff
