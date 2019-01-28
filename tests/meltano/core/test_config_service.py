import pytest
import yaml
import os
import shutil

from meltano.core.config_service import ConfigService
from meltano.core.plugin import Plugin, PluginType


def make_meltano_yml(project):
    with open(project.meltanofile, "w") as f:
        f.write(
            yaml.dump(
                {
                    "plugins": {
                        "extractors": [
                            {
                                "name": "gitlab",
                                "pip_url": "git+https://gitlab.com/meltano/tap-gitlab.git",
                            }
                        ],
                        "loaders": [
                            {
                                "name": "csv",
                                "pip_url": "git+https://gitlab.com/meltano/target-csv.git",
                            }
                        ],
                    }
                }
            )
        )


def make_database_yml(project):
    with open(project.meltano_dir(".database_test.yml"), "w") as f:
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
    @pytest.fixture
    def subject(self, project):
        make_meltano_yml(project)
        make_database_yml(project)
        return ConfigService(project)

    def test_default_init_should_not_fail(self, subject):
        assert subject

    def test_get_extractors(self, subject):
        extractors = list(subject.get_extractors())
        assert len(extractors) == 1
        assert all(map(lambda p: p.type == PluginType.EXTRACTORS, extractors))

    def test_get_loaders(self, subject):
        loaders = list(subject.get_loaders())
        assert len(loaders) == 1
        assert all(map(lambda p: p.type == PluginType.LOADERS, loaders))

    def test_database_config(self, subject):
        assert subject.get_database("test") == {
            "database": "test",
            "host": "127.0.0.1",
            "name": "test",
            "password": "hatpants",
            "root_name": "TEST",
            "schema": "test",
            "username": "test",
        }
