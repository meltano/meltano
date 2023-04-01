"""Test the run command."""

from __future__ import annotations

import typing as t

from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from tests.conftest import HTTPServer


class TestCloudRun:
    """Test the Meltano Cloud run command."""

    def test_run_ok(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        """Test the `run` subcommand."""
        deployment = "sandbox"
        job_or_schedule = "daily"
        path = (
            f"/run/v1/external/"
            f"{tenant_resource_key}/{internal_project_id}/"
            f"{deployment}/{job_or_schedule}"
        )
        httpserver.expect_oneshot_request(path).respond_with_data(
            b"Running a Meltano project in Meltano Cloud",
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
