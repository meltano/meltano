from __future__ import annotations

import json
import platform

import pytest
from mock import AsyncMock, mock

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.project import Project


class TestCliConfig:
    def test_config(self, project: Project, cli_runner, tap, project_plugins_service):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            if platform.system() == "Windows":
                pytest.xfail(
                    "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
                )
            result = cli_runner.invoke(cli, ["config", tap.name])
            assert_cli_runner(result)

            json_config = json.loads(result.stdout)
            assert json_config["test"] == "mock"

    def test_config_extras(
        self, project: Project, cli_runner, tap, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", "--extras", tap.name])
            assert_cli_runner(result)

            json_config = json.loads(result.stdout)
            assert "_select" in json_config

    def test_config_env(
        self, project: Project, cli_runner, tap, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            if platform.system() == "Windows":
                pytest.xfail(
                    "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
                )
            result = cli_runner.invoke(cli, ["config", "--format=env", tap.name])
            assert_cli_runner(result)

            assert "TAP_MOCK_TEST='mock'" in result.stdout

    def test_config_meltano(
        self, project: Project, cli_runner, engine_uri, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", "meltano"])
            assert_cli_runner(result)

            json_config = json.loads(result.stdout)
            assert json_config["database_uri"] == engine_uri
            assert json_config["cli"]["log_level"] == "info"

    def test_config_meltano_set(
        self, project: Project, cli_runner, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(
                cli, ["config", "meltano", "set", "cli.log_config", "log_config.yml"]
            )
            assert_cli_runner(result)
            assert (
                "Meltano setting 'cli.log_config' was set in `meltano.yml`: 'log_config.yml'"
                in result.stdout
            )

    def test_config_test(
        self, project: Project, cli_runner, tap, project_plugins_service
    ):

        mock_invoke = mock.Mock()
        mock_invoke.sterr.at_eof.side_effect = True
        mock_invoke.stdout.at_eof.side_effect = (False, True)
        mock_invoke.wait = AsyncMock(return_value=-1)
        mock_invoke.returncode = -1
        payload = json.dumps({"type": "RECORD"}).encode()
        mock_invoke.stdout.readline = AsyncMock(return_value=b"%b" % payload)

        with mock.patch(
            "meltano.core.plugin_test_service.PluginInvoker.invoke_async",
            return_value=mock_invoke,
        ) as mocked_invoke:
            with mock.patch(
                "meltano.cli.config.ProjectPluginsService",
                return_value=project_plugins_service,
            ):
                result = cli_runner.invoke(cli, ["config", tap.name, "test"])
                assert mocked_invoke.assert_called_once
                assert_cli_runner(result)

                assert "Plugin configuration is valid" in result.stdout

    def test_config_meltano_test(self, project: Project, cli_runner):
        result = cli_runner.invoke(cli, ["config", "meltano", "test"])

        assert result.exit_code == 1
        assert (
            str(result.exception)
            == "Testing of the Meltano project configuration is not supported"
        )


class TestCliConfigSet:
    def test_environments_order_of_precedence(
        self, project: Project, cli_runner, tap, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            # set base config in `meltano.yml`
            result = cli_runner.invoke(
                cli,
                ["--no-environment", "config", "tap-mock", "set", "test", "base-mock"],
            )
            assert_cli_runner(result)
            base_tap_config = next(
                (
                    tap
                    for tap in project.meltano["plugins"]["extractors"]
                    if tap["name"] == "tap-mock"
                ),
                {},
            )
            assert base_tap_config["config"]["test"] == "base-mock"

            # set base config in `meltano.yml` -- ignore default environment
            result = cli_runner.invoke(
                cli,
                ["config", "tap-mock", "set", "test", "base-mock-no-default"],
            )
            assert_cli_runner(result)
            base_tap_config = next(
                (
                    tap
                    for tap in project.meltano["plugins"]["extractors"]
                    if tap["name"] == "tap-mock"
                ),
                {},
            )
            assert base_tap_config["config"]["test"] == "base-mock-no-default"

            # set dev environment config in `meltano.yml`
            result = cli_runner.invoke(
                cli,
                ["--environment=dev", "config", "tap-mock", "set", "test", "dev-mock"],
            )
            assert_cli_runner(result)
            dev_env = next(
                (
                    env
                    for env in project.meltano["environments"]
                    if env["name"] == "dev"
                ),
                {},
            )
            tap_config = next(
                (
                    tap
                    for tap in dev_env["config"]["plugins"]["extractors"]
                    if tap["name"] == "tap-mock"
                ),
                {},
            )
            assert tap_config["config"]["test"] == "dev-mock"
