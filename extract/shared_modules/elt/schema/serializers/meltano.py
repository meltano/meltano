import yaml
import pathlib
import re

from typing import Generator
from functools import partial
from elt.schema import Schema, Column
from .base import Serializer


class MeltanoSerializer(Serializer):
    @staticmethod
    def tables(schema) -> Generator[dict, None, None]:
        col_in_table = lambda table, col: col.table_name == table

        for table in schema.tables:
            in_table = partial(col_in_table, table)
            table_columns = list(filter(in_table, schema.columns.values()))

            column_defs = {
                col.column_name: col.data_type \
                for col in table_columns
            }

            mapping_keys = {
                Schema.mapping_key_name(col): col.column_name \
                for col in table_columns \
                if col.is_mapping_key
            }

            yield {table: {
                **column_defs,
                **mapping_keys,
            }}

    def dumps(self) -> str:
        schema_def = dict()
        for table_def in self.tables(self.schema):
            schema_def.update(table_def)

        return yaml.dump(schema_def, default_flow_style=False)

    def loads(self, yaml_str: str) -> Serializer:
        raw = yaml.load(yaml_str)

        columns = []
        for table, table_data in raw.items():
            for column, data_type in table_data.items():
                if column.endswith("_mapping_key"):
                    continue

                # HACK: we should reformat this manifest file
                mapping_key = "{}_{}_mapping_key".format(table, column)
                is_mapping_key = mapping_key in table_data

                column = Column(table_schema=self.schema.name,
                                table_name=table,
                                column_name=column,
                                data_type=data_type,
                                is_nullable=not is_mapping_key,
                                is_mapping_key=is_mapping_key)

                self.schema.add_column(column)

        return self
