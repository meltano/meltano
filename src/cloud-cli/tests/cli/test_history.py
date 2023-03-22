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
from meltano.cloud.cli.history import process_table_row

if t.TYPE_CHECKING:
    from meltano.cloud.api import MeltanoCloudClient
    from meltano.cloud.api.config import MeltanoCloudConfig


@pytest.mark.parametrize(
    "execution, expected",
    [
        pytest.param(
            {
                "execution_id": "123",
                "start_time": "2023-09-02T00:00:00+00:00",
                "end_time": "2023-09-02T00:10:00+00:00",
                "status": "STOPPED",
                "exit_code": 0,
                "environment_name": "dev",
                "schedule_name": "daily",
                "job_name": "N/A",
            },
            (
                "123",
                "daily",
                "2023-09-02T00:00:00+00:00",
                "Success",
                "00:10:00",
            ),
            id="stopped",
        ),
        pytest.param(
            {
                "execution_id": "123",
                "start_time": "2023-09-02T00:00:00+00:00",
                "end_time": None,
                "status": "RUNNING",
                "exit_code": None,
                "environment_name": "dev",
                "schedule_name": "daily",
                "job_name": "N/A",
            },
            (
                "123",
                "daily",
                "2023-09-02T00:00:00+00:00",
                "Running",
                "N/A",
            ),
            id="running",
        ),
    ],
)
def test_table_rows(execution: dict, expected: tuple):
    assert process_table_row(execution) == expected


class TestHistoryCommand:
    """Test the history command."""

    def test_history_json(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        client: MeltanoCloudClient,
        config: MeltanoCloudConfig,
    ):
        path = f"history/v1/{tenant_resource_key}/{internal_project_id}"
        url = urljoin(client.api_url, path)
        pattern = re.compile(f"^{url}(\\?.*)?$")
        runner = CliRunner()

        with aioresponses() as m:
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.get(
                pattern,
                status=200,
                payload={
                    "results": [
                        {
                            "execution_id": "123",
                            "start_time": "2023-09-02T00:00:00Z",
                            "end_time": "2023-09-02T00:10:00Z",
                            "status": "STOPPED",
                            "exit_code": 0,
                            "environment_name": "dev",
                            "schedule_name": "daily",
                            "job_name": "N/A",
                        },
                        {
                            "execution_id": "456",
                            "start_time": "2023-09-01T00:00:00Z",
                            "end_time": None,
                            "status": "STOPPED",
                            "exit_code": 1,
                            "environment_name": "dev",
                            "schedule_name": "daily",
                            "job_name": "N/A",
                        },
                    ],
                    "pagination": None,
                },
            )
            result = runner.invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "history",
                    "--format=json",
                ),
            )
            assert result.exit_code == 0

            data = json.loads(result.output)
            assert len(data) == 2
