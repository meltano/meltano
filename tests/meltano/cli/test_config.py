import json
from unittest import mock

import dotenv
import pytest
from asserts import assert_cli_runner
from meltano.cli import cli


class TestCliConfig:
    def test_config(self, project, cli_runner, tap, project_plugins_service):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", tap.name])
            assert_cli_runner(result)

            json_config = json.loads(result.stdout)
            assert json_config["test"] == "mock"

    def test_config_extras(self, project, cli_runner, tap, project_plugins_service):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", "--extras", tap.name])
            assert_cli_runner(result)

            json_config = json.loads(result.stdout)
            assert "_select" in json_config

    def test_config_env(self, project, cli_runner, tap, project_plugins_service):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", "--format=env", tap.name])
            assert_cli_runner(result)

            assert 'TAP_MOCK_TEST="mock"' in result.stdout

    def test_config_meltano(
        self, project, cli_runner, engine_uri, project_plugins_service
    ):
        with mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            result = cli_runner.invoke(cli, ["config", "meltano"])
            assert_cli_runner(result)

            json_config = json.loads(result.stdout)
            assert json_config["send_anonymous_usage_stats"] == False
            assert json_config["database_uri"] == engine_uri
            assert json_config["cli"]["log_level"] == "info"
