from elt.schema import Schema
from elt.schema.serializers import MeltanoSerializer
from config import manifest_file_path


def describe_schema(args) -> Schema:
    serializer = MeltanoSerializer(args.schema or "sfdc")

    with open(manifest_file_path(args), 'r') as reader:
        serializer.load(reader)

    return serializer.schema
