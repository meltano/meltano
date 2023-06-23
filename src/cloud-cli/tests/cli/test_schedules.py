"""Test the schedule command."""

from __future__ import annotations

import json
import re
import typing as t

import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudProjectSchedule


class TestScheduleCommand:
    """Test the logs command."""

    def test_schedule_enable(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        path = (
            f"/schedules/v1/{tenant_resource_key}/{internal_project_id}"
            "/dev/daily/enabled"
        )
        runner = CliRunner()
        for cmd in ("enable", "disable"):
            for opts in (
                ("--deployment=dev", cmd, "--schedule=daily"),
                ("--schedule=daily", "--deployment=dev", cmd),
                (cmd, "--schedule=daily", "--deployment=dev"),
                ("--schedule=daily", cmd, "--deployment=dev"),
            ):
                httpserver.expect_oneshot_request(path).respond_with_data(status=204)
                result = runner.invoke(
                    cli,
                    ("--config-path", config.config_path, "schedule", *opts),
                )
                assert result.exit_code == 0, result.output
                assert not result.output

    def test_schedule_enable_with_default_deployment(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        path = (
            f"/schedules/v1/{tenant_resource_key}/{internal_project_id}"
            "/test-deployment/daily/enabled"
        )
        config.default_deployment_name = "test-deployment"
        config.write_to_file()
        runner = CliRunner()
        for cmd in ("enable", "disable"):
            httpserver.expect_oneshot_request(path).respond_with_data(status=204)
            result = runner.invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "schedule",
                    cmd,
                    "--schedule=daily",
                ),
            )
            assert result.exit_code == 0, result.output
            assert not result.output

    def test_schedule_enable_with_missing_deployment(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        path = (
            f"/schedules/v1/{tenant_resource_key}/{internal_project_id}"
            "/test-deployment/daily/enabled"
        )
        config.default_deployment_name = None
        config.write_to_file()
        runner = CliRunner()
        for cmd in ("enable", "disable"):
            httpserver.expect_oneshot_request(path).respond_with_data(status=204)
            result = runner.invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "schedule",
                    cmd,
                    "--schedule=daily",
                ),
            )
            assert result.exit_code == 2, result.output
            assert "A deployment name is required." in result.output

    @pytest.fixture()
    def schedules(self) -> list[CloudProjectSchedule]:
        return [
            {
                "deployment_name": "deployment 1",
                "schedule_name": "schedule 1",
                "interval": "1 2 * * *",
                "enabled": True,
            },
            {
                "deployment_name": "deployment 2",
                "schedule_name": "schedule 2",
                "interval": "15,45 */2 * * 1,3,5",
                "enabled": False,
            },
            {
                "deployment_name": "deployment 3",
                "schedule_name": "schedule 3",
                "interval": "0 0 * * 1,3,5",
                "enabled": False,
            },
        ]

    @pytest.fixture()
    def schedules_get_response(
        self,
        schedules: list[CloudProjectSchedule],
        tenant_resource_key: str,
        internal_project_id: str,
        httpserver: HTTPServer,
    ) -> None:
        path = f"/schedules/v1/{tenant_resource_key}/{internal_project_id}"
        pattern = re.compile(f"^{path}(\\?.*)?$")
        httpserver.expect_oneshot_request(pattern).respond_with_json(
            {"results": schedules, "pagination": None},
        )

    @freeze_time("2023-03-24 19:30:00")
    @pytest.mark.usefixtures("schedules_get_response")
    def test_schedule_list_table(self, config: MeltanoCloudConfig):
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "schedule", "list"),
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭──────────────┬────────────┬─────────────────────┬──────────────┬───────────╮\n"  # noqa: E501
            "│ Deployment   │ Schedule   │ Interval            │   Runs / Day │ Enabled   │\n"  # noqa: E501
            "├──────────────┼────────────┼─────────────────────┼──────────────┼───────────┤\n"  # noqa: E501
            "│ deployment 1 │ schedule 1 │ 1 2 * * *           │          1.0 │ True      │\n"  # noqa: E501
            "│ deployment 2 │ schedule 2 │ 15,45 */2 * * 1,3,5 │         10.3 │ False     │\n"  # noqa: E501
            "│ deployment 3 │ schedule 3 │ 0 0 * * 1,3,5       │          < 1 │ False     │\n"  # noqa: E501
            "╰──────────────┴────────────┴─────────────────────┴──────────────┴───────────╯\n"  # noqa: E501
        )  # noqa: E501

    @pytest.mark.usefixtures("schedules_get_response")
    def test_schedule_list_json(
        self,
        schedules: list[CloudProjectSchedule],
        config: MeltanoCloudConfig,
    ):
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "schedule",
                "list",
                "--format=json",
            ),
        )
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == schedules

    @pytest.mark.usefixtures("schedules_get_response")
    def test_schedule_list_limit_truncated(
        self,
        config: MeltanoCloudConfig,
    ):
        # Limit is strictly less than number of schedules
        result = CliRunner(mix_stderr=False).invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "schedule",
                "list",
                "--limit=1",
            ),
        )
        assert result.exit_code == 0, result.output
        assert result.stdout == (
            "╭──────────────┬────────────┬────────────┬──────────────┬───────────╮\n"
            "│ Deployment   │ Schedule   │ Interval   │   Runs / Day │ Enabled   │\n"
            "├──────────────┼────────────┼────────────┼──────────────┼───────────┤\n"
            "│ deployment 1 │ schedule 1 │ 1 2 * * *  │          1.0 │ True      │\n"
            "╰──────────────┴────────────┴────────────┴──────────────┴───────────╯\n"
        )
        assert result.stderr == (
            "Output truncated. To print more items, increase the limit using the "
            "--limit option.\n"
        )

    @pytest.mark.usefixtures("schedules_get_response")
    def test_schedule_list_limit_equal(
        self,
        config: MeltanoCloudConfig,
    ):
        # Limit is equal to number of schedules
        result = CliRunner(mix_stderr=False).invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "schedule",
                "list",
                "--limit=3",
            ),
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        assert result.output == (
            "╭──────────────┬────────────┬─────────────────────┬──────────────┬───────────╮\n"  # noqa: E501
            "│ Deployment   │ Schedule   │ Interval            │   Runs / Day │ Enabled   │\n"  # noqa: E501
            "├──────────────┼────────────┼─────────────────────┼──────────────┼───────────┤\n"  # noqa: E501
            "│ deployment 1 │ schedule 1 │ 1 2 * * *           │          1.0 │ True      │\n"  # noqa: E501
            "│ deployment 2 │ schedule 2 │ 15,45 */2 * * 1,3,5 │         10.3 │ False     │\n"  # noqa: E501
            "│ deployment 3 │ schedule 3 │ 0 0 * * 1,3,5       │          < 1 │ False     │\n"  # noqa: E501
            "╰──────────────┴────────────┴─────────────────────┴──────────────┴───────────╯\n"  # noqa: E501
        )  # noqa: E501
        assert result.stderr == ""

    @freeze_time("2023-03-24 16:00:00")
    def test_schedule_describe(
        self,
        tenant_resource_key: str,
        internal_project_id: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
    ):
        deployment_name = "test deployment name"
        schedule_name = "test schedule name"
        interval = "15,45 */8 * * 1,3,5"
        path = (
            f"/schedules/v1/{tenant_resource_key}/{internal_project_id}/"
            f"{deployment_name}/{schedule_name}"
        )

        runner = CliRunner()
        cli_args = (
            "--config-path",
            config.config_path,
            "schedule",
            "describe",
            "--deployment",
            deployment_name,
            "--schedule",
            schedule_name,
            "--num-upcoming=9",
        )
        upcoming_datetimes = (
            "2023-03-24 16:15\n"
            "2023-03-24 16:45\n"
            "2023-03-27 00:15\n"
            "2023-03-27 00:45\n"
            "2023-03-27 08:15\n"
            "2023-03-27 08:45\n"
            "2023-03-27 16:15\n"
            "2023-03-27 16:45\n"
            "2023-03-29 00:15\n"
        )
        httpserver.expect_oneshot_request(path).respond_with_json(
            {
                "deployment_name": deployment_name,
                "schedule_name": schedule_name,
                "interval": interval,
                "enabled": True,
            },
        )
        result = runner.invoke(cli, cli_args)
        assert result.exit_code == 0, result.output
        assert (
            result.output
            == (
                "Deployment name: test deployment name\n"
                "Schedule name:   test schedule name\n"
                "Interval:        15,45 */8 * * 1,3,5\n"
                "Enabled:         True\n"
                "\n"
                "Approximate starting date and time (UTC) of next 9 scheduled runs:\n"  # noqa: E501
            )
            + upcoming_datetimes
        )

        httpserver.expect_oneshot_request(path).respond_with_json(
            {
                "deployment_name": deployment_name,
                "schedule_name": schedule_name,
                "interval": interval,
                "enabled": True,
            },
        )
        result = runner.invoke(cli, (*cli_args, "--only-upcoming"))
        assert result.exit_code == 0, result.output
        assert result.output == upcoming_datetimes

        httpserver.expect_oneshot_request(path).respond_with_json(
            {
                "deployment_name": deployment_name,
                "schedule_name": schedule_name,
                "interval": interval,
                "enabled": False,
            },
        )
        result = runner.invoke(cli, cli_args)
        assert result.exit_code == 0, result.output
        assert result.output == (
            "Deployment name: test deployment name\n"
            "Schedule name:   test schedule name\n"
            "Interval:        15,45 */8 * * 1,3,5\n"
            "Enabled:         False\n"
        )
