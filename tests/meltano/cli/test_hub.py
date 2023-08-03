from __future__ import annotations

import typing as t
from collections import Counter

import mock
from click.testing import CliRunner

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.project import Project

if t.TYPE_CHECKING:
    from requests_mock import Mocker as RequestsMocker


class TestCliHub:
    def test_ping(
        self,
        project: Project,
        cli_runner: CliRunner,
        hub_request_counter: Counter,
    ):
        with mock.patch(
            "requests.adapters.HTTPAdapter.send",
            project.hub_service.session.get_adapter(
                project.hub_service.hub_api_url,
            ).send,
        ):
            result = cli_runner.invoke(cli, ("hub", "ping"))

        assert_cli_runner(result)

        assert hub_request_counter["/orchestrators/index"] == 1
        assert (
            f"Successfully connected to the Hub at {project.hub_service.hub_api_url!r}"
            in result.stdout
        )

    def test_ping_unreachable(
        self,
        project: Project,
        cli_runner: CliRunner,
        hub_request_counter: Counter,
        requests_mock: RequestsMocker,
    ):
        hub_api = project.hub_service.hub_api_url
        requests_mock.get(  # noqa: S113
            hub_api,
            exc=ConnectionError("Connection refused"),
        )
        result = cli_runner.invoke(cli, ("hub", "ping"))
        assert f"Error: Failed to connect to the Hub at {hub_api!r}" in result.stderr
        assert result.exit_code == 1
        assert not hub_request_counter
