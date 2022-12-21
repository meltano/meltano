from __future__ import annotations

import json

from mock import mock

from asserts import assert_cli_runner
from meltano.cli import cli


class TestCliSelect:
    def test_update_select_pattern(
        self, project, cli_runner, tap, project_plugins_service
    ):
        with mock.patch(
            "meltano.core.select_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            with mock.patch(
                "meltano.cli.config.ProjectPluginsService",
                return_value=project_plugins_service,
            ):
                # add select pattern
                result = cli_runner.invoke(
                    cli, ["--no-environment", "select", tap.name, "mock", "*"]
                )
                assert_cli_runner(result)
                # verify pattern was added
                result = cli_runner.invoke(cli, ["config", "--extras", tap.name])
                assert_cli_runner(result)
                json_config = json.loads(result.stdout)
                assert "mock.*" in json_config["_select"]
                # remove select pattern
                result = cli_runner.invoke(
                    cli, ["--no-environment", "select", tap.name, "--rm", "mock", "*"]
                )
                assert_cli_runner(result)
                # verify select pattern removed
                result = cli_runner.invoke(cli, ["config", "--extras", tap.name])
                assert_cli_runner(result)
                json_config = json.loads(result.stdout)
                assert "mock.*" not in json_config["_select"]
