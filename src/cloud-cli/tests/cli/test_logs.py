"""Test the logs command."""

from __future__ import annotations

import typing as t

from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from tests.conftest import HTTPServer


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
        path = f"/logs/v1/{tenant_resource_key}/{internal_project_id}/{execution_id}"
        httpserver.expect_oneshot_request(path).respond_with_data(
            b"[2023-05-01 00:00:00] Starting Job...",
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
