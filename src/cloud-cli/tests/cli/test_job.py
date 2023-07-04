"""Test the schedule command."""

from __future__ import annotations

import typing as t

import pytest
from click.testing import CliRunner

from meltano.cloud.api import MeltanoCloudError
from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from meltano.cloud.api.config import MeltanoCloudConfig


class TestJobStopCommand:
    """Test the `stop` command."""

    @pytest.fixture()
    def path(self, tenant_resource_key: str, internal_project_id: str) -> str:
        return f"/jobs/v1/{tenant_resource_key}/{internal_project_id}"

    @pytest.fixture()
    def response_body(self) -> dict:
        return {
            "results": [
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
                {
                    "execution_id": "456",
                    "start_time": "2023-09-01T00:00:00+00:00",
                    "end_time": None,
                    "status": "STOPPED",
                    "exit_code": 1,
                    "environment_name": "dev",
                    "schedule_name": "daily",
                    "job_name": "N/A",
                },
            ],
            "pagination": None,
        }

    def test_stop(
        self,
        path: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        execution_id = "123"
        reason = "User requested stop"

        httpserver.expect_oneshot_request(
            f"{path}/{execution_id}",
            method="DELETE",
        ).respond_with_json(
            {
                "execution_id": execution_id,
                "reason": reason,
            },
        )
        result = CliRunner(mix_stderr=False).invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "job",
                "stop",
                "--execution-id",
                execution_id,
            ),
        )
        assert result.exit_code == 0
        assert result.stderr == f"Stopping execution {execution_id}...\n"

    def test_already_stopped(
        self,
        path: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        execution_id = "123"
        message = "Execution is already stopped"

        httpserver.expect_oneshot_request(
            f"{path}/{execution_id}",
            method="DELETE",
        ).respond_with_json(
            {
                "detail": message,
                "status": "STOPPED",
            },
            status=400,
        )
        result = CliRunner(mix_stderr=False).invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "job",
                "stop",
                "--execution-id",
                execution_id,
            ),
        )
        assert result.exit_code == 0
        assert result.stderr == f"{message}\n"

    def test_not_found(
        self,
        path: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        execution_id = "123"

        httpserver.expect_oneshot_request(
            f"{path}/{execution_id}",
            method="DELETE",
        ).respond_with_json({}, status=404)
        result = CliRunner(mix_stderr=False).invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "job",
                "stop",
                "--execution-id",
                execution_id,
            ),
        )
        assert result.exit_code == 1
        assert isinstance(result.exception, MeltanoCloudError)
        assert result.exception.response.status == 404
