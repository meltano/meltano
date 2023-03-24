"""Test the schedule command."""

from __future__ import annotations

import json
import re
import typing as t
from urllib.parse import urljoin

import pytest
from aioresponses import aioresponses
from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from meltano.cloud.api import MeltanoCloudClient
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudProjectSchedule


class TestScheduleCommand:
    """Test the logs command."""

    def test_schedule_enable(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        client: MeltanoCloudClient,
        config: MeltanoCloudConfig,
    ):
        url = urljoin(
            client.api_url,
            "/".join(
                (
                    "schedules",
                    "v1",
                    tenant_resource_key,
                    internal_project_id,
                    "dev",
                    "daily",
                    "enabled",
                )
            ),
        )
        runner = CliRunner()
        for cmd in ("enable", "disable"):
            for opts in (
                ("--deployment=dev", cmd, "--schedule=daily"),
                ("--schedule=daily", "--deployment=dev", cmd),
                (cmd, "--schedule=daily", "--deployment=dev"),
                ("--schedule=daily", cmd, "--deployment=dev"),
            ):
                with aioresponses() as m:
                    m.get(
                        f"{config.base_auth_url}/oauth2/userInfo",
                        status=200,
                        body=json.dumps({"sub": "meltano-cloud-test"}),
                    )
                    m.put(url, status=204)
                    result = runner.invoke(
                        cli,
                        ("--config-path", config.config_path, "schedule", *opts),
                    )
                    assert result.exit_code == 0, result.output
                    assert not result.output

    @pytest.fixture
    def schedules(self) -> list[CloudProjectSchedule]:
        return [
            {
                "deployment_name": "deployment 1",
                "schedule_name": "schedule 1",
                "interval": "1 2 * * *",
                "enabled": True,
            },
            {
                "deployment_name": "deployment 2",
                "schedule_name": "schedule 2",
                "interval": "15,45 */2 * * 1,3,5",
                "enabled": False,
            },
        ]

    @pytest.fixture
    def schedules_get_reponse(
        self,
        schedules: list[CloudProjectSchedule],
        tenant_resource_key: str,
        internal_project_id: str,
        client: MeltanoCloudClient,
        config: MeltanoCloudConfig,
    ) -> None:
        path = f"schedules/v1/{tenant_resource_key}/{internal_project_id}"
        url = urljoin(client.api_url, path)
        pattern = re.compile(f"^{url}(\\?.*)?$")
        with aioresponses() as m:
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.get(
                pattern,
                status=200,
                payload={"results": schedules, "pagination": None},
            )
            yield

    @pytest.mark.usefixtures("schedules_get_reponse")
    def test_schedule_list_table(self, config: MeltanoCloudConfig):
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "schedule", "list"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭──────────────┬────────────┬─────────────────────┬──────────────┬───────────╮\n"  # noqa: E501
            "│ Deployment   │ Schedule   │ Interval            │   Runs / Day │ Enabled   │\n"  # noqa: E501
            "├──────────────┼────────────┼─────────────────────┼──────────────┼───────────┤\n"  # noqa: E501
            "│ deployment 1 │ schedule 1 │ 1 2 * * *           │        1.000 │ True      │\n"  # noqa: E501
            "│ deployment 2 │ schedule 2 │ 15,45 */2 * * 1,3,5 │       10.268 │ False     │\n"  # noqa: E501
            "╰──────────────┴────────────┴─────────────────────┴──────────────┴───────────╯\n"  # noqa: E501
        )

    @pytest.mark.usefixtures("schedules_get_reponse")
    def test_schedule_list_json(
        self,
        schedules: list[CloudProjectSchedule],
        config: MeltanoCloudConfig,
    ):
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "schedule",
                "list",
                "--format=json",
            ),
        )
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == schedules
