from __future__ import annotations

import datetime
import json
import platform
import tempfile
from pathlib import Path
from textwrap import dedent

import pytest
import yaml
from jsonschema import validate

from fixtures.utils import cd
from meltano.core.project_files import deep_merge


@pytest.fixture
def cd_temp_subdir():
    original_dir = Path.cwd()
    with tempfile.TemporaryDirectory(dir=original_dir) as name:
        with cd(Path(name).resolve()) as new_dir:
            yield new_dir


@pytest.fixture
def cd_temp_dir():
    with tempfile.TemporaryDirectory() as name:
        with cd(Path(name).resolve()) as new_dir:
            yield new_dir


@pytest.mark.order(0)
@pytest.mark.parametrize(
    ("parent", "children", "expected"),
    (
        ({"a": 1}, [{"a": 1}], {"a": 1}),
        ({"a": 1}, [{"a": 2}], {"a": 2}),
        ({"a": 1}, [{"a": 2, "b": 2}], {"a": 2, "b": 2}),
        ({"a": [1, 2, 3]}, [{"a": [3, 4, 5]}], {"a": [1, 2, 3, 3, 4, 5]}),
        ({"a": "A", "b": "B"}, [{"a": "Z"}], {"a": "Z", "b": "B"}),
    ),
)
def test_deep_merge(parent, children, expected):
    assert deep_merge(parent, children) == expected


