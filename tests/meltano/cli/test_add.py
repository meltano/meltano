import pytest

from meltano.cli import cli
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginMissingError


class TestCliAdd:
    def test_add(self, project, cli_runner, config_service):
        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.get_plugin(PluginType.EXTRACTORS, "tap-carbon-intensity")

        res = cli_runner.invoke(cli, ["add", "extractor", "tap-carbon-intensity"])

        assert res.exit_code == 0
        assert "Installed 'tap-carbon-intensity'." in res.stdout

    def test_add_missing(self, project, cli_runner, config_service):
        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.get_plugin(PluginType.EXTRACTORS, "tap-unknown")

        res = cli_runner.invoke(cli, ["add", "extractor", "tap-unknown"])

        assert res.exit_code == 1
        assert "'tap-unknown' is not supported" in res.stdout
        assert res.stderr

    def test_add_fails(self, project, cli_runner, config_service):
        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.get_plugin(PluginType.EXTRACTORS, "tap-mock")

        res = cli_runner.invoke(cli, ["add", "extractor", "tap-mock"])

        assert res.exit_code == 1, res.stdout
        assert "Failed to install plugin 'tap-mock'" in res.stdout
        assert res.stderr
