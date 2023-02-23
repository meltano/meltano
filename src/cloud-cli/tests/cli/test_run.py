from __future__ import annotations

import pytest
from aioresponses import aioresponses
from click.testing import CliRunner

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.cli import cloud as cli


class TestCloudRun:
    """Test the Meltano Cloud run command."""

    def test_run_ok(self, monkeypatch: pytest.MonkeyPatch):
        tenant_resource_key = "meltano-cloud-test"
        project_id = "pytest-123"
        environment = "dev"
        job_or_schedule = "gh-to-snowflake"

        monkeypatch.setenv("MELTANO_CLOUD_RUNNER_API_KEY", "keepitsecret")
        monkeypatch.setenv("MELTANO_CLOUD_RUNNER_SECRET", "keepitsafe")
        monkeypatch.setenv("MELTANO_CLOUD_ORGANIZATION_ID", tenant_resource_key)

        path = MeltanoCloudClient.construct_runner_path(
            tenant_resource_key=tenant_resource_key,
            project_id=project_id,
            environment=environment,
            job_or_schedule=job_or_schedule,
        )

        with aioresponses() as m:
            m.post(
                f"{MeltanoCloudClient.CLOUD_RUNNERS_URL}{path}",
                status=200,
                body=b"Running Job",
            )
            result = CliRunner().invoke(
                cli,
                [
                    "run",
                    job_or_schedule,
                    "--project-id",
                    project_id,
                    "--environment",
                    environment,
                ],
            )

            assert result.exit_code == 0
            assert "Running Job" in result.output

    def test_run_missing_env_var(self, monkeypatch: pytest.MonkeyPatch):
        project_id = "pytest-123"
        environment = "dev"
        job_or_schedule = "gh-to-snowflake"

        monkeypatch.setenv("MELTANO_CLOUD_RUNNER_API_KEY", "keepitsecret")
        monkeypatch.setenv("MELTANO_CLOUD_RUNNER_SECRET", "keepitsafe")
        monkeypatch.delenv("MELTANO_CLOUD_ORGANIZATION_ID", raising=False)

        result = CliRunner().invoke(
            cli,
            [
                "run",
                job_or_schedule,
                "--project-id",
                project_id,
                "--environment",
                environment,
            ],
        )

        assert result.exit_code == 2
        assert (
            "Environment variable MELTANO_CLOUD_ORGANIZATION_ID is not set"
            in result.output
        )

    def test_run_unauthorized(self, monkeypatch: pytest.MonkeyPatch):
        tenant_resource_key = "meltano-cloud-test"
        project_id = "pytest-123"
        environment = "dev"
        job_or_schedule = "gh-to-snowflake"

        monkeypatch.setenv("MELTANO_CLOUD_RUNNER_API_KEY", "keepitsecret")
        monkeypatch.setenv("MELTANO_CLOUD_RUNNER_SECRET", "keepitsafe")
        monkeypatch.setenv("MELTANO_CLOUD_ORGANIZATION_ID", tenant_resource_key)

        path = MeltanoCloudClient.construct_runner_path(
            tenant_resource_key=tenant_resource_key,
            project_id=project_id,
            environment=environment,
            job_or_schedule=job_or_schedule,
        )

        with aioresponses() as m:
            m.post(
                f"{MeltanoCloudClient.CLOUD_RUNNERS_URL}{path}",
                status=401,
                reason="Unauthorized",
            )
            result = CliRunner().invoke(
                cli,
                [
                    "run",
                    job_or_schedule,
                    "--project-id",
                    project_id,
                    "--environment",
                    environment,
                ],
            )

            assert result.exit_code == 1
            assert result.exception is not None
            assert isinstance(result.exception, MeltanoCloudError)
            assert result.exception.response.reason == "Unauthorized"
