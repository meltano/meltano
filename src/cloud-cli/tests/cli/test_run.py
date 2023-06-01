"""Test the run command."""

from __future__ import annotations

import typing as t

from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from meltano.cloud.api.config import MeltanoCloudConfig


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

    def test_run_ok_with_default_deployment(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        deployment = "default-sandbox"
        job_or_schedule = "daily"
        path = (
            f"/run/v1/external/"
            f"{tenant_resource_key}/{internal_project_id}/"
            f"{deployment}/{job_or_schedule}"
        )
        config.default_deployment_name = deployment
        config.write_to_file()
        httpserver.expect_oneshot_request(path).respond_with_data(
            b"Running a Meltano project in Meltano Cloud",
        )
        result = CliRunner().invoke(
            cli,
            ["--config-path", config.config_path, "run", job_or_schedule],
        )
        assert result.exit_code == 0
        assert "Running a Meltano project in Meltano Cloud" in result.output

    def test_run_fails_when_missing_deployment(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        deployment = "default-sandbox"
        job_or_schedule = "daily"
        path = (
            f"/run/v1/external/"
            f"{tenant_resource_key}/{internal_project_id}/"
            f"{deployment}/{job_or_schedule}"
        )
        config.default_deployment_name = None
        config.write_to_file()
        httpserver.expect_oneshot_request(path).respond_with_data(
            b"Running a Meltano project in Meltano Cloud",
        )
        result = CliRunner().invoke(
            cli,
            ["--config-path", config.config_path, "run", job_or_schedule],
        )
        assert result.exit_code == 2
        assert "A deployment name is required." in result.output
