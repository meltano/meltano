"""Test the Meltano Cloud API client."""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urljoin

import pytest
from aioresponses import aioresponses

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.api.config import MeltanoCloudConfig


class TestMeltanoCloudClient:
    """Test the Meltano Cloud API client."""

    RUNNER_ARGS = {
        "tenant_resource_key": "meltano-cloud-test",
        "project_id": "pytest-123",
        "deployment": "dev",
        "job_or_schedule": "gh-to-snowflake",
    }

    @pytest.fixture(scope="function")
    def config(self, tmp_path: Path):
        path = tmp_path / "meltano-cloud.json"
        path.touch()
        return MeltanoCloudConfig.find(config_path=path)

    async def test_run_ok(self, config: MeltanoCloudConfig):
        """Test that a successful run returns the expected result."""
        async with MeltanoCloudClient(config=config) as client:
            path = client.construct_runner_path(**self.RUNNER_ARGS)
            with aioresponses() as m:
                logging.debug(
                    f"Mocking 200 response for {urljoin(client.api_url, path)}"
                )

                m.post(
                    urljoin(client.api_url, path),
                    status=200,
                    body="Running Job",
                    repeat=True,
                )
                assert not client.session.closed
                result = await client.run_project(
                    **self.RUNNER_ARGS,
                )
                assert result == "Running Job"

    async def test_run_error(self, config: MeltanoCloudConfig):
        """Test that a response error is raised as a MeltanoCloudError."""
        async with MeltanoCloudClient(config=config) as client:
            path = client.construct_runner_path(**self.RUNNER_ARGS)
            with aioresponses() as m:
                m.post(
                    urljoin(client.api_url, path),
                    status=403,
                    payload={"status": "error"},
                    reason="Forbidden",
                )
                with pytest.raises(MeltanoCloudError):
                    await client.run_project(**self.RUNNER_ARGS)
