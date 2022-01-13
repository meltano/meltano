import json
import os
import pathlib

from jsonschema import validate
from ruamel.yaml import YAML

yaml = YAML()
cur_path = pathlib.Path(__file__).parent.resolve()

with open(os.path.join(cur_path, "discovery.schema.json"), "r") as schema_file:
    schema_content = json.load(schema_file)

with open(os.path.join(cur_path.parent.resolve(), "src/meltano/core/bundle/discovery.yml"), "r") as yaml_file:
    yaml_content = yaml.load(yaml_file)
    validate(instance=yaml_content, schema=schema_content)
