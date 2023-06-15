"""Test the cloud config command."""

from __future__ import annotations

import re
import typing as t

from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from meltano.cloud.api.config import MeltanoCloudConfig


class TestConfigEnvCommand:
    """Tests the env subcommand."""

    def test_env_list(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        path = f"/secrets/v1/{tenant_resource_key}/{internal_project_id}/"
        pattern = re.compile(f"^{path}(\\?.*)?$")
        httpserver.expect_oneshot_request(pattern).respond_with_json(
            {
                "results": [{"name": "MY_ENV_VAR"}, {"name": "MY_OTHER_ENV_VAR"}],
                "pagination": None,
            },
        )
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "config", "env", "list"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == "MY_ENV_VAR\nMY_OTHER_ENV_VAR\n"

    def test_env_list_limit(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        path = f"/secrets/v1/{tenant_resource_key}/{internal_project_id}/"
        pattern = re.compile(f"^{path}(\\?.*)?$")
        httpserver.expect_oneshot_request(pattern).respond_with_json(
            {
                "results": [{"name": "MY_ENV_VAR"}, {"name": "MY_OTHER_ENV_VAR"}],
                "pagination": None,
            },
        )
        result = CliRunner(mix_stderr=False).invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "config",
                "env",
                "list",
                "--limit",
                "1",
            ),
        )
        assert result.exit_code == 0, result.output
        assert result.stdout == "MY_ENV_VAR\n"
        assert result.stderr == (
            "Output truncated due to reaching the item limit. To print more items, "
            "increase the limit using the --limit flag.\n"
        )
