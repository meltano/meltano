import os
import pathlib
import shutil

import pytest
from meltano.core.plugin_discovery_generator import PluginDiscoveryGenerator

TEST_DEFINITION = """
name: tap-csv
label: Comma Separated Values (CSV)
description: Generic data extractor of CSV (comma separated value) files
namespace: tap_csv
variants:
- name: meltanolabs
  docs: https://hub.meltano.com/extractors/csv.html
  repo: https://github.com/MeltanoLabs/tap-csv
  pip_url: git+https://github.com/MeltanoLabs/tap-csv.git
  capabilities:
  - discover
  - catalog
  - state
  settings_group_validation:
  - - files
  - - csv_files_definition
  settings:
  - name: files
    kind: array
    description: Array of objects with `entity`, `path`, and `keys` keys
  - name: csv_files_definition
    env: TAP_CSV_FILES_DEFINITION
    label: CSV Files Definition
    description: Project-relative path to JSON file holding array of objects with
      `entity`, `path`, and `keys` keys
    placeholder: Ex. files-def.json
    documentation: https://github.com/MeltanoLabs/tap-csv#settings
"""

EXPECTED_DISCOVERY = """# Increment this version number whenever the schema of discovery.yml is changed.
# See https://www.meltano.com/docs/contributor-guide.html#discovery-yml-version for more information.
version: 19
extractors:
- name: tap-csv
  label: Comma Separated Values (CSV)
  description: Generic data extractor of CSV (comma separated value) files
  namespace: tap_csv
  variants:
  - name: meltanolabs
    docs: https://hub.meltano.com/extractors/csv.html
    repo: https://github.com/MeltanoLabs/tap-csv
    pip_url: git+https://github.com/MeltanoLabs/tap-csv.git
    capabilities:
    - discover
    - catalog
    - state
    settings_group_validation:
    - - files
    - - csv_files_definition
    settings:
    - name: files
      kind: array
      description: Array of objects with `entity`, `path`, and `keys` keys
    - name: csv_files_definition
      env: TAP_CSV_FILES_DEFINITION
      label: CSV Files Definition
      description: Project-relative path to JSON file holding array of objects with
        `entity`, `path`, and `keys` keys
      placeholder: Ex. files-def.json
      documentation: https://github.com/MeltanoLabs/tap-csv#settings
"""

ABS_PATH = pathlib.Path(__file__).parent.resolve()
DEFINITIONS_PATH = f"{ABS_PATH}/test_plugin_definitions/"


@pytest.fixture
def plugin_definitions():
    os.makedirs(DEFINITIONS_PATH, exist_ok=True)
    os.makedirs(DEFINITIONS_PATH + "extractors", exist_ok=True)

    with open(DEFINITIONS_PATH + "extractors/csv.yml", "w") as f:
        f.write(TEST_DEFINITION)

    yield

    shutil.rmtree(DEFINITIONS_PATH)


def test_discovery_generator(plugin_definitions):
    obj = PluginDiscoveryGenerator()
    obj.generate_discovery(
        plugin_definitions_dir=DEFINITIONS_PATH,
        discovery_file_path=f"{DEFINITIONS_PATH}/discovery.yml",
    )
    with open(f"{DEFINITIONS_PATH}/discovery.yml", "r") as f:
        generated_discovery = f.read()
    assert generated_discovery == EXPECTED_DISCOVERY
