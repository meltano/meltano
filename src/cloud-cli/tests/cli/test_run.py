from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

import pytest
from aioresponses import aioresponses
from click.testing import CliRunner

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.api.config import MeltanoCloudConfig
from meltano.cloud.cli import cloud as cli


class TestCloudRun:
    """Test the Meltano Cloud run command."""

    @pytest.fixture
    def client(self):
        return MeltanoCloudClient()

    @pytest.fixture
    def config(self, tmp_path: Path):
        path = tmp_path / "meltano-cloud.json"
        path.touch()
        return MeltanoCloudConfig(config_path=path)

    def test_run_ok(
        self,
        monkeypatch: pytest.MonkeyPatch,
        client: MeltanoCloudClient,
        config: MeltanoCloudConfig,
    ):
        tenant_resource_key = "meltano-cloud-test"
        project_id = "pytest-123"
        deployment = "dev"
        job_or_schedule = "gh-to-snowflake"

        monkeypatch.setenv("MELTANO_CLOUD_ORGANIZATION_ID", tenant_resource_key)

        path = client.construct_runner_path(
            tenant_resource_key=tenant_resource_key,
            project_id=project_id,
            deployment=deployment,
            job_or_schedule=job_or_schedule,
        )

        with aioresponses() as m:
            m.post(
                urljoin(client.api_url, path),
                status=200,
                body=b"Running Job",
            )

            result = CliRunner().invoke(
                cli,
                [
                    "--config-path",
                    str(config.config_path),
                    "run",
                    job_or_schedule,
                    "--project-id",
                    project_id,
                    "--deployment",
                    deployment,
                ],
            )
            assert result.exit_code == 0
            assert "Running Job" in result.output

    def test_run_unauthorized(
        self,
        monkeypatch: pytest.MonkeyPatch,
        client: MeltanoCloudClient,
        config: MeltanoCloudConfig,
    ):
        tenant_resource_key = "meltano-cloud-test"
        project_id = "pytest-123"
        deployment = "dev"
        job_or_schedule = "gh-to-snowflake"

        monkeypatch.setenv("MELTANO_CLOUD_ORGANIZATION_ID", tenant_resource_key)

        path = client.construct_runner_path(
            tenant_resource_key=tenant_resource_key,
            project_id=project_id,
            deployment=deployment,
            job_or_schedule=job_or_schedule,
        )

        with aioresponses() as m:
            m.post(
                urljoin(client.api_url, path),
                status=401,
                reason="Unauthorized",
            )
            result = CliRunner().invoke(
                cli,
                (
                    "--config-path",
                    str(config.config_path),
                    "run",
                    job_or_schedule,
                    "--project-id",
                    project_id,
                    "--deployment",
                    deployment,
                ),
            )

            assert result.exit_code == 1
            assert result.exception is not None
            assert isinstance(result.exception, MeltanoCloudError)
            assert result.exception.response.reason == "Unauthorized"
