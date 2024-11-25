from __future__ import annotations

import json

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.plugin.singer.catalog import (
    ListSelectedExecutor,
    SelectedNode,
    SelectionType,
)
from meltano.core.select_service import SelectService


class TestCliSelect:
    @pytest.mark.parametrize(
        "environment",
        (
            pytest.param(None, id="no-environment"),
            pytest.param("dev", id="dev"),
        ),
    )
    @pytest.mark.usefixtures("project")
    def test_update_select_pattern(self, cli_runner, tap, environment) -> None:
        environment_flag = () if environment is None else ("--environment", environment)
        # add select pattern
        result = cli_runner.invoke(
            cli,
            [*environment_flag, "select", tap.name, "mock", "*"],
        )
        assert_cli_runner(result)
        # verify pattern was added
        result = cli_runner.invoke(
            cli,
            [*environment_flag, "config", "--extras", tap.name],
        )
        assert_cli_runner(result)
        json_config = json.loads(result.stdout)
        assert "mock.*" in json_config["_select"]
        # remove select pattern
        result = cli_runner.invoke(
            cli,
            [*environment_flag, "select", tap.name, "--rm", "mock", "*"],
        )
        assert_cli_runner(result)
        # verify select pattern removed
        result = cli_runner.invoke(
            cli,
            [*environment_flag, "config", "--extras", tap.name],
        )
        assert_cli_runner(result)
        json_config = json.loads(result.stdout)
        assert "mock.*" not in json_config["_select"]

    @pytest.mark.usefixtures("project")
    def test_select_list(
        self,
        cli_runner,
        tap,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def mock_list_all(*args, **kwargs):  # noqa: ARG001
            result = ListSelectedExecutor()
            result.streams = {
                SelectedNode(key="users", selection=SelectionType.SELECTED),
            }
            result.properties = {
                "users": {
                    SelectedNode(key="id", selection=SelectionType.SELECTED),
                    SelectedNode(key="name", selection=SelectionType.EXCLUDED),
                    SelectedNode(key="secret", selection=SelectionType.UNSUPPORTED),
                },
            }
            return result

        monkeypatch.setattr(
            SelectService,
            "list_all",
            mock_list_all,
        )

        # list selection
        result = cli_runner.invoke(
            cli,
            [
                "--no-environment",
                "select",
                tap.name,
                "--list",
                "--all",
            ],
        )
        assert_cli_runner(result)

        assert "[selected   ] users.id" in result.stdout
        assert "[excluded   ] users.name" in result.stdout
        assert "[unsupported] users.secret" in result.stdout
