"""Test the project command."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import typing as t
from pathlib import Path

import pytest
from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli
from meltano.cloud.cli.project import _remove_private_project_attributes  # noqa: WPS450

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudProject


class TestProjectCommand:
    """Test the logs command."""

    @pytest.fixture()
    def projects(self, tenant_resource_key: str) -> list[CloudProject]:
        return [
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQ7520WNMQT0PQ6KHCC4EE1",
                "project_name": "Meltano Cubed",
                "git_repository": "https://github.com/meltano/cubed.git",
                "project_root_path": "information",
                "default": False,
            },
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQ76M7EN1GKYGKV8P6BFKNV",
                "project_name": "Post-Modern Data Stack in a Box",
                "git_repository": "https://github.com/meltano/pmds-in-a-box.git",
                "project_root_path": ".",
                "default": False,
            },
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQW9WSW06F47Q0KVM1BV914",
                "project_name": "Post-Modern Data Stack in a Box",
                "git_repository": "https://github.com/meltano/pmds-in-a-box-2.git",
                "project_root_path": ".",
                "default": False,
            },
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQ788M7TVP9HFVRGQ34BG17",
                "project_name": "Stranger in a Strange Org",
                "git_repository": "https://github.com/onatlem/grok.git",
                "project_root_path": ".",
                "default": False,
            },
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQREZ7G0526JZS9JY5H3BH9",
                "project_name": "01GWQRDA1HZNTSW7JK0KNGCYS9",
                "git_repository": "Really? A ULID for your project name?",
                "project_root_path": ".",
                "default": False,
            },
        ]

    @pytest.fixture()
    def path(self, tenant_resource_key: str) -> str:
        return f"/projects/v1/{tenant_resource_key}"

    def test_project_list_table(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        projects: list[CloudProject],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": projects, "pagination": None},
        )
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "project", "list"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭───────────┬─────────────────────────────────┬────────────────────────────────────────────────╮\n"  # noqa: E501
            "│  Default  │ Name                            │ Git Repository                                 │\n"  # noqa: E501
            "├───────────┼─────────────────────────────────┼────────────────────────────────────────────────┤\n"  # noqa: E501
            "│           │ Meltano Cubed                   │ https://github.com/meltano/cubed.git           │\n"  # noqa: E501
            "│           │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box.git   │\n"  # noqa: E501
            "│           │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box-2.git │\n"  # noqa: E501
            "│           │ Stranger in a Strange Org       │ https://github.com/onatlem/grok.git            │\n"  # noqa: E501
            "│           │ 01GWQRDA1HZNTSW7JK0KNGCYS9      │ Really? A ULID for your project name?          │\n"  # noqa: E501
            "╰───────────┴─────────────────────────────────┴────────────────────────────────────────────────╯\n"  # noqa: E501
        )  # noqa: E501

    def test_project_list_table_limit(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        projects: list[CloudProject],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": projects, "pagination": None},
        )
        result = CliRunner(mix_stderr=False).invoke(
            cli,
            ("--config-path", config.config_path, "project", "list", "--limit", "4"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭───────────┬─────────────────────────────────┬────────────────────────────────────────────────╮\n"  # noqa: E501
            "│  Default  │ Name                            │ Git Repository                                 │\n"  # noqa: E501
            "├───────────┼─────────────────────────────────┼────────────────────────────────────────────────┤\n"  # noqa: E501
            "│           │ Meltano Cubed                   │ https://github.com/meltano/cubed.git           │\n"  # noqa: E501
            "│           │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box.git   │\n"  # noqa: E501
            "│           │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box-2.git │\n"  # noqa: E501
            "│           │ Stranger in a Strange Org       │ https://github.com/onatlem/grok.git            │\n"  # noqa: E501
            "╰───────────┴─────────────────────────────────┴────────────────────────────────────────────────╯\n"  # noqa: E501
        )  # noqa: E501
        assert result.stderr == (
            "Output truncated. To print more items, increase the limit using the "
            "--limit option.\n"
        )

    def test_project_list_table_with_default_project(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        projects: list[CloudProject],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": projects, "pagination": None},
        )
        config.internal_project_id = "01GWQ76M7EN1GKYGKV8P6BFKNV"  # Set default project
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "project", "list"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭───────────┬─────────────────────────────────┬────────────────────────────────────────────────╮\n"  # noqa: E501
            "│  Default  │ Name                            │ Git Repository                                 │\n"  # noqa: E501
            "├───────────┼─────────────────────────────────┼────────────────────────────────────────────────┤\n"  # noqa: E501
            "│           │ Meltano Cubed                   │ https://github.com/meltano/cubed.git           │\n"  # noqa: E501
            "│     X     │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box.git   │\n"  # noqa: E501
            "│           │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box-2.git │\n"  # noqa: E501
            "│           │ Stranger in a Strange Org       │ https://github.com/onatlem/grok.git            │\n"  # noqa: E501
            "│           │ 01GWQRDA1HZNTSW7JK0KNGCYS9      │ Really? A ULID for your project name?          │\n"  # noqa: E501
            "╰───────────┴─────────────────────────────────┴────────────────────────────────────────────────╯\n"  # noqa: E501
        )  # noqa: E501

    def test_project_list_json(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        projects: list[CloudProject],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": projects, "pagination": None},
        )
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "project",
                "list",
                "--format=json",
            ),
        )
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == [
            _remove_private_project_attributes(x) for x in projects
        ]

    def test_project_use_by_name(
        self,
        path: str,
        httpserver: HTTPServer,
        config: MeltanoCloudConfig,
        projects: list[CloudProject],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": [projects[0]], "pagination": None},
        )
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "project",
                "use",
                "--name",
                "Meltano Cubed",
            ),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "Set 'Meltano Cubed' as the default Meltano Cloud project for "
            "future commands\n"
        )
        assert (
            json.loads(Path(config.config_path).read_text())["organizations_defaults"][
                config.tenant_resource_key
            ]["default_project_id"]
            == "01GWQ7520WNMQT0PQ6KHCC4EE1"
        )

    @pytest.mark.xfail(
        platform.system() == "Windows",
        reason=(
            "prompt_toolkit fails when in subprocess on Windows: NoConsoleScreenBuffer"
        ),
    )
    def test_project_use_by_name_interactive(
        self,
        path: str,
        httpserver: HTTPServer,
        config: MeltanoCloudConfig,
        projects: list[CloudProject],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": [*projects[:2], *projects[3:]], "pagination": None},
        )
        result = subprocess.run(
            (
                sys.executable,
                "-m",
                "meltano.cloud.cli",
                "--config-path",
                config.config_path,
                "project",
                "use",
            ),
            input="\x1b[B\x1b[B\x0a",  # down, down, enter
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert result.returncode == 0, result.stdout
        assert (
            "Set 'Stranger in a Strange Org' as the default Meltano Cloud "
            "project for future commands\n"
        ) in result.stdout
        assert (
            json.loads(Path(config.config_path).read_text())["organizations_defaults"][
                config.tenant_resource_key
            ]["default_project_id"]
            == "01GWQ788M7TVP9HFVRGQ34BG17"
        )

    def test_project_use_by_name_interactive_duplicate_name(
        self,
        config: MeltanoCloudConfig,
        path: str,
        httpserver: HTTPServer,
        projects: list[CloudProject],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": projects, "pagination": None},
        )
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "project",
                "use",
            ),
        )
        assert result.exit_code == 1
        assert (
            "Error: Multiple Meltano Cloud projects have the same name."
            in result.output
        )

    def test_project_use_by_name_like_id(
        self,
        path: str,
        httpserver: HTTPServer,
        config: MeltanoCloudConfig,
        projects: list[CloudProject],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": [*projects[:2], *projects[3:]], "pagination": None},
        )
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "project",
                "use",
                "--name",
                "01GWQRDA1HZNTSW7JK0KNGCYS9",
            ),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "Set '01GWQRDA1HZNTSW7JK0KNGCYS9' as the default Meltano Cloud "
            "project for future commands\n"
        )
        assert (
            json.loads(Path(config.config_path).read_text())["organizations_defaults"][
                config.tenant_resource_key
            ]["default_project_id"]
            == "01GWQREZ7G0526JZS9JY5H3BH9"
        )

    def test_project_use_by_id(self, config: MeltanoCloudConfig):
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "project",
                "use",
                "--id",
                "01GWQ7520WNMQT0PQ6KHCC4EE1",
            ),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "Set the project with ID '01GWQ7520WNMQT0PQ6KHCC4EE1' as the "
            "default Meltano Cloud project for future commands\n"
        )
        assert (
            json.loads(Path(config.config_path).read_text())["organizations_defaults"][
                config.tenant_resource_key
            ]["default_project_id"]
            == "01GWQ7520WNMQT0PQ6KHCC4EE1"
        )

    def test_project_use_ambigous_name_error(
        self,
        path: str,
        httpserver: HTTPServer,
        config: MeltanoCloudConfig,
        projects: list[CloudProject],
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(
            {"results": projects[1:3], "pagination": None},
        )
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "project",
                "use",
                "--name",
                "Post-Modern Data Stack in a Box",
            ),
        )
        assert result.exit_code == 1
        assert result.output == (
            "Error: Multiple Meltano Cloud projects have the same name. "
            "Please specify the project using the `--id` option with its "
            "internal ID, shown below. Note that these IDs may change at any "
            "time. To avoid this issue, please use unique project names.\n"
            "01GWQ76M7EN1GKYGKV8P6BFKNV: Post-Modern Data Stack in a Box "
            "('https://github.com/meltano/pmds-in-a-box.git')\n"
            "01GWQW9WSW06F47Q0KVM1BV914: Post-Modern Data Stack in a Box "
            "('https://github.com/meltano/pmds-in-a-box-2.git')\n"
        )

    def test_project_use_by_name_and_id_error(self, config: MeltanoCloudConfig):
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "project",
                "use",
                "--name",
                "a name",
                "--id",
                "and an ID",
            ),
        )
        assert result.exit_code == 2
        assert "The '--name' and '--id' options are mutually exclusive" in result.output

    def test_project_add(
        self,
        projects: list[CloudProject],
        httpserver: HTTPServer,
        config: MeltanoCloudConfig,
    ):
        for project in projects[:3]:
            httpserver.expect_oneshot_request(
                f"/projects/v1/{project['tenant_resource_key']}",
                method="POST",
            ).respond_with_json(project)
            result = CliRunner().invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "project",
                    "add",
                    "--project-name",
                    project["project_name"],
                    "--git-repository",
                    project["git_repository"],
                    "--project-root-path",
                    project["project_root_path"],
                ),
            )
            assert result.exit_code == 0, result.output
            assert result.output == (
                f"Project {project['project_name']} created successfully.\n"
                + json.dumps(project)
                + "\n"
            )
