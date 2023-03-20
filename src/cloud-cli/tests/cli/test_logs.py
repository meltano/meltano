"""Test the logs command."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urljoin

import jwt
import pytest
from aioresponses import aioresponses
from click.testing import CliRunner

from meltano.cloud.api import MeltanoCloudClient
from meltano.cloud.api.config import MeltanoCloudConfig
from meltano.cloud.cli import cloud as cli


class TestLogsCommand:
    """Test the logs command."""

    @pytest.fixture
    def tenant_resource_key(self):
        return "meltano-cloud-test"

    @pytest.fixture
    def internal_project_id(self):
        return "pytest-123"

    @pytest.fixture
    def id_token(self, tenant_resource_key: str, internal_project_id: str):
        return jwt.encode(
            {
                "sub": "meltano-cloud-test",
                "custom:trk_and_pid": f"{tenant_resource_key}::{internal_project_id}",
            },
            key="",
        )

    @pytest.fixture
    def config(self, config_path: Path, id_token: str):
        config = MeltanoCloudConfig(  # noqa: S106
            config_path=config_path,
            base_auth_url="http://auth-test.meltano.cloud",
            base_url="https://internal.api-test.meltano.cloud/",
            app_client_id="meltano-cloud-test",
            access_token="meltano-cloud-test",  # noqa: S106
            id_token=id_token,
        )
        config.write_to_file()
        return config

    @pytest.fixture
    def client(self, config: MeltanoCloudConfig):
        return MeltanoCloudClient(config=config)

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
