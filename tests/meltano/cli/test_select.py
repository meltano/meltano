import json

from asserts import assert_cli_runner
from asynctest import mock
from meltano.cli import cli


class TestCliSelect:
    def test_add_select_pattern(
        self, project, cli_runner, tap, project_plugins_service
    ):
        with mock.patch(
            "meltano.core.select_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            # add select pattern
            _ = cli_runner.invoke(cli, ["select", tap.name, "mock", "*"])
            assert_cli_runner(_)
            result = cli_runner.invoke(cli, ["config", "--extras", tap.name])
            assert_cli_runner(result)
            # verify pattern was added
            json_config = json.loads(result.stdout)
            assert "mock.*" in json_config["_select"]

    def test_remove_select_pattern(
        self, project, cli_runner, tap, project_plugins_service
    ):
        with mock.patch(
            "meltano.core.select_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch(
            "meltano.cli.config.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            # check select pattern exists (this may not be necessary?)
            result = cli_runner.invoke(cli, ["config", "--extras", tap.name])
            assert_cli_runner(result)
            json_config = json.loads(result.stdout)
            assert "mock.*" in json_config["_select"]
            # remove select pattern
            _ = cli_runner.invoke(cli, ["select", "--rm", tap.name, "mock", "*"])
            assert_cli_runner(_)
            result = cli_runner.invoke(cli, ["config", "--extras", tap.name])
            assert_cli_runner(result)
            # verify select pattern removed
            json_config = json.loads(result.stdout)
            assert "mock.*" not in json_config["_select"]
