import pytest
import yaml
import os
import shutil

from meltano.core.plugin_install_service import PluginInstallService


class TestPluginInstallService:
    def test_default_init_should_not_fail(self, project):
        install_service = PluginInstallService(project)
        assert install_service

    def test_get_plugin_url(self, project):
        install_service = PluginInstallService(project)
        install_service.add_service.meltano_yml = yaml.load(
            """extractors:
- {name: tap-first, url: 'git+https://gitlab.com/meltano/tap-first.git'}
loaders:
- {name: target-csv, url: 'git+https://gitlab.com/meltano/target-csv.git'}"""
        )
        all_plugins = install_service.install_all_plugins()
        assert len(all_plugins["errors"]) == 0
        assert len(all_plugins["installed"]) == 2
        assert all_plugins["installed"][0]["status"] == "success"
        assert all_plugins["installed"][1]["status"] == "success"