class TestProjectFiles:
    @pytest.mark.order(1)
    def test_resolve_subfiles(self, project_files):
        assert project_files._meltano_file_path == (project_files.root / "meltano.yml")
        assert project_files.meltano == {
            "version": 1,
            "default_environment": "test-meltano-environment",
            "database_uri": "sqlite:///.meltano/meltano.db",
            "include_paths": [
                "./subconfig_[0-9].yml",
                "./*/subconfig_[0-9].yml",
                "./*/**/subconfig_[0-9].yml",
            ],
            "plugins": {
                "extractors": [
                    {
                        "name": "tap-meltano-yml",
                        "settings": [
                            {
                                "name": "token",
                                "kind": "password",
                                "description": "Token for the API. This is a secret.",
                            }
                        ],
                    }
                ],
                "mappers": [
                    {
                        "name": "map-meltano-yml",
                        "mappings": [{"name": "transform-meltano-yml"}],
                    }
                ],
                "loaders": [{"name": "target-meltano-yml"}],
            },
            "schedules": [
                {
                    "name": "test-meltano-yml",
                    "extractor": "tap-meltano-yml",
                    "loader": "target-meltano-yml",
                    "transform": "skip",
                    "interval": "@once",
                    "start_date": datetime.datetime(2020, 8, 5, 0, 0),  # noqa: WPS432
                }
            ],
            "environments": [
                {"name": "test-meltano-environment", "env": {"TEST": "TEST-MELTANO"}}
            ],
            "jobs": [
                {
                    "name": "my-job",
                    "tasks": [
                        "tap-meltano-yml map-meltano-yml target-meltano-yml",
                    ],
                },
            ],
        }
        assert project_files.include_paths == [
            (project_files.root / "subconfig_2.yml"),
            (project_files.root / "subfolder" / "subconfig_1.yml"),
        ]

    @pytest.mark.order(2)
    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Test fails if even attempted to be run, xfail can't save us here.",
    )
    def test_resolve_from_subdir(self, project_files, cd_temp_subdir):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        assert Path.cwd() == cd_temp_subdir
        assert cd_temp_subdir.parent == project_files.root
        assert project_files.include_paths == [
            (project_files.root / "subconfig_2.yml"),
            (project_files.root / "subfolder" / "subconfig_1.yml"),
        ]

    @pytest.mark.order(3)
    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Test fails if even attempted to be run, xfail can't save us here.",
    )
    def test_resolve_from_any_dir(self, project_files, cd_temp_dir):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        assert Path.cwd() == cd_temp_dir
        assert project_files.include_paths == [
            (project_files.root / "subconfig_2.yml"),
            (project_files.root / "subfolder" / "subconfig_1.yml"),
        ]

    @pytest.mark.order(4)
    def test_jsonschema(self, project_files):
        schema_path = (
            Path(__file__).resolve().parents[3] / "schema" / "meltano.schema.json"
        )
        schema_content = json.loads(schema_path.read_text())

        class JsonCompatibleLoader(yaml.SafeLoader):
            """YAML loader to create dicts compatible with jsonschema validation."""

            @classmethod
            def remove_implicit_resolver(cls, tag):
                cls.yaml_implicit_resolvers = {
                    key: [(t, r) for (t, r) in values if t != tag]  # noqa: WPS111
                    for key, values in cls.yaml_implicit_resolvers.items()
                }

        JsonCompatibleLoader.remove_implicit_resolver("tag:yaml.org,2002:timestamp")

        for config_path in [
            project_files.root / "meltano.yml",
        ] + project_files.include_paths:
            with config_path.open("rt") as config_file:
                yaml_content = yaml.load(  # noqa: S506 (SafeLoader is subclassed)
                    config_file,
                    Loader=JsonCompatibleLoader,
                )
            validate(instance=yaml_content, schema=schema_content)

    @pytest.mark.order(5)
    def test_load(self, project_files):
        expected_result = {
            "version": 1,
            "default_environment": "test-meltano-environment",
            "database_uri": "sqlite:///.meltano/meltano.db",
            "include_paths": [
                "./subconfig_[0-9].yml",
                "./*/subconfig_[0-9].yml",
                "./*/**/subconfig_[0-9].yml",
            ],
            "plugins": {
                "extractors": [
                    {
                        "name": "tap-meltano-yml",
                        "settings": [
                            {
                                "name": "token",
                                "kind": "password",
                                "description": "Token for the API. This is a secret.",
                            }
                        ],
                    },
                    {"name": "tap-subconfig-2-yml"},
                    {"name": "tap-subconfig-1-yml"},
                ],
                "mappers": [
                    {
                        "name": "map-meltano-yml",
                        "mappings": [{"name": "transform-meltano-yml"}],
                    }
                ],
                "loaders": [
                    {"name": "target-meltano-yml"},
                    {"name": "target-subconfig-2-yml"},
                    {"name": "target-subconfig-1-yml"},
                ],
            },
            "schedules": [
                {
                    "name": "test-meltano-yml",
                    "extractor": "tap-meltano-yml",
                    "loader": "target-meltano-yml",
                    "transform": "skip",
                    "start_date": datetime.datetime(2020, 8, 5),  # noqa: WPS432
                    "interval": "@once",
                },
                {
                    "name": "test-subconfig-2-yml",
                    "extractor": "tap-subconfig-2-yml",
                    "loader": "target-subconfig-2-yml",
                    "transform": "skip",
                    "start_date": datetime.datetime(2020, 8, 4),  # noqa: WPS432
                    "interval": "@once",
                },
                {
                    "name": "test-subconfig-1-yml",
                    "extractor": "tap-subconfig-1-yml",
                    "loader": "target-subconfig-1-yml",
                    "transform": "skip",
                    "start_date": datetime.datetime(2020, 8, 6),  # noqa: WPS432
                    "interval": "@once",
                },
            ],
            "environments": [
                {"name": "test-meltano-environment", "env": {"TEST": "TEST-MELTANO"}},
                {
                    "name": "test-subconfig-2-yml",
                    "env": {"TEST": "TEST-SUBCONFIG-2-YML"},
                },
                {
                    "name": "test-subconfig-1-yml",
                    "env": {"TEST": "TEST-SUBCONFIG-1-YML"},
                },
            ],
            "jobs": [
                {
                    "name": "my-job",
                    "tasks": [
                        "tap-meltano-yml map-meltano-yml target-meltano-yml",
                    ],
                },
            ],
        }
        read_result = project_files.load()
        assert read_result == expected_result

    @pytest.mark.order(6)
    def test_update(self, project_files):
        meltano_config = project_files.load()
        meltano_config["version"] = 2
        meltano_config["plugins"]["extractors"][1][
            "name"
        ] = "modified-tap-subconfig-2-yml"
        meltano_config["plugins"]["loaders"][2][
            "name"
        ] = "modified-target-subconfig-1-yml"
        meltano_config["schedules"][0]["name"] = "modified-test-meltano-yml"

        project_files.update(meltano_config)
        expected_result = {
            "default_environment": "test-meltano-environment",
            "database_uri": "sqlite:///.meltano/meltano.db",
            "include_paths": [
                "./subconfig_[0-9].yml",
                "./*/subconfig_[0-9].yml",
                "./*/**/subconfig_[0-9].yml",
            ],
            "plugins": {
                "extractors": [
                    {
                        "name": "tap-meltano-yml",
                        "settings": [
                            {
                                "name": "token",
                                "kind": "password",
                                "description": "Token for the API. This is a secret.",
                            }
                        ],
                    },
                    {"name": "modified-tap-subconfig-2-yml"},
                    {"name": "tap-subconfig-1-yml"},
                ],
                "mappers": [
                    {
                        "name": "map-meltano-yml",
                        "mappings": [{"name": "transform-meltano-yml"}],
                    }
                ],
                "loaders": [
                    {"name": "target-meltano-yml"},
                    {"name": "modified-target-subconfig-1-yml"},
                    {"name": "target-subconfig-2-yml"},
                ],
            },
            "schedules": [
                {
                    "extractor": "tap-meltano-yml",
                    "interval": "@once",
                    "loader": "target-meltano-yml",
                    "name": "modified-test-meltano-yml",
                    "start_date": datetime.datetime(2020, 8, 5),  # noqa: WPS432
                    "transform": "skip",
                },
                {
                    "extractor": "tap-subconfig-2-yml",
                    "interval": "@once",
                    "loader": "target-subconfig-2-yml",
                    "name": "test-subconfig-2-yml",
                    "start_date": datetime.datetime(2020, 8, 4),  # noqa: WPS432
                    "transform": "skip",
                },
                {
                    "extractor": "tap-subconfig-1-yml",
                    "interval": "@once",
                    "loader": "target-subconfig-1-yml",
                    "name": "test-subconfig-1-yml",
                    "start_date": datetime.datetime(2020, 8, 6),  # noqa: WPS432
                    "transform": "skip",
                },
            ],
            "environments": [
                {"name": "test-meltano-environment", "env": {"TEST": "TEST-MELTANO"}},
                {
                    "name": "test-subconfig-2-yml",
                    "env": {"TEST": "TEST-SUBCONFIG-2-YML"},
                },
                {
                    "name": "test-subconfig-1-yml",
                    "env": {"TEST": "TEST-SUBCONFIG-1-YML"},
                },
            ],
            "jobs": [
                {
                    "name": "my-job",
                    "tasks": [
                        "tap-meltano-yml map-meltano-yml target-meltano-yml",
                    ],
                },
            ],
            "version": 2,
        }
        read_result = project_files.load()
        assert read_result == expected_result

    @pytest.mark.order(7)
    def test_preserve_format(self, project_files):
        meltano_config = project_files.load()
        meltano_config["version"] = 3
        meltano_config["schedules"][0]["transform"] = "only"
        meltano_config["schedules"][0].yaml_add_eol_comment(
            "Only update dbt models\n",
            "transform",
        )

        project_files.update(meltano_config)

        contents = project_files._meltano_file_path.read_text()

        expected_contents = """\
            # Top-level comment
            version: 3
            default_environment: test-meltano-environment
            database_uri: sqlite:///.meltano/meltano.db

            include_paths:
            - ./subconfig_[0-9].yml
            # Config files inside a subfolder
            - ./*/subconfig_[0-9].yml
            - ./*/**/subconfig_[0-9].yml

            schedules:
            # My schedules
            - name: modified-test-meltano-yml
              extractor: tap-meltano-yml
              loader: target-meltano-yml
              transform: only  # Only update dbt models
              start_date: 2020-08-05 00:00:00
              interval: '@once' # Run only once

            jobs:  # My jobs
            # An EL job with mapping
            - name: my-job
              tasks:
              - >-
                tap-meltano-yml
                map-meltano-yml
                target-meltano-yml

            environments:
            # My meltano environments
            - name: test-meltano-environment
              env:
                TEST: TEST-MELTANO

            plugins:
              # Project plugins
              extractors:
              - name: tap-meltano-yml # Comment on array element
                settings:
                - name: token
                  kind: password
                  description: >-
                    Token for the API.
                    This is a secret.

              - name: modified-tap-subconfig-2-yml

              mappers:
              # My mappers
              - name: map-meltano-yml
                # These are some mappings
                mappings:
                - name: transform-meltano-yml

              loaders:
              - name: target-meltano-yml
              - name: modified-target-subconfig-1-yml

        """

        assert contents == dedent(expected_contents)

        expected_subconfig_2_contents = """\
            plugins:
              # Subconfig 2 Plugins
              loaders:
              - name: target-subconfig-2-yml  # Subconfig 2 Loader

            schedules:
            # Subconfig 2 Schedules
            - name: test-subconfig-2-yml
              extractor: tap-subconfig-2-yml
              loader: target-subconfig-2-yml
              transform: skip
              start_date: 2020-08-04 00:00:00
              interval: '@once' # Run only once

            environments:
            # Subconfig 2 Environments
            - name: test-subconfig-2-yml
              env:
                TEST: TEST-SUBCONFIG-2-YML
        """

        included_path = project_files.root / "subconfig_2.yml"
        assert included_path.read_text() == dedent(expected_subconfig_2_contents)

    @pytest.mark.order(-1)
    def test_remove_all_file_contents(self, project_files):
        meltano_config = project_files.load()
        meltano_config["plugins"]["extractors"] = [
            entry
            for entry in meltano_config["plugins"]["extractors"]
            if entry["name"] != "tap-subconfig-2-yml"
        ]
        meltano_config["plugins"]["loaders"] = [
            entry
            for entry in meltano_config["plugins"]["loaders"]
            if entry["name"] != "target-subconfig-2-yml"
        ]
        meltano_config["schedules"] = [
            entry
            for entry in meltano_config["schedules"]
            if entry["name"] != "test-subconfig-2-yml"
        ]
        meltano_config["environments"] = [
            entry
            for entry in meltano_config["environments"]
            if entry["name"] != "test-subconfig-2-yml"
        ]
        project_files.update(meltano_config)

        expected_subconfig_2_contents = """\
        plugins: {}
        schedules: []
        jobs: []
        environments: []
        """

        included_path = project_files.root / "subconfig_2.yml"
        assert included_path.read_text() == dedent(expected_subconfig_2_contents)
