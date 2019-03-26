import json
from os.path import join, dirname
from jsonschema import validate


def assert_cli_runner(runner, message=None):
    assertion_message = str(message or runner.output)

    assert runner.exit_code == 0, assertion_message


def assert_valid_schema(data, schema_file):
    """ Checks whether the given data matches the schema """

    schema = _load_json_schema(schema_file)
    return validate(data, schema)


def _load_json_schema(filename):
    """ Loads the given schema file """

    relative_path = join('schemas', filename)
    absolute_path = join(dirname(__file__), relative_path)

    with open(absolute_path) as schema_file:
        return json.loads(schema_file.read())