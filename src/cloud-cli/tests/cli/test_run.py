"""Test the run command."""

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


class TestCloudRun:
    """Test the Meltano Cloud run command."""

    def test_run_ok(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        client: MeltanoCloudClient,
        config: MeltanoCloudConfig,
    ):
        """Test the `run` subcommand."""
        deployment = "sandbox"
        job_or_schedule = "daily"
        path = (
            f"run/v1/external/"
            f"{tenant_resource_key}/{internal_project_id}/"
            f"{deployment}/{job_or_schedule}"
        )

        with aioresponses() as m:
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.post(
                urljoin(client.api_url, path),
                status=200,
                body=b"Running a Meltano project in Meltano Cloud",
            )
            result = CliRunner().invoke(
                cli,
                [
                    "--config-path",
                    str(config.config_path),
                    "run",
                    job_or_schedule,
                    "--deployment",
                    deployment,
                ],
            )
            assert result.exit_code == 0
            assert "Running a Meltano project in Meltano Cloud" in result.output
