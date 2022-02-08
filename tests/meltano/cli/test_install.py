from unittest import mock

import pytest
import yaml
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
                project, [dbt, target, tap_gitlab, tap], parallelism=None, clean=False
            )

    def test_install_type(
        self,
        project,
        tap,
        tap_gitlab,
        target,
        dbt,
        mapper,
        cli_runner,
        project_plugins_service,
    ):
        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_e:
            install_plugin_mock_e.return_value = True

            result = cli_runner.invoke(cli, ["install", "extractors"])
            assert_cli_runner(result)

            install_plugin_mock_e.assert_called_once_with(
                project, [tap_gitlab, tap], parallelism=None, clean=False
            )

        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_l:
            install_plugin_mock_l.return_value = True

            result = cli_runner.invoke(cli, ["install", "loaders"])
            assert_cli_runner(result)

            install_plugin_mock_l.assert_called_once_with(
                project, [target], parallelism=None, clean=False
            )

        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_m:
            install_plugin_mock_m.return_value = True

            result = cli_runner.invoke(cli, ["install", "mappers"])
            assert_cli_runner(result)

            assert install_plugin_mock_m.call_count == 1
            seen_mappers = install_plugin_mock_m.call_args[0][1]
            assert len(seen_mappers) == 3
            assert seen_mappers[0] == mapper
            assert not seen_mappers[1].extra_config.get("_mapper")
            assert not seen_mappers[2].extra_config.get("_mapper")

    def test_install_type_name(
        self,
        project,
        tap,
        tap_gitlab,
        target,
        dbt,
        mapper,
        cli_runner,
        project_plugins_service,
    ):
        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_e:
            install_plugin_mock_e.return_value = True

            result = cli_runner.invoke(cli, ["install", "extractor", tap.name])
            assert_cli_runner(result)

            install_plugin_mock_e.assert_called_once_with(
                project, [tap], parallelism=None, clean=False
            )

        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_l:
            install_plugin_mock_l.return_value = True

            result = cli_runner.invoke(cli, ["install", "loader", target.name])
            assert_cli_runner(result)

            install_plugin_mock_l.assert_called_once_with(
                project, [target], parallelism=None, clean=False
            )

        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock_m:
            install_plugin_mock_m.return_value = True

            result = cli_runner.invoke(cli, ["install", "mapper", mapper.name])
            assert_cli_runner(result)

            assert install_plugin_mock_m.call_count == 1
            seen_mappers = install_plugin_mock_m.call_args[0][1]
            assert len(seen_mappers) == 3
            assert seen_mappers[0] == mapper
            assert not seen_mappers[1].extra_config.get("_mapper")
            assert not seen_mappers[2].extra_config.get("_mapper")

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

            install_plugin_mock.assert_called_once_with(
                project, [tap_gitlab, tap], parallelism=None, clean=False
            )

    def test_install_parallel(
        self,
        project,
        tap,
        tap_gitlab,
        target,
        dbt,
        mapper,
        cli_runner,
        project_plugins_service,
    ):
        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install", "--parallelism=10"])
            assert_cli_runner(result)

            assert install_plugin_mock.call_count == 1
            assert install_plugin_mock.mock_calls[0].args[0] == project
            seen_plugins = install_plugin_mock.mock_calls[0].args[1]
            assert dbt in seen_plugins
            assert tap_gitlab in seen_plugins
            assert target in seen_plugins
            assert tap in seen_plugins
            assert mapper in seen_plugins
            assert install_plugin_mock.mock_calls[0].kwargs["parallelism"] == 10
            assert not install_plugin_mock.mock_calls[0].kwargs["clean"]

    def test_clean_install(
        self,
        project,
        tap,
        tap_gitlab,
        target,
        dbt,
        mapper,
        cli_runner,
        project_plugins_service,
    ):
        with mock.patch(
            "meltano.cli.install.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.install.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            result = cli_runner.invoke(cli, ["install", "--clean"])
            assert_cli_runner(result)

            assert install_plugin_mock.call_count == 1
            assert install_plugin_mock.mock_calls[0].args[0] == project
            seen_plugins = install_plugin_mock.mock_calls[0].args[1]
            assert dbt in seen_plugins
            assert tap_gitlab in seen_plugins
            assert target in seen_plugins
            assert tap in seen_plugins
            assert mapper in seen_plugins
            assert not install_plugin_mock.mock_calls[0].kwargs["parallelism"]
            assert install_plugin_mock.mock_calls[0].kwargs["clean"]
