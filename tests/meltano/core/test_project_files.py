import os
import tempfile
from pathlib import Path

import pytest  # noqa: F401


@pytest.fixture
def cd_temp_subdir():
    original_dir = Path.cwd()
    with tempfile.TemporaryDirectory(dir=original_dir) as name:
        new_dir = Path(name).resolve()
        os.chdir(new_dir)
        yield new_dir
    os.chdir(original_dir)


@pytest.fixture
def cd_temp_dir():
    original_dir = Path.cwd()
    with tempfile.TemporaryDirectory() as name:
        new_dir = Path(name).resolve()
        os.chdir(new_dir)
        yield new_dir
    os.chdir(original_dir)


class TestProjectFiles:
    def test_resolve_subfiles(self, project_files):
        assert project_files._meltano_file_path == (project_files.root / "meltano.yml")
        assert project_files.meltano == {
            "version": 1,
            "default_environment": "test-meltano-environment",
            "include_paths": [
                "./subconfig_[0-9].yml",
                "./*/subconfig_[0-9].yml",
                "./*/**/subconfig_[0-9].yml",
            ],
            "plugins": {
                "extractors": [{"name": "tap-meltano-yml"}],
                "loaders": [{"name": "target-meltano-yml"}],
            },
            "schedules": [
                {
                    "name": "test-meltano-yml",
                    "extractor": "tap-meltano-yml",
                    "loader": "target-meltano-yml",
                    "transform": "skip",
                    "interval": "@once",
                }
            ],
            "environments": [
                {"name": "test-meltano-environment", "env": {"TEST": "TEST-MELTANO"}}
            ],
        }
        assert project_files.include_paths == [
            (project_files.root / "subconfig_2.yml"),
            (project_files.root / "subfolder" / "subconfig_1.yml"),
        ]

    def test_resolve_from_subdir(self, project_files, cd_temp_subdir):
        assert Path.cwd() == cd_temp_subdir
        assert cd_temp_subdir.parent == project_files.root
        assert project_files.include_paths == [
            (project_files.root / "subconfig_2.yml"),
            (project_files.root / "subfolder" / "subconfig_1.yml"),
        ]

    def test_resolve_from_any_dir(self, project_files, cd_temp_dir):
        assert Path.cwd() == cd_temp_dir
        assert project_files.include_paths == [
            (project_files.root / "subconfig_2.yml"),
            (project_files.root / "subfolder" / "subconfig_1.yml"),
        ]

    def test_load(self, project_files):
        expected_result = {
            "version": 1,
            "default_environment": "test-meltano-environment",
            "include_paths": [
                "./subconfig_[0-9].yml",
                "./*/subconfig_[0-9].yml",
                "./*/**/subconfig_[0-9].yml",
            ],
            "plugins": {
                "extractors": [
                    {"name": "tap-meltano-yml"},
                    {"name": "tap-subconfig-2-yml"},
                    {"name": "tap-subconfig-1-yml"},
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
                    "interval": "@once",
                },
                {
                    "name": "test-subconfig-2-yml",
                    "extractor": "tap-subconfig-2-yml",
                    "loader": "target-subconfig-2-yml",
                    "transform": "skip",
                    "interval": "@once",
                },
                {
                    "name": "test-subconfig-1-yml",
                    "extractor": "tap-subconfig-1-yml",
                    "loader": "target-subconfig-1-yml",
                    "transform": "skip",
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
        }
        read_result = project_files.load()
        assert read_result == expected_result

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
            "include_paths": [
                "./subconfig_[0-9].yml",
                "./*/subconfig_[0-9].yml",
                "./*/**/subconfig_[0-9].yml",
            ],
            "plugins": {
                "extractors": [
                    {"name": "tap-meltano-yml"},
                    {"name": "modified-tap-subconfig-2-yml"},
                    {"name": "tap-subconfig-1-yml"},
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
                    "transform": "skip",
                },
                {
                    "extractor": "tap-subconfig-2-yml",
                    "interval": "@once",
                    "loader": "target-subconfig-2-yml",
                    "name": "test-subconfig-2-yml",
                    "transform": "skip",
                },
                {
                    "extractor": "tap-subconfig-1-yml",
                    "interval": "@once",
                    "loader": "target-subconfig-1-yml",
                    "name": "test-subconfig-1-yml",
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
            "version": 2,
        }
        read_result = project_files.load()
        assert read_result == expected_result
