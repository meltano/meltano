import yaml
import pytest
from unittest import mock

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.plugin import PluginType
from meltano.core.project_add_service import PluginAlreadyAddedException


class TestCliInstall:
    @pytest.fixture(scope="class")
    def tap_gitlab(self, project_add_service):
        try:
            return project_add_service.add(PluginType.EXTRACTORS, "tap-gitlab")
        except PluginAlreadyAddedException as err:
            return err.plugin

    def test_install(
        self, project, tap, tap_gitlab, target, dbt, cli_runner, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install"])
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(
                project, [dbt, target, tap_gitlab, tap]
            )

    def test_install_type(
        self, project, tap, tap_gitlab, target, dbt, cli_runner, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install", "extractors"])
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(project, [tap_gitlab, tap])

        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install", "loaders"])
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(project, [target])

    def test_install_type_name(
        self, project, tap, tap_gitlab, target, dbt, cli_runner, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install", "extractor", tap.name])
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(project, [tap])

        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install", "loader", target.name])
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(project, [target])

    def test_install_multiple(
        self, project, tap, tap_gitlab, target, dbt, cli_runner, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(
                cli, ["install", "extractors", tap.name, tap_gitlab.name]
            )
            assert_cli_runner(result)

            install_plugin_mock.assert_called_once_with(project, [tap_gitlab, tap])
