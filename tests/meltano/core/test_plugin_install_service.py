import os
import shutil
from unittest import mock

import pytest
import yaml

from meltano.core.config_service import ConfigService
from meltano.core.plugin_install_service import PluginInstallService


class TestPluginInstallService:
    @pytest.fixture
    def subject(self, project):
        with open(project.meltanofile, "w") as f:
            f.write(
                yaml.dump(
                    {
                        "plugins": {
                            "extractors": [
                                {
                                    "name": "tap-gitlab",
                                    "pip_url": "git+https://gitlab.com/meltano/tap-gitlab.git",
                                },
                                {
                                    "name": "tap-gitlab--child-1",
                                    "inherit_from": "tap-gitlab"
                                }
                            ],
                            "loaders": [
                                {
                                    "name": "target-csv",
                                    "pip_url": "git+https://gitlab.com/meltano/target-csv.git",
                                }
                            ],
                        }
                    }
                )
            )

        return PluginInstallService(project)

    def test_default_init_should_not_fail(self, subject):
        assert subject

    @pytest.mark.slow
    def test_install_all(self, subject):
        all_plugins = subject.install_all_plugins()
        assert len(all_plugins) == 3
        assert all_plugins[0].successful
        assert all_plugins[1].successful
        assert all_plugins[2].successful
