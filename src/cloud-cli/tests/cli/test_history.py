"""Test the schedule command."""

from __future__ import annotations

import datetime
import json
import typing as t

import pytest
from click.testing import CliRunner
from freezegun import freeze_time
from hypothesis import given
from hypothesis import strategies as st

from meltano.cloud.cli import cloud as cli
from meltano.cloud.cli.history.utils import (
    LOOKBACK_PATTERN,
    UTC,
    format_history_row,
    interval_to_lookback,
    lookback_to_interval,
)

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from meltano.cloud.api.config import MeltanoCloudConfig


@given(st.from_regex(LOOKBACK_PATTERN, fullmatch=True))
def test_lookback_pattern(lookback: str):
    """Test the lookback pattern."""
    interval = lookback_to_interval(lookback)

    new_lookback = interval_to_lookback(interval)
    new_interval = lookback_to_interval(new_lookback)

    assert interval == new_interval


@pytest.mark.parametrize(
    ("execution", "expected"),
    (
        pytest.param(
            {
                "execution_id": "123",
                "start_time": "2023-09-02T00:00:00+00:00",
                "end_time": "2023-09-02T00:10:00+00:00",
                "status": "STOPPED",
                "exit_code": 0,
                "deployment_name": "dev",
                "schedule_name": "daily",
                "job_name": "N/A",
            },
            (
                "123",
                "daily",
                "dev",
                "2023-09-02 00:00:00",
                "Success",
                "00:10:00",
            ),
            id="stopped",
        ),
        pytest.param(
            {
                "execution_id": "123",
                "start_time": "2023-09-02T00:00:00+00:00",
                "end_time": None,
                "status": "RUNNING",
                "exit_code": None,
                "deployment_name": "dev",
                "schedule_name": "daily",
                "job_name": "N/A",
            },
            (
                "123",
                "daily",
                "dev",
                "2023-09-02 00:00:00",
                "Running",
                "N/A",
            ),
            id="running",
        ),
    ),
)
def test_table_rows(execution: dict, expected: tuple):
    assert format_history_row(execution) == expected


