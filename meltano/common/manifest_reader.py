import yaml

from meltano.common.entity import Entity, Attribute, TransientAttribute
from .manifest import Manifest


class ManifestReader:
    def __init__(self, source_name):
        self.source_name = source_name

    def load(self, file):
        return self.loads(file.read())

    def loads(self, raw):
        raw_manifest = yaml.load(raw)

        version = raw_manifest.pop('version')
        entities = [self.parse_entity(entity_name, entity_def) \
                    for entity_name, entity_def in raw_manifest.items()]

        return Manifest(self.source_name,
                        version=version,
                        entities=entities)

    def parse_entity(self, entity_name, entity_def) -> Entity:
        attributes = [self.parse_attribute(attr) \
                      for attr in entity_def['attributes']]

        return Entity(entity_name,
                      alias=entity_def.get('alias'),
                      attributes=attributes)

    def parse_attribute(self, attribute_def) -> Attribute:
        input, output = map(self.parse_transient_attribute, (
            attribute_def.get('input'),
            attribute_def.get('output')
        ))

        return Attribute(attribute_def['alias'], input, output,
                         metadata=attribute_def.get('metadata', {}))

    def parse_transient_attribute(self, transient_attribute_def) -> TransientAttribute:
        if transient_attribute_def is None:
            return None

        return TransientAttribute(transient_attribute_def['name'],
                                  transient_attribute_def['type'])
