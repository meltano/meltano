import os
import pytest
from unittest import mock

from meltano.cli import cli
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginMissingError


class TestCliAdd:
    @pytest.mark.parametrize(
        "plugin_type,plugin_name",
        [
            (PluginType.EXTRACTORS, "tap-carbon-intensity"),
            (PluginType.LOADERS, "target-sqlite"),
            (PluginType.MODELS, "model-carbon-intensity-sqlite"),
            (PluginType.TRANSFORMERS, "dbt"),
            (PluginType.TRANSFORMS, "tap-carbon-intensity"),
            (PluginType.ORCHESTRATORS, "airflow"),
        ],
    )
    def test_add(self, plugin_type, plugin_name, project, cli_runner, config_service):
        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.get_plugin(plugin_type, plugin_name)

        res = cli_runner.invoke(cli, ["add", plugin_type.cli_command, plugin_name])

        assert res.exit_code == 0, res.stdout
        assert f"Installed '{plugin_name}'." in res.stdout

        project.reload()
        plugin = config_service.get_plugin(plugin_name, plugin_type)

        if plugin.name == "airflow":
            assert project.plugin_dir(plugin, "airflow.cfg").exists()
            assert project.plugin_dir(plugin, "airflow.db").exists()

    def test_add_missing(self, project, cli_runner, config_service):
        res = cli_runner.invoke(cli, ["add", "extractor", "tap-unknown"])

        assert res.exit_code == 1
        assert "'tap-unknown' is not supported" in res.stdout
        assert res.stderr

        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            project.reload()
            config_service.get_plugin("tap-unknown", PluginType.EXTRACTORS)

    @pytest.mark.xfail(reason="Uninstall not implemented yet.")
    def test_add_fails(self, project, cli_runner, config_service):
        res = cli_runner.invoke(cli, ["add", "extractor", "tap-mock"])

        assert res.exit_code == 1, res.stdout
        assert "Failed to install plugin 'tap-mock'" in res.stdout
        assert res.stderr

        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            project.reload()
            config_service.get_plugin("tap-mock", PluginType.EXTRACTORS)

    @mock.patch("meltano.cli.add.PluginInstallService", autospec=True)
    def test_add_custom(
        self, PluginInstallService, project, cli_runner, config_service
    ):
        service = PluginInstallService.return_value

        # it's important to have a stdout
        service.install_plugin.return_value.stdout = "Mocked install_plugin() called."
        service.test = 100

        stdin = os.linesep.join(
            ["-e path/to/tap-custom", "tap-custom-bin"]  # pip_url  # executable
        )

        res = cli_runner.invoke(
            cli, ["add", "--custom", "extractor", "tap-custom"], input=stdin
        )

        project.reload()
        plugin = config_service.get_plugin("tap-custom", PluginType.EXTRACTORS)
        assert plugin.name == "tap-custom"
        assert plugin.executable == "tap-custom-bin"

        service.create_venv.assert_called_once_with(plugin)
        service.install_plugin.assert_called_once_with(plugin)
