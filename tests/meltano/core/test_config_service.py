import pytest
import yaml
import os
import shutil

from meltano.core.config_service import ConfigService


def make_meltano_yml():
    with open(os.path.join("./", "meltano.yml"), "w") as f:
        f.write(
            yaml.dump(
                {
                    "extractors": [
                        {
                            "name": "first",
                            "url": "git+https://gitlab.com/meltano/tap-first.git",
                        }
                    ],
                    "loaders": [
                        {
                            "name": "csv",
                            "url": "git+https://gitlab.com/meltano/target-csv.git",
                        }
                    ],
                }
            )
        )


def make_database_yml():
    with open(os.path.join("./.meltano/.database_test.yml"), "w") as f:
        f.write(
            yaml.dump(
                {
                    "database": "test",
                    "host": "127.0.0.1",
                    "name": "test",
                    "password": "hatpants",
                    "root_name": "TEST",
                    "schema": "test",
                    "username": "test",
                }
            )
        )


class TestConfigService:
    def test_default_init_should_not_fail(self):
        config_service = ConfigService()
        assert config_service

    def test_get_extractors(self):
        make_meltano_yml()
        config_service = ConfigService()
        assert config_service.get_extractors() == [
            {"name": "first", "url": "git+https://gitlab.com/meltano/tap-first.git"}
        ]

    def test_get_extractors(self):
        make_meltano_yml()
        config_service = ConfigService()
        assert config_service.get_loaders() == [
            {"name": "csv", "url": "git+https://gitlab.com/meltano/target-csv.git"}
        ]

    def test_database_config(self):
        config_service = ConfigService()
        make_database_yml()
        assert config_service.get_database("test") == {
            "database": "test",
            "host": "127.0.0.1",
            "name": "test",
            "password": "hatpants",
            "root_name": "TEST",
            "schema": "test",
            "username": "test",
        }
