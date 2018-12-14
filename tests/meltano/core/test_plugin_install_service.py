import pytest
import yaml
import os
import shutil

from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.config_service import ConfigService


class TestPluginInstallService:
    @pytest.fixture
    def subject(self, project):
        with project.meltanofile.open("w") as f:
            f.write(
                """
                    extractors:
                    - {name: tap-gitlab, pip_url: 'git+https://gitlab.com/meltano/tap-gitlab.git'}
                    loaders:
                    - {name: target-csv, pip_url: 'git+https://gitlab.com/meltano/target-csv.git'}
            """
            )

        return PluginInstallService(project)

    def test_default_init_should_not_fail(self, subject):
        assert subject

    @pytest.mark.slow
    def test_install_all(self, subject):
        all_plugins = subject.install_all_plugins()
        assert len(all_plugins["errors"]) == 0
        assert len(all_plugins["installed"]) == 2
        assert all_plugins["installed"][0]["status"] == "success"
        assert all_plugins["installed"][1]["status"] == "success"
