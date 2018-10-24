import pytest
import yaml
import os
import shutil

from meltano.support.plugin_install_service import (
    PluginInstallService,
    PluginInstallServicePluginNotFoundError,
)

class TestPluginInstallService:
    def test_default_init_should_not_fail(self):
        install_service = PluginInstallService()
        assert install_service

    def test_get_plugin_url(self):
        install_service = PluginInstallService()
        install_service.add_service.meltano_yml = yaml.load("""extractors:
- {name: first, url: 'git+https://gitlab.com/meltano/tap-first.git'}
loaders:
- {name: csv, url: 'git+https://gitlab.com/meltano/target-csv.git'}""")
        all_plugins = install_service.install_all_plugins()
        assert len(all_plugins['errors']) == 0
        assert len(all_plugins['installed']) == 2
        assert all_plugins['installed'][0]['status'] == 'success'
        assert all_plugins['installed'][1]['status'] == 'success'

        # Clean up
        shutil.rmtree('./.meltano')
        os.remove('./meltano.yml')


