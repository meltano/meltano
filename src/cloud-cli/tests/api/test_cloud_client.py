"""Test the Meltano Cloud API client."""

from __future__ import annotations

import pytest
from aioresponses import aioresponses

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError


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

    async def test_run_ok(self):
        """Test that a successful run returns the expected result."""
        async with MeltanoCloudClient() as client:
            path = client.construct_runner_path(**self.RUNNER_ARGS)
            with aioresponses() as m:
                m.post(
                    f"{client.CLOUD_RUNNERS_URL}{path}",
                    status=200,
                    body="Running Job",
                    repeat=True,
                )
                assert not client.session.closed
                result = await client.run_project(
                    **self.RUNNER_ARGS,
                    **self.RUNNER_CREDS,
                )
                assert result == "Running Job"

    async def test_run_error(self):
        """Test that a response error is raised as a MeltanoCloudError."""
        async with MeltanoCloudClient() as client:
            path = client.construct_runner_path(**self.RUNNER_ARGS)
            with aioresponses() as m:
                m.post(
                    f"{client.CLOUD_RUNNERS_URL}{path}",
                    status=403,
                    payload={"status": "error"},
                    reason="Forbidden",
                )
                with pytest.raises(MeltanoCloudError):
                    await client.run_project(**self.RUNNER_ARGS, **self.RUNNER_CREDS)
