from meltano.schema import Schema, Column, DBType


class Manifest:
    def __init__(self, version, source_name, entities=[]):
        self.version = version
        self.source_name = source_name
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
