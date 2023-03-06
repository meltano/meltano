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
        "environment": "dev",
        "job_or_schedule": "gh-to-snowflake",
    }

    RUNNER_CREDS = {
        "api_key": "keepitsecret",
        "runner_secret": "keepitsafe",
    }

    @pytest.fixture(scope="function")
    def config(self, tmp_path: Path):
        return MeltanoCloudConfig.find(config_path=tmp_path / "meltano-cloud.json")

    async def test_run_ok(self, config: MeltanoCloudConfig):
        """Test that a successful run returns the expected result."""
        async with MeltanoCloudClient(config=config) as client:
            client.api_key = self.RUNNER_CREDS["api_key"]
            client.runner_secret = self.RUNNER_CREDS["runner_secret"]
            path = client.construct_runner_path(**self.RUNNER_ARGS)
            with aioresponses() as m:
                logging.debug(
                    f"Mocking 200 response for {urljoin(client.runner_api_url, path)}"
                )

                m.post(
                    urljoin(client.runner_api_url, path),
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
            client.api_key = self.RUNNER_CREDS["api_key"]
            client.runner_secret = self.RUNNER_CREDS["runner_secret"]
            path = client.construct_runner_path(**self.RUNNER_ARGS)
            with aioresponses() as m:
                m.post(
                    urljoin(client.runner_api_url, path),
                    status=403,
                    payload={"status": "error"},
                    reason="Forbidden",
                )
                with pytest.raises(MeltanoCloudError):
                    await client.run_project(**self.RUNNER_ARGS)
