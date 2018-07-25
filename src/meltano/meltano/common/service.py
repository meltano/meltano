import re

from meltano.schema.serializers import MeltanoSerializer


class MeltanoService:
    loaders = dict()
    extractors = dict()


    @classmethod
    def register_loader(cls, loader_id, loader_class):
        """
        loader_id: "urn:com.meltano:load:{backend}"
        """
        # TODO test if loader_class > MeltanoLoader
        cls.loaders[loader_id] = loader_class


    @classmethod
    def register_extractor(cls, extractor_id, extractor_class):
        """
        extractor_id: "urn:com.meltano:extract:{source}"
        """
        # TODO test if extractor_class > MeltanoExtractor
        cls.extractors[extractor_id] = extractor_class


    def __init__(self):
        self._entities = {}


    def create_loader(self, loader_id, stream):
        return MeltanoService.loaders[loader_id](stream, self)


    def create_extractor(self, extractor_id, stream):
        return MeltanoService.extractors[extractor_id](stream, self)


    def register_entity(self, entity_id, entity: 'Entity'):
        """
        entity_id: "urn:com.meltano:entity:{source}:{entity}"
        """
        if entity_id in self._entities:
            raise ValueError("{} is already registered".format(entity_id))

        self._entities[entity_id] = entity
        return entity_id


    def register_manifest(cls, manifest: 'Manifest'):
        """
        manifest: The manifest to register.
        """
        build_id = lambda e: \
          "urn:com.meltano:entity:{source}:{entity}".format(source=manifest.source_name,
                                                            entity=e.alias)

        return [cls.register_entity(build_id(entity), entity) \
                for entity in manifest.entities]


    def get_entity(self, entity_id):
        return self._entities[entity_id]


    def auto_discover(self):
        packages = pkg_resources.AvailableDistributions()  # scan sys.path
        addons = filter(lambda pkg: re.search(r'meltano-(load|extract)-\w+'))

        return list(map(importlib.import_module, addons))


    def load_schema(self, schema_name, schema_file):
        serializer = MeltanoSerializer(schema_name)
        with open(schema_file, 'r') as f:
            serializer.load(f)

        return serializer.schema
