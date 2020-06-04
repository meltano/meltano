import os
import pytest
import functools
from unittest import mock

from meltano.cli import cli
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginMissingError
from meltano.core.m5o.dashboards_service import DashboardsService
from meltano.core.m5o.reports_service import ReportsService


class TestCliAdd:
    @pytest.mark.parametrize(
        "plugin_type,plugin_name",
        [
            (PluginType.EXTRACTORS, "tap-carbon-intensity"),
            (PluginType.LOADERS, "target-sqlite"),
            (PluginType.TRANSFORMS, "tap-carbon-intensity"),
            (PluginType.MODELS, "model-carbon-intensity"),
            (PluginType.DASHBOARDS, "dashboard-google-analytics"),
            (PluginType.ORCHESTRATORS, "airflow"),
            (PluginType.TRANSFORMERS, "dbt"),
        ],
    )
    def test_add(self, plugin_type, plugin_name, project, cli_runner, config_service):
        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.find_plugin(plugin_name, plugin_type=plugin_type)

        with mock.patch(
            "meltano.cli.add.PluginInstallService.install_plugin"
        ) as install_plugin_mock:
            install_plugin_mock.return_value = mock.Mock(
                stdout=f"Mocked {plugin_name} install."
            )
            res = cli_runner.invoke(cli, ["add", plugin_type.singular, plugin_name])

        assert res.exit_code == 0, res.stdout
        assert f"Installed {plugin_type.singular} '{plugin_name}'." in res.stdout

        assert config_service.find_plugin(plugin_name, plugin_type)

    def test_add_transform(self, project, cli_runner):
        res = cli_runner.invoke(cli, ["add", "transform", "tap-google-analytics"])

        assert res.exit_code == 0

        assert (
            "dbt-tap-google-analytics"
            in project.root_dir("transform/packages.yml").open().read()
        )
        assert (
            "tap_google_analytics"
            in project.root_dir("transform/dbt_project.yml").open().read()
        )

    def test_add_dashboard(self, project, cli_runner):
        def install():
            return cli_runner.invoke(
                cli, ["add", "dashboard", "dashboard-google-analytics"]
            )

        res = install()
        assert res.exit_code == 0

        dashboards_service = DashboardsService(project)
        dashboards_count = len(dashboards_service.get_dashboards())

        assert dashboards_count > 0

        reports_service = ReportsService(project)
        reports_count = len(reports_service.get_reports())
        assert reports_count > 0

        # Verify that reinstalling doesn't duplicate dashboards and reports
        res = install()
        assert res.exit_code == 0

        assert len(dashboards_service.get_dashboards()) == dashboards_count
        assert len(reports_service.get_reports()) == reports_count

    def test_add_related(self, project, cli_runner, config_service):
        with mock.patch(
            "meltano.cli.add.PluginInstallService.install_plugin"
        ) as install_plugin_mock:
            install_plugin_mock.return_value = mock.Mock(stdout=f"Mocked install.")
            res = cli_runner.invoke(
                cli, ["add", "--include-related", "extractor", "tap-google-analytics"]
            )

        assert res.exit_code == 0

        # Verify that all related plugins are installed
        assert config_service.find_plugin("tap-google-analytics", PluginType.EXTRACTORS)
        assert config_service.find_plugin("tap-google-analytics", PluginType.TRANSFORMS)
        assert config_service.find_plugin("model-google-analytics", PluginType.MODELS)
        assert config_service.find_plugin(
            "dashboard-google-analytics", PluginType.DASHBOARDS
        )

    def test_add_missing(self, project, cli_runner, config_service):
        res = cli_runner.invoke(cli, ["add", "extractor", "tap-unknown"])

        assert res.exit_code == 1
        assert "'tap-unknown' is not supported" in res.stdout
        assert res.stderr

        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.find_plugin("tap-unknown", PluginType.EXTRACTORS)

    @pytest.mark.xfail(reason="Uninstall not implemented yet.")
    def test_add_fails(self, project, cli_runner, config_service):
        res = cli_runner.invoke(cli, ["add", "extractor", "tap-mock"])

        assert res.exit_code == 1, res.stdout
        assert "Failed to install plugin 'tap-mock'" in res.stdout
        assert res.stderr

        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.find_plugin("tap-mock", PluginType.EXTRACTORS)

    @mock.patch("meltano.cli.add.PluginInstallService", autospec=True)
    def test_add_custom(
        self, PluginInstallService, project, cli_runner, config_service
    ):
        service = PluginInstallService.return_value

        # it's important to have a stdout
        service.install_plugin.return_value.stdout = "Mocked install_plugin() called."
        service.test = 100

        stdin = os.linesep.join(
            # namespace, executable, pip_url
            ["custom", "-e path/to/tap-custom", "tap-custom-bin"]
        )

        res = cli_runner.invoke(
            cli, ["add", "--custom", "extractor", "tap-custom"], input=stdin
        )

        plugin = config_service.find_plugin("tap-custom", PluginType.EXTRACTORS)
        assert plugin.name == "tap-custom"
        assert plugin.executable == "tap-custom-bin"

        service.install_plugin.assert_called_once_with(plugin)
