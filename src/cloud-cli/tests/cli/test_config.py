"""Test the cloud config command."""

from __future__ import annotations

import hashlib
import re
import typing as t

from click.testing import CliRunner
from pytest_httpserver.httpserver import Response

from meltano.cloud.api.client import HTTPStatus
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
            "Output truncated. To print more items, increase the limit using the "
            "--limit option.\n"
        )


class TestConfigNotificationCommand:
    """Tests the notification command"""

    def test_notification_set(
        self,
        tenant_resource_key: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        webhook_url = "http://test+melty/cheese"
        key_hash = hashlib.sha256(webhook_url.encode("utf-8")).hexdigest()
        path = f"/notifications/v1/{tenant_resource_key}/{key_hash}/notification"
        httpserver.expect_oneshot_request(path).respond_with_response(
            Response(status=HTTPStatus.NO_CONTENT),
        )

        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "config",
                "notification",
                "set",
                "webhook",
                "--value",
                webhook_url,
            ),
        )
        assert result.exit_code == 0, result.output
        assert result.output == "Successfully created webhook notification\n"

    def test_notification_update(
        self,
        tenant_resource_key: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        webhook_url = "http://test+melty/cheese"
        key_hash = hashlib.sha256(webhook_url.encode("utf-8")).hexdigest()
        path = f"/notifications/v1/{tenant_resource_key}/{key_hash}/notification/key"
        httpserver.expect_oneshot_request(path).respond_with_response(
            Response(status=HTTPStatus.NO_CONTENT),
        )

        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "config",
                "notification",
                "update",
                "webhook",
                "--old",
                "http://test+melty/cheese",
                "--new",
                "http://testing",
            ),
        )
        assert result.exit_code == 0, result.output
        assert result.output == "Successfully updated webhook notification\n"

    def test_notification_delete(
        self,
        tenant_resource_key: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        webhook_url = "http://test+melty/cheese"
        key_hash = hashlib.sha256(webhook_url.encode("utf-8")).hexdigest()
        path = f"/notifications/v1/{tenant_resource_key}/{key_hash}/notification"
        httpserver.expect_oneshot_request(path).respond_with_response(
            Response(status=HTTPStatus.NO_CONTENT),
        )

        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "config",
                "notification",
                "delete",
                "webhook",
                "--value",
                webhook_url,
            ),
        )
        assert result.exit_code == 0, result.output
        assert result.output == "Successfully deleted webhook notification\n"
