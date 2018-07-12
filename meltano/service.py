from meltano.schema.serializers import MeltanoSerializer

class MeltanoService:
    loaders = dict()

    @classmethod
    def register_loader(cls, loader_uri, loader_class):
        # TODO test if class is correct
        cls.loaders[loader_uri] = loader_class

    def create_loader(self, loader_uri, stream):
        return MeltanoService.loaders[loader_uri](stream, self)

    def load_schema(self, schema_name, schema_file):
        serializer = MeltanoSerializer(schema_name)
        with open(schema_file, 'r') as f:
            serializer.load(f)

        return serializer.schema
