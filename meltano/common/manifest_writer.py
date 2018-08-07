import yaml
import yamlordereddictloader

from collections import OrderedDict
from .manifest import Manifest


class ManifestWriter:
    def __init__(self, file):
        self.file = file


    def write(self, manifest: Manifest):
        entities = [
            (entity.alias, self.raw_entity(entity)) \
            for entity in manifest.entities
        ]

        raw_manifest = OrderedDict([
            ('version', manifest.version),
            *entities
        ])

        yaml.dump(raw_manifest, self.file,
                  Dumper=yamlordereddictloader.SafeDumper,
                  default_flow_style=False)


    def raw_entity(self, entity):
        raw_entity = {
            'alias': entity.alias,
            'attributes': [
                self.raw_attribute(attr) \
                for attr in entity.attributes
            ]
        }

        return raw_entity


    def raw_attribute(self, attribute):
        raw_attribute = {
            'alias': attribute.alias,
            'input': self.raw_transient_attribute(attribute.input),
        }

        if attribute.input != attribute.output:
            raw_attribute['output'] = self.raw_transient_attribute(attribute.output)

        if attribute.metadata:
            raw_attribute['metadata'] = attribute.metadata

        return raw_attribute


    def raw_transient_attribute(self, transient_attribute):
        return {
            'name': transient_attribute.name,
            'type': transient_attribute.data_type,
        }
