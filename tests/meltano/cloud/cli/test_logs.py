"""Test the logs command."""

from __future__ import annotations

import typing as t

from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from meltano.cloud.api.config import MeltanoCloudConfig


class TestLogsCommand:
    """Test the logs command."""

    def test_logs_print(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        """Test the `logs print` subcommand."""
        execution_id = "12345"
        path = (
            f"/logs/v1/{tenant_resource_key}/{internal_project_id}/tail/{execution_id}"
        )
        httpserver.expect_oneshot_request(path).respond_with_json(
            {
                "results": [
                    {
                        "timestamp": 1620000000,
                        "ingestion_time": 1620000000,
                        "message": "[2023-05-01 00:00:00] Starting Job...",
                    },
                    {
                        "timestamp": 1620000000,
                        "ingestion_time": 1620000000,
                        "message": "[2023-05-01 00:00:01] Running Job...",
                    },
                ],
                "pagination": {
                    "next_page_token": "abc123",
                    "page_size": 2,
                },
            },
        )
        httpserver.expect_oneshot_request(
            path,
            query_string={"page_token": "abc123"},
        ).respond_with_json(
            {
                "results": [
                    {
                        "timestamp": 1620000000,
                        "ingestion_time": 1620000000,
                        "message": "[2023-05-01 00:00:02] Finishing Job...",
                    },
                ],
                "pagination": {
                    "next_page_token": "def123",
                    "page_size": 2,
                },
            },
        )
        httpserver.expect_oneshot_request(
            path,
            query_string={"page_token": "def123"},
        ).respond_with_json(
            {
                "results": [],
                "pagination": {
                    "next_page_token": "def123",
                    "page_size": 2,
                },
            },
        )

        result = CliRunner().invoke(
            cli,
            [
                "--config-path",
                str(config.config_path),
                "logs",
                "print",
                "--execution-id",
                execution_id,
            ],
        )
        assert result.exit_code == 0
        assert "[2023-05-01 00:00:00] Starting Job..." in result.output
        assert "[2023-05-01 00:00:01] Running Job..." in result.output
        assert "[2023-05-01 00:00:02] Finishing Job..." in result.output
