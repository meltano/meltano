from meltano.schema.serializers import MeltanoSerializer

class MeltanoService:
    loaders = dict()
    extractors = dict()

    @classmethod
    def register_loader(cls, loader_uri, loader_class):
        # TODO test if loader_class > MeltanoLoader
        cls.loaders[loader_uri] = loader_class

    @classmethod
    def register_extractor(cls, extractor_uri, extractor_class):
        # TODO test if extractor_class > MeltanoExtractor
        cls.extractors[extractor_uri] = extractor_class

    def create_loader(self, loader_uri, stream):
        return MeltanoService.loaders[loader_uri](stream, self)

    def create_extractor(self, extractor_uri, stream):
        return MeltanoService.extractors[extractor_uri](stream, self)

    def load_schema(self, schema_name, schema_file):
        serializer = MeltanoSerializer(schema_name)
        with open(schema_file, 'r') as f:
            serializer.load(f)

        return serializer.schema
