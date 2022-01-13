import json
import os
import pathlib

from jsonschema import validate
from ruamel.yaml import YAML

yaml = YAML()
proj_path = pathlib.Path(__file__).resolve().parents[4]

with open(os.path.join(proj_path, "schema/discovery.schema.json"), "r") as schema_file:
    schema_content = json.load(schema_file)

with open(
    os.path.join(proj_path, "src/meltano/core/bundle/discovery.yml"), "r"
) as yaml_file:
    yaml_content = yaml.load(yaml_file)
    validate(instance=yaml_content, schema=schema_content)
