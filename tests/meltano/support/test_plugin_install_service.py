import pytest

from meltano.support.plugin_install_service import (
    PluginInstallService,
    PluginInstallServicePluginNotFoundError,
)

class TestPluginInstallService:

    def test_default_init_should_not_fail(self):
        # This fails in new project without a ./meltano.yml
        # Fix it :-)
        install_service = PluginInstallService()
        assert install_service
