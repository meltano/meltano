"""Test the schedule command."""

from __future__ import annotations

import json
import typing as t
from urllib.parse import urljoin

from aioresponses import aioresponses
from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from meltano.cloud.api import MeltanoCloudClient
    from meltano.cloud.api.config import MeltanoCloudConfig


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