class TestHistoryCommand:
    """Test the history command."""

    @pytest.fixture()
    def path(self, tenant_resource_key: str, internal_project_id: str) -> str:
        return f"/jobs/v1/{tenant_resource_key}/{internal_project_id}"

    @pytest.fixture()
    def response_body(self) -> dict:
        return {
            "results": [
                {
                    "execution_id": "123",
                    "start_time": "2023-09-02T00:00:00+00:00",
                    "end_time": "2023-09-02T00:10:00+00:00",
                    "status": "STOPPED",
                    "exit_code": 0,
                    "deployment_name": "dev",
                    "schedule_name": "daily",
                    "job_name": "N/A",
                },
                {
                    "execution_id": "456",
                    "start_time": "2023-09-01T00:00:00+00:00",
                    "end_time": None,
                    "status": "STOPPED",
                    "exit_code": 1,
                    "deployment_name": "dev",
                    "schedule_name": "daily",
                    "job_name": "N/A",
                },
            ],
            "pagination": None,
        }

    def test_history_json(
        self,
        path: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
        response_body: dict,
    ):
        httpserver.expect_oneshot_request(
            path,
            query_string={"page_size": "11"},
        ).respond_with_json(response_body)
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "history",
                "--format=json",
            ),
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2

    def test_too_many_schedule_filters(self):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            (
                "history",
                "--schedule",
                "daily",
                "--schedule-contains",
                "_el_",
            ),
        )
        assert result.exit_code == 2
        assert (
            "Only one of --schedule, --schedule-prefix, or --schedule-contains"
            in result.output
        )

    @pytest.mark.parametrize(
        ("filter_option", "value", "expected_param"),
        (
            pytest.param(
                "--schedule",
                "daily",
                "daily",
                id="exact match",
            ),
            pytest.param(
                "--schedule-contains",
                "_el_",
                "*_el_*",
                id="contains",
            ),
            pytest.param(
                "--schedule-prefix",
                "dai",
                "dai*",
                id="prefix",
            ),
        ),
    )
    def test_filter_schedule(
        self,
        path: str,
        config: MeltanoCloudConfig,
        response_body: dict,
        httpserver: HTTPServer,
        filter_option: str,
        value: str,
        expected_param: str,
    ):
        httpserver.expect_oneshot_request(
            path,
            query_string={"page_size": "11", "schedule": expected_param},
        ).respond_with_json(response_body)
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "history",
                f"{filter_option}={value}",
            ),
        )

        assert result.exit_code == 0

    def test_multiple_filters(
        self,
        path: str,
        config: MeltanoCloudConfig,
        response_body: dict,
        httpserver: HTTPServer,
    ):
        httpserver.expect_oneshot_request(
            path,
            query_string={
                "page_size": "11",
                "schedule": "gitlab_el",
                "deployment": "ci*",
                "result": "failed",
            },
        ).respond_with_json(response_body)
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "history",
                "--schedule=gitlab_el",
                "--deployment-prefix=ci",
                "--result=failed",
            ),
        )

        assert result.exit_code == 0

    @freeze_time(datetime.datetime(2023, 5, 20, tzinfo=UTC))
    @pytest.mark.parametrize(
        ("lookback", "expected_start_time"),
        (
            pytest.param("1w", "2023-05-13T00:00:00+00:00", id="1w"),
            pytest.param("1d", "2023-05-19T00:00:00+00:00", id="1d"),
            pytest.param("1h", "2023-05-19T23:00:00+00:00", id="1h"),
            pytest.param("1m", "2023-05-19T23:59:00+00:00", id="1m"),
            pytest.param("1w2d", "2023-05-11T00:00:00+00:00", id="1w2d"),
            pytest.param("1w2d3h", "2023-05-10T21:00:00+00:00", id="1w2d3h"),
            pytest.param("1w2d3h4m", "2023-05-10T20:56:00+00:00", id="1w2d3h4m"),
        ),
    )
    def test_lookback(
        self,
        lookback: str,
        expected_start_time: str,
        path: str,
        config: MeltanoCloudConfig,
        response_body: dict,
        httpserver: HTTPServer,
    ):
        httpserver.expect_oneshot_request(
            path,
            query_string={
                "page_size": "11",
                "start_time": expected_start_time,
            },
        ).respond_with_json(response_body)
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "history",
                f"--lookback={lookback}",
            ),
        )
        assert result.exit_code == 0
        httpserver.check_assertions()

    def test_invalid_lookback(self):
        runner = CliRunner()
        result = runner.invoke(cli, ("history", "--lookback", "invalid"))

        assert result.exit_code == 2
        assert "Invalid value for '--lookback'" in result.output

    def test_history_table(
        self,
        path: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
        response_body: dict,
    ):
        httpserver.expect_oneshot_request(
            path,
            query_string={"page_size": "11"},
        ).respond_with_json(response_body)
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "history",
            ),
        )
        assert result.exit_code == 0
        assert result.stdout == (
            "╭────────────────┬─────────────────┬──────────────┬─────────────────────┬──────────┬────────────╮\n"  # noqa: E501
            "│   Execution ID │ Schedule Name   │ Deployment   │ Executed At (UTC)   │ Result   │ Duration   │\n"  # noqa: E501
            "├────────────────┼─────────────────┼──────────────┼─────────────────────┼──────────┼────────────┤\n"  # noqa: E501
            "│            123 │ daily           │ dev          │ 2023-09-02 00:00:00 │ Success  │ 00:10:00   │\n"  # noqa: E501
            "│            456 │ daily           │ dev          │ 2023-09-01 00:00:00 │ Failed   │ N/A        │\n"  # noqa: E501
            "╰────────────────┴─────────────────┴──────────────┴─────────────────────┴──────────┴────────────╯\n"  # noqa: E501
        )  # noqa: E501

    def test_history_table_limit(
        self,
        path: str,
        config: MeltanoCloudConfig,
        httpserver: HTTPServer,
        response_body: dict,
    ):
        httpserver.expect_oneshot_request(
            path,
            query_string={"page_size": "2"},
        ).respond_with_json(response_body)
        result = CliRunner(mix_stderr=False).invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "history",
                "--limit",
                "1",
            ),
        )
        assert result.exit_code == 0
        assert result.stdout == (
            "╭────────────────┬─────────────────┬──────────────┬─────────────────────┬──────────┬────────────╮\n"  # noqa: E501
            "│   Execution ID │ Schedule Name   │ Deployment   │ Executed At (UTC)   │ Result   │ Duration   │\n"  # noqa: E501
            "├────────────────┼─────────────────┼──────────────┼─────────────────────┼──────────┼────────────┤\n"  # noqa: E501
            "│            123 │ daily           │ dev          │ 2023-09-02 00:00:00 │ Success  │ 00:10:00   │\n"  # noqa: E501
            "╰────────────────┴─────────────────┴──────────────┴─────────────────────┴──────────┴────────────╯\n"  # noqa: E501
        )  # noqa: E501
        assert result.stderr == (
            "Output truncated due to reaching the item limit. To print more items, "
            "increase the limit using the --limit flag.\n"
        )
