from __future__ import annotations

import json
import typing as t
from unittest import mock

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.plugin.singer.catalog import (
    ListSelectedExecutor,
    SelectedNode,
    SelectionType,
)
from meltano.core.select_service import SelectService

if t.TYPE_CHECKING:
    from fixtures.cli import MeltanoCliRunner
    from meltano.core.plugin.project_plugin import ProjectPlugin


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

        with mock.patch(
            "meltano.core.select_service.PluginSettingsService.get",
            return_value=["users.id", "!users.name"],
        ):
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

        assert "users.id" in result.stdout
        assert "!users.name" in result.stdout
        assert "[selected   ] users.id" in result.stdout
        assert "[excluded   ] users.name" in result.stdout
        assert "[unsupported] users.secret" in result.stdout

    @pytest.mark.parametrize(
        ("show_all", "entities"),
        (
            pytest.param(
                True,
                [
                    {
                        "stream": "users",
                        "property": "id",
                        "selection": "selected",
                    },
                    {
                        "stream": "users",
                        "property": "name",
                        "selection": "excluded",
                    },
                    {
                        "stream": "users",
                        "property": "secret",
                        "selection": "unsupported",
                    },
                ],
                id="show-all",
            ),
            pytest.param(
                False,
                [
                    {
                        "stream": "users",
                        "property": "id",
                        "selection": "selected",
                    },
                ],
                id="show-selected",
            ),
        ),
    )
    @pytest.mark.usefixtures("project")
    def test_select_list_json(
        self,
        cli_runner: MeltanoCliRunner,
        tap: ProjectPlugin,
        monkeypatch: pytest.MonkeyPatch,
        show_all: bool,  # noqa: FBT001
        entities: list[dict[str, t.Any]],
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

        args = ["--no-environment", "select", tap.name, "--json"]
        if show_all:
            args.append("--all")

        with mock.patch(
            "meltano.core.select_service.PluginSettingsService.get",
            return_value=["users.id", "!users.name"],
        ):
            # list selection
            result = cli_runner.invoke(cli, args)

        assert_cli_runner(result)

        json_result = json.loads(result.stdout)
        assert json_result["enabled_patterns"] == ["users.id", "!users.name"]
        assert json_result["entities"] == entities
