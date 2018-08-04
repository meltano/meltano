import os

from elt.schema import Schema, DBType, Column
from elt.schema.serializers.meltano import MeltanoSerializer
from elt.utils import compose
from itertools import chain
from functools import partial
from config import getObjectList, getZuoraFields


PG_SCHEMA = 'zuora'
PRIMARY_KEY = 'id'


def describe_schema() -> Schema:
    serializer = MeltanoSerializer(PG_SCHEMA)
    heredir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(heredir, '../config', 'zuora_manifest.yaml')

    return serializer.load(open(schema_path, 'r')).schema


def field_column_name(field) -> str:
    return field.lower().replace(".", "")
