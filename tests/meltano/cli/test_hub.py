from __future__ import annotations

import typing as t

import mock

from asserts import assert_cli_runner
from meltano.cli import cli

if t.TYPE_CHECKING:
    from collections import Counter

    from click.testing import CliRunner
    from requests_mock import Mocker as RequestsMocker

    from meltano.core.project import Project


class TestCliHub:
    def test_ping(
        self,
        project: Project,
        cli_runner: CliRunner,
        hub_request_counter: Counter,
    ) -> None:
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
    ) -> None:
        hub_api = project.hub_service.hub_api_url
        requests_mock.get(
            hub_api,
            exc=ConnectionError("Connection refused"),
        )
        result = cli_runner.invoke(cli, ("hub", "ping"))
        assert f"Error: Failed to connect to the Hub at {hub_api!r}" in result.stderr
        assert result.exit_code == 1
        assert not hub_request_counter
