from meltano.schema import Schema, Column, DBType


class Manifest:
    __version__ = '1.0'

    def __init__(self, source_name, version=None, entities=[]):
        self.source_name = source_name
        self.version = version or Manifest.__version__
        self.entities = entities

    def as_schema(self):
        columns = []
        for entity in self.entities:
            for attr in entity.attributes:
                columns.append(
                    Column(table_schema=self.source_name,
                           table_name=entity.alias,
                           column_name=attr.name,
                           data_type=attr.data_type,
                           is_mapping_key=attr.metadata.get('is_pkey', False),
                           is_nullable=attr.metadata.get('is_nullable', True))
                )

        return Schema(self.source_name, columns)
