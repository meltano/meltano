import yaml
from sqlalchemy import (
    MetaData,
    Table,
    String,
    Column,
    TIMESTAMP,
    Float,
    Integer,
    Boolean,
    Date,
    REAL,
    SMALLINT,
    TEXT,
    BIGINT,
    JSON,
)


def get_sqlalchemy_col(field_name: str, field_type_name: str) -> Column:
    if field_type_name == 'timestamp without time zone':
        return Column(field_name, TIMESTAMP(timezone=False))
    elif field_type_name == 'timestamp with time zone':
        return Column(field_name, TIMESTAMP(timezone=True))
    elif field_type_name == 'character varying':
        return Column(field_name, String)
    elif field_type_name == 'date':
        return Column(field_name, Date)
    elif field_type_name == 'real':
        return Column(field_name, REAL)
    elif field_type_name == 'integer':
        return Column(field_name, Integer)
    elif field_type_name == 'smallint':
        return Column(field_name, SMALLINT)
    elif field_type_name == 'text':
        return Column(field_name, TEXT)
    elif field_type_name == 'bigint':
        return Column(field_name, BIGINT)
    elif field_type_name == 'float':
        return Column(field_name, Float)
    elif field_type_name == 'boolean':
        return Column(field_name, Boolean)
    elif field_type_name == 'json':
        return Column(field_name, JSON)
    # elif field_type_name == '':
    #     return Column(field_name, )
    print((f'{field_type_name} is unknown column type'))
    raise NotImplemented


def tables_from_manifest(
        manifest_file_path: str,
        metadata: MetaData,
        schema_name: str,
) -> {str: Table}:
    with open(manifest_file_path) as file:
        schema_manifest: dict = yaml.load(file)
        tables = {}
        for table_name in schema_manifest:
            columns: {str: str} = schema_manifest[table_name]['columns']
            columns_list = [
                get_sqlalchemy_col(field_name, field_type_name)
                for field_name, field_type_name in columns.items()
            ]
            table = Table(
                table_name,
                metadata,
                *columns_list,
                schema=schema_name,
            )
            tables[table_name] = table
    return tables
