"""Test the logs command."""

from __future__ import annotations

import json
import typing as t
from urllib.parse import urljoin

from aioresponses import aioresponses
from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from meltano.cloud.api import MeltanoCloudClient
    from meltano.cloud.api.config import MeltanoCloudConfig


class TestLogsCommand:
    """Test the logs command."""

    def test_logs_print(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        client: MeltanoCloudClient,
        config: MeltanoCloudConfig,
    ):
        """Test the `logs print` subcommand."""
        execution_id = "12345"
        path = f"logs/v1/{tenant_resource_key}/{internal_project_id}/{execution_id}"

        with aioresponses() as m:
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.get(
                urljoin(client.api_url, path),
                status=200,
                body=b"[2023-05-01 00:00:00] Starting Job...",
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
