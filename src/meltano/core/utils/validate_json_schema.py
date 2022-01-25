"""Validates yaml files against their schemas."""

import json
import os
import pathlib

import yaml
from jsonschema import validate

proj_path = pathlib.Path(__file__).resolve().parents[4]

with open(os.path.join(proj_path, "schema/discovery.schema.json"), "r") as schema_file:
    schema_content = json.load(schema_file)

with open(
    os.path.join(proj_path, "src/meltano/core/bundle/discovery.yml"), "r"
) as yaml_file:
    yaml_content = yaml.safe_load(yaml_file)
    validate(instance=yaml_content, schema=schema_content)
