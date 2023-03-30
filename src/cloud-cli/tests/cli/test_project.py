"""Test the project command."""

from __future__ import annotations

import json
import re
import typing as t
from pathlib import Path
from urllib.parse import urljoin

import pytest
from aioresponses import aioresponses
from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli
from meltano.cloud.cli.project import _remove_private_project_attributes  # noqa: WPS450

if t.TYPE_CHECKING:
    from meltano.cloud.api import MeltanoCloudClient
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudProject


class TestProjectCommand:
    """Test the logs command."""

    @pytest.fixture
    def url_pattern(
        self,
        tenant_resource_key: str,
        client: MeltanoCloudClient,
    ) -> re.Pattern:
        path = f"projects/v1/{tenant_resource_key}"
        return re.compile(f"^{urljoin(client.api_url, path)}(\\?.*)?$")

    @pytest.fixture
    def projects(self, tenant_resource_key: str) -> list[CloudProject]:
        return [
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQ7520WNMQT0PQ6KHCC4EE1",
                "project_name": "Meltano Cubed",
                "git_repository": "https://github.com/meltano/cubed.git",
                "project_root_path": "information",
                "active": False,
            },
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQ76M7EN1GKYGKV8P6BFKNV",
                "project_name": "Post-Modern Data Stack in a Box",
                "git_repository": "https://github.com/meltano/pmds-in-a-box.git",
                "project_root_path": ".",
                "active": False,
            },
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQW9WSW06F47Q0KVM1BV914",
                "project_name": "Post-Modern Data Stack in a Box",
                "git_repository": "https://github.com/meltano/pmds-in-a-box-2.git",
                "project_root_path": ".",
                "active": False,
            },
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQ788M7TVP9HFVRGQ34BG17",
                "project_name": "Stranger in a Strange Org",
                "git_repository": "https://github.com/onatlem/grok.git",
                "project_root_path": ".",
                "active": False,
            },
            {
                "tenant_resource_key": tenant_resource_key,
                "project_id": "01GWQREZ7G0526JZS9JY5H3BH9",
                "project_name": "01GWQRDA1HZNTSW7JK0KNGCYS9",
                "git_repository": "Really? A ULID for your project name?",
                "project_root_path": ".",
                "active": False,
            },
        ]

    @pytest.fixture
    def projects_get_reponse(
        self,
        url_pattern: re.Pattern,
        projects: list[CloudProject],
        config: MeltanoCloudConfig,
    ) -> None:
        with aioresponses() as m:
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.get(
                url_pattern,
                status=200,
                payload={"results": projects, "pagination": None},
            )
            yield

    @pytest.mark.usefixtures("projects_get_reponse")
    def test_project_list_table(self, config: MeltanoCloudConfig):
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "project", "list"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭──────────┬─────────────────────────────────┬────────────────────────────────────────────────╮\n"  # noqa: E501
            "│  Active  │ Name                            │ Git Repository                                 │\n"  # noqa: E501
            "├──────────┼─────────────────────────────────┼────────────────────────────────────────────────┤\n"  # noqa: E501
            "│          │ Meltano Cubed                   │ https://github.com/meltano/cubed.git           │\n"  # noqa: E501
            "│          │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box.git   │\n"  # noqa: E501
            "│          │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box-2.git │\n"  # noqa: E501
            "│          │ Stranger in a Strange Org       │ https://github.com/onatlem/grok.git            │\n"  # noqa: E501
            "│          │ 01GWQRDA1HZNTSW7JK0KNGCYS9      │ Really? A ULID for your project name?          │\n"  # noqa: E501
            "╰──────────┴─────────────────────────────────┴────────────────────────────────────────────────╯\n"  # noqa: E501
        )  # noqa: E501

    @pytest.mark.usefixtures("projects_get_reponse")
    def test_project_list_table_with_active_project(self, config: MeltanoCloudConfig):
        config.internal_project_id = "01GWQ76M7EN1GKYGKV8P6BFKNV"  # Set active project
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "project", "list"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭──────────┬─────────────────────────────────┬────────────────────────────────────────────────╮\n"  # noqa: E501
            "│  Active  │ Name                            │ Git Repository                                 │\n"  # noqa: E501
            "├──────────┼─────────────────────────────────┼────────────────────────────────────────────────┤\n"  # noqa: E501
            "│          │ Meltano Cubed                   │ https://github.com/meltano/cubed.git           │\n"  # noqa: E501
            "│    X     │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box.git   │\n"  # noqa: E501
            "│          │ Post-Modern Data Stack in a Box │ https://github.com/meltano/pmds-in-a-box-2.git │\n"  # noqa: E501
            "│          │ Stranger in a Strange Org       │ https://github.com/onatlem/grok.git            │\n"  # noqa: E501
            "│          │ 01GWQRDA1HZNTSW7JK0KNGCYS9      │ Really? A ULID for your project name?          │\n"  # noqa: E501
            "╰──────────┴─────────────────────────────────┴────────────────────────────────────────────────╯\n"  # noqa: E501
        )  # noqa: E501

    @pytest.mark.usefixtures("projects_get_reponse")
    def test_project_list_json(
        self,
        projects: list[CloudProject],
        config: MeltanoCloudConfig,
    ):
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

    def test_project_activate_by_name(
        self,
        url_pattern: re.Pattern,
        config: MeltanoCloudConfig,
        projects: list[CloudProject],
    ):
        with aioresponses() as m:
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.get(
                url_pattern,
                status=200,
                payload={"results": [projects[0]], "pagination": None},
            )
            result = CliRunner().invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "project",
                    "activate",
                    "Meltano Cubed",
                ),
            )
        assert result.exit_code == 0, result.output
        assert result.output == "Activated Meltano Cloud project 'Meltano Cubed'\n"
        assert (
            json.loads(Path(config.config_path).read_text())["active_project_id"]
            == "01GWQ7520WNMQT0PQ6KHCC4EE1"
        )

    def test_project_activate_by_name_like_id(
        self,
        url_pattern: re.Pattern,
        config: MeltanoCloudConfig,
        projects: list[CloudProject],
    ):
        with aioresponses() as m:
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.get(url_pattern, status=404)
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.get(
                url_pattern,
                status=200,
                payload={"results": [projects[4]], "pagination": None},
            )
            result = CliRunner().invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "project",
                    "activate",
                    "01GWQRDA1HZNTSW7JK0KNGCYS9",
                ),
            )
        assert result.exit_code == 0, result.output
        assert (
            result.output
            == "Activated Meltano Cloud project '01GWQRDA1HZNTSW7JK0KNGCYS9'\n"
        )
        assert (
            json.loads(Path(config.config_path).read_text())["active_project_id"]
            == "01GWQREZ7G0526JZS9JY5H3BH9"
        )

    def test_project_activate_by_id(
        self,
        url_pattern: re.Pattern,
        config: MeltanoCloudConfig,
        projects: list[CloudProject],
    ):
        with aioresponses() as m:
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.get(
                url_pattern,
                status=200,
                payload={"results": [projects[0]], "pagination": None},
            )
            result = CliRunner().invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "project",
                    "activate",
                    "01GWQ7520WNMQT0PQ6KHCC4EE1",
                ),
            )
        assert result.exit_code == 0, result.output
        assert result.output == "Activated Meltano Cloud project 'Meltano Cubed'\n"
        assert (
            json.loads(Path(config.config_path).read_text())["active_project_id"]
            == "01GWQ7520WNMQT0PQ6KHCC4EE1"
        )

    def test_project_activate_ambigous_name_error(
        self,
        url_pattern: re.Pattern,
        config: MeltanoCloudConfig,
        projects: list[CloudProject],
    ):
        with aioresponses() as m:
            m.get(
                f"{config.base_auth_url}/oauth2/userInfo",
                status=200,
                body=json.dumps({"sub": "meltano-cloud-test"}),
            )
            m.get(
                url_pattern,
                status=200,
                payload={"results": projects[1:3], "pagination": None},
            )
            result = CliRunner().invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "project",
                    "activate",
                    "Post-Modern Data Stack in a Box",
                ),
            )
        assert result.exit_code == 1
        assert result.output == (
            "Unable to uniquely identify a Meltano Cloud project. "
            "Please specify the project using its internal ID, shown below. "
            "Note that these IDs may change at any time. "
            "To avoid this issue, please use unique project names.\n"
            "01GWQ76M7EN1GKYGKV8P6BFKNV: Post-Modern Data Stack in a Box\n"
            "01GWQW9WSW06F47Q0KVM1BV914: Post-Modern Data Stack in a Box\n"
        )
