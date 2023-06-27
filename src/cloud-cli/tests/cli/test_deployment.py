"""Test the deployment command."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import typing as t
from http import HTTPStatus
from pathlib import Path

import pytest
from click.testing import CliRunner
from pytest_httpserver.httpserver import Response

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer
    from requests_mock import Mocker as RequestsMocker

    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudDeployment


class TestDeploymentCommand:
    """Test the logs command."""

    @pytest.fixture()
    def deployments(self) -> list[CloudDeployment]:
        return [
            {
                "git_rev": "Main",
                "git_rev_hash": "0e3a4e17fdbd02b4df7d94035680fc88476a8fa5",
                "deployment_name": "ultra-production",
                "environment_name": "Ultra Production",
                "last_deployed_timestamp": "2023-05-30T16:52:44.725476+00:00",
                "default": False,
            },
            {
                "git_rev": "e219d8183ac288ea9a0de1b3b53da045c6c14570",
                "git_rev_hash": "e219d8183ac288ea9a0de1b3b53da045c6c14570",
                "deployment_name": "temp",
                "environment_name": "Ultra Production",
                "last_deployed_timestamp": "2023-05-30T16:51:52.492991+00:00",
                "default": True,
            },
            {
                "git_rev": "v1.2.0",
                "git_rev_hash": "b678fe12e559ccfdf68de7b0eab97e53346326d1",
                "deployment_name": "legacy",
                "environment_name": "Future",
                "last_deployed_timestamp": "2123-05-30T16:51:52.492991+00:00",
                "default": False,
            },
        ]

    @pytest.fixture()
    def path(self, tenant_resource_key: str, internal_project_id: str) -> str:
        return f"/deployments/v1/{tenant_resource_key}/{internal_project_id}"

    @pytest.fixture()
    def prepared_request(self, request: pytest.FixtureRequest):
        return {
            "method": request.param["method"],
            "url": "https://asdf.lambda-url.us-west-2.on.aws.example.com/",
            "params": {},
            "headers": {
                "Content-Type": "application/json",
                "X-Amz-Date": "20230525T185058Z",
                "X-Amz-Security-Token": "IQoJb3JpZ2luX2VjEOP/////////wEaCXV==",
                "Authorization": "AWS4-HMAC-SHA256 Credential=ASI3AV1SM3BH...",
            },
            "data": '{"environment_name": "staging", "git_rev": "main"}',
        }

    def test_deployment_list_table(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        deployments: list[CloudDeployment],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": deployments, "pagination": None},
        )
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "deployment", "list"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭───────────┬──────────────────┬──────────────────┬──────────────────────────────────────────┬────────────────────┬───────────────────────╮\n"  # noqa: E501
            "│  Default  │ Name             │ Environment      │ Tracked Git Rev                          │ Current Git Hash   │ Last Deployed (UTC)   │\n"  # noqa: E501
            "├───────────┼──────────────────┼──────────────────┼──────────────────────────────────────────┼────────────────────┼───────────────────────┤\n"  # noqa: E501
            "│           │ ultra-production │ Ultra Production │ Main                                     │ 0e3a4e1            │ 2023-05-30 16:52:44   │\n"  # noqa: E501
            "│           │ temp             │ Ultra Production │ e219d8183ac288ea9a0de1b3b53da045c6c14570 │ e219d81            │ 2023-05-30 16:51:52   │\n"  # noqa: E501
            "│           │ legacy           │ Future           │ v1.2.0                                   │ b678fe1            │ 2123-05-30 16:51:52   │\n"  # noqa: E501
            "╰───────────┴──────────────────┴──────────────────┴──────────────────────────────────────────┴────────────────────┴───────────────────────╯\n"  # noqa: E501
        )  # noqa: E501

    def test_deployment_list_table_limit(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        deployments: list[CloudDeployment],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": deployments, "pagination": None},
        )
        result = CliRunner(mix_stderr=False).invoke(
            cli,
            ("--config-path", config.config_path, "deployment", "list", "--limit", "2"),
        )
        assert result.exit_code == 0, result.output
        assert result.stdout == (
            "╭───────────┬──────────────────┬──────────────────┬──────────────────────────────────────────┬────────────────────┬───────────────────────╮\n"  # noqa: E501
            "│  Default  │ Name             │ Environment      │ Tracked Git Rev                          │ Current Git Hash   │ Last Deployed (UTC)   │\n"  # noqa: E501
            "├───────────┼──────────────────┼──────────────────┼──────────────────────────────────────────┼────────────────────┼───────────────────────┤\n"  # noqa: E501
            "│           │ ultra-production │ Ultra Production │ Main                                     │ 0e3a4e1            │ 2023-05-30 16:52:44   │\n"  # noqa: E501
            "│           │ temp             │ Ultra Production │ e219d8183ac288ea9a0de1b3b53da045c6c14570 │ e219d81            │ 2023-05-30 16:51:52   │\n"  # noqa: E501
            "╰───────────┴──────────────────┴──────────────────┴──────────────────────────────────────────┴────────────────────┴───────────────────────╯\n"  # noqa: E501
        )  # noqa: E501
        assert result.stderr == (
            "Output truncated. To print more items, increase the limit using the "
            "--limit option.\n"
        )

    def test_deployment_list_table_with_default_deployment(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        deployments: list[CloudDeployment],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": deployments, "pagination": None},
        )
        config.default_deployment_name = "legacy"
        config.write_to_file()
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "deployment", "list"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭───────────┬──────────────────┬──────────────────┬──────────────────────────────────────────┬────────────────────┬───────────────────────╮\n"  # noqa: E501
            "│  Default  │ Name             │ Environment      │ Tracked Git Rev                          │ Current Git Hash   │ Last Deployed (UTC)   │\n"  # noqa: E501
            "├───────────┼──────────────────┼──────────────────┼──────────────────────────────────────────┼────────────────────┼───────────────────────┤\n"  # noqa: E501
            "│           │ ultra-production │ Ultra Production │ Main                                     │ 0e3a4e1            │ 2023-05-30 16:52:44   │\n"  # noqa: E501
            "│           │ temp             │ Ultra Production │ e219d8183ac288ea9a0de1b3b53da045c6c14570 │ e219d81            │ 2023-05-30 16:51:52   │\n"  # noqa: E501
            "│     X     │ legacy           │ Future           │ v1.2.0                                   │ b678fe1            │ 2123-05-30 16:51:52   │\n"  # noqa: E501
            "╰───────────┴──────────────────┴──────────────────┴──────────────────────────────────────────┴────────────────────┴───────────────────────╯\n"  # noqa: E501
        )  # noqa: E501

    def test_deployment_list_json(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        deployments: list[CloudDeployment],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": deployments, "pagination": None},
        )
        config.default_deployment_name = "temp"
        config.write_to_file()
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "deployment",
                "list",
                "--format=json",
            ),
        )
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == deployments

    def test_deployment_use_by_name(
        self,
        path: str,
        httpserver: HTTPServer,
        config: MeltanoCloudConfig,
        deployments: list[CloudDeployment],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": [deployments[0]], "pagination": None},
        )
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "deployment",
                "use",
                "--name",
                "UlTrA  \tPrOdUcTiOn",
            ),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "Set 'ultra-production' as the default Meltano Cloud deployment "
            "for future commands\n"
        )
        assert (
            json.loads(Path(config.config_path).read_text())["default_deployment_name"]
            == "ultra-production"
        )
        default_org_settings = json.loads(Path(config.config_path).read_text())[
            "organizations_defaults"
        ][config.tenant_resource_key]
        default_project_id = default_org_settings["default_project_id"]
        assert (
            default_org_settings["projects"][default_project_id][
                "default_deployment_name"
            ]
            == "ultra-production"
        )

    @pytest.mark.xfail(
        platform.system() == "Windows",
        reason=(
            "prompt_toolkit fails when in subprocess on Windows: NoConsoleScreenBuffer"
        ),
    )
    def test_deployment_use_by_name_interactive(
        self,
        path: str,
        httpserver: HTTPServer,
        config: MeltanoCloudConfig,
        deployments: list[CloudDeployment],
    ):
        httpserver.expect_oneshot_request(path, "GET").respond_with_json(
            {"results": deployments, "pagination": None},
        )
        result = subprocess.run(
            (
                sys.executable,
                "-m",
                "meltano.cloud.cli",
                "--config-path",
                config.config_path,
                "deployment",
                "use",
            ),
            input="\x1b[B\x1b[B\x0a",  # down, down, enter
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert result.returncode == 0, result.stdout
        assert (
            "Set 'legacy' as the default Meltano Cloud deployment for future commands\n"
        ) in result.stdout
        assert (
            json.loads(Path(config.config_path).read_text())["default_deployment_name"]
            == "legacy"
        )
        default_org_settings = json.loads(Path(config.config_path).read_text())[
            "organizations_defaults"
        ][config.tenant_resource_key]
        default_project_id = default_org_settings["default_project_id"]

        assert (
            default_org_settings["projects"][default_project_id][
                "default_deployment_name"
            ]
            == "legacy"
        )

    @pytest.mark.parametrize("prepared_request", ({"method": "POST"},), indirect=True)
    def test_create_new_deployment(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        deployments: list[CloudDeployment],
        prepared_request,
        requests_mock: RequestsMocker,
    ):
        httpserver.expect_oneshot_request(
            f"{path}/ultra-production",
            "GET",
        ).respond_with_response(Response(status=HTTPStatus.NOT_FOUND))
        httpserver.expect_oneshot_request(
            f"{path}/ultra-production",
            "POST",
        ).respond_with_json(prepared_request)
        requests_mock.post(prepared_request["url"], json=deployments[0])  # noqa: S113
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "deployment",
                "create",
                "--name",
                "ultra-production",
                "--environment",
                "Ultra Production",
                "--git-rev",
                "Main",
            ),
        )
        assert result.exit_code == 0, result.output
        assert "Creating deployment - this may take several minutes..." in result.output
        assert "Created deployment 'ultra-production'\n" in result.output

    @pytest.mark.parametrize("prepared_request", ({"method": "POST"},), indirect=True)
    def test_update_existing_deployment(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        deployments: list[CloudDeployment],
        prepared_request,
        requests_mock: RequestsMocker,
    ):
        httpserver.expect_oneshot_request(
            f"{path}/ultra-production",
            "GET",
        ).respond_with_json(deployments[0])
        httpserver.expect_oneshot_request(
            f"{path}/ultra-production",
            "POST",
        ).respond_with_json(prepared_request)
        requests_mock.post(prepared_request["url"], json=deployments[0])  # noqa: S113
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "deployment",
                "update",
                "--name",
                "ultra-production",
            ),
        )
        assert result.exit_code == 0, result.output
        assert "Updating deployment - this may take several minutes..." in result.output
        assert "Updated deployment 'ultra-production'\n" in result.output

    def test_update_non_existent_deployment(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
    ):
        httpserver.expect_oneshot_request(
            f"{path}/ultra-production",
            "GET",
        ).respond_with_response(Response(status=HTTPStatus.NOT_FOUND))
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "deployment",
                "update",
                "--name",
                "ultra-production",
            ),
        )
        assert result.exit_code == 1, result.output
        assert (
            "Deployment 'ultra-production' does not exist. Use `meltano cloud "
            "deployment create` to create a new Meltano Cloud deployment.\n"
        ) in result.output

    @pytest.mark.parametrize("prepared_request", ({"method": "DELETE"},), indirect=True)
    def test_delete_deployment(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        prepared_request,
        requests_mock: RequestsMocker,
        deployments: list[CloudDeployment],
    ):
        httpserver.expect_oneshot_request(
            f"{path}/ultra-production",
            "GET",
        ).respond_with_json(deployments[0])
        httpserver.expect_oneshot_request(
            f"{path}/ultra-production",
            "DELETE",
        ).respond_with_json(prepared_request)
        requests_mock.delete(  # noqa: S113
            prepared_request["url"],
            status_code=HTTPStatus.NO_CONTENT,
        )
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "deployment",
                "delete",
                "--name",
                "ultra-production",
            ),
        )
        assert result.exit_code == 0, result.output
        assert "Deleting deployment - this may take several minutes..." in result.output
        assert "Deleted deployment 'ultra-production'\n" in result.output

    def test_delete_non_existent_deployment(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
    ):
        httpserver.expect_oneshot_request(
            f"{path}/fake",
            "GET",
        ).respond_with_response(Response(status=HTTPStatus.NOT_FOUND))
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "deployment",
                "delete",
                "--name",
                "fake",
            ),
        )
        assert result.exit_code == 1, result.output
        assert "Deployment 'fake' does not exist.\n" in result.output
