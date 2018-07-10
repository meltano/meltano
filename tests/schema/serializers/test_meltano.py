from functools import partial
from itertools import chain
from elt.schema import Schema, DBType, Column
from elt.schema.serializers.meltano import MeltanoSerializer


def sample_schema(table_names=()):
    table_schema = 'pytest'

    # curry the Column object
    def column(table_name, column_name, data_type, *,
               is_nullable=True,
               is_mapping_key=False):
        return Column(table_schema=table_schema,
                      table_name=table_name,
                      column_name=column_name,
                      data_type=data_type.value,
                      is_nullable=is_nullable,
                      is_mapping_key=is_mapping_key)

    def table(table_name):
        table_column = partial(column, table_name)
        return [
            table_column("id",         DBType.Integer,        is_mapping_key=True),
            table_column("string",     DBType.String),
            table_column("long",       DBType.Long,           is_nullable=False),
            table_column("bool",       DBType.Boolean),
            table_column("date",       DBType.Date),
            table_column("ao_strings", DBType.ArrayOfString),
            table_column("json",       DBType.JSON),
            table_column("ao_long",    DBType.ArrayOfLong),
        ]

    return Schema(table_schema, chain(*(table(name) for name in table_names)))


def test_dumps():
    schema = sample_schema(table_names=('entity01', 'entity02'))
    yaml = MeltanoSerializer(schema).dumps()

    assert(yaml)

def test_loads():
    yaml_schema = """
entity01:
  id: integer
  long: bigint
  text: text
  entity01_long_mapping_key: long
"""
    schema = MeltanoSerializer('yaml').loads(yaml_schema).schema
    assert(len(schema.columns.values()) == 3)


def test_idempotent():
    schema = sample_schema(table_names=('entity01', 'entity02'))
    serializer = MeltanoSerializer(schema)
    schema2 = MeltanoSerializer(schema.name).loads(serializer.dumps()).schema

    assert(len(schema.tables) == len(schema2.tables))
