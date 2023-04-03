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
    interval_to_lookback,
    lookback_to_interval,
    process_table_row,
)

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from tests.conftest import HTTPServer


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
                "environment_name": "dev",
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
                "environment_name": "dev",
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
    assert process_table_row(execution) == expected


class TestHistoryCommand:
    """Test the history command."""

    @pytest.fixture()
    def path(self, tenant_resource_key: str, internal_project_id: str) -> str:
        return f"/history/v1/{tenant_resource_key}/{internal_project_id}"

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
                    "environment_name": "dev",
                    "schedule_name": "daily",
                    "job_name": "N/A",
                },
                {
                    "execution_id": "456",
                    "start_time": "2023-09-01T00:00:00+00:00",
                    "end_time": None,
                    "status": "STOPPED",
                    "exit_code": 1,
                    "environment_name": "dev",
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
        httpserver.expect_oneshot_request(path).respond_with_json(response_body)
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
        httpserver.assert_called_with(path=path, query={"page_size": ["10"]})
        data = json.loads(result.output)
        assert len(data) == 2

    def test_filter_schedule(
        self,
        path: str,
        config: MeltanoCloudConfig,
        response_body: dict,
        httpserver: HTTPServer,
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(response_body)
        result = CliRunner().invoke(
            cli,
            (
                "--config-path",
                config.config_path,
                "history",
                "--filter=daily",
            ),
        )

        assert result.exit_code == 0
        httpserver.assert_called_with(
            path=path,
            query={"page_size": ["10"], "schedule": ["daily"]},
        )

    @freeze_time(datetime.datetime(2023, 5, 20, tzinfo=UTC))
    @pytest.mark.parametrize(
        ("lookback", "expected_start_time"),
        (
            pytest.param("1w", "2023-05-13T00:00:00 00:00", id="1w"),
            pytest.param("1d", "2023-05-19T00:00:00 00:00", id="1d"),
            pytest.param("1h", "2023-05-19T23:00:00 00:00", id="1h"),
            pytest.param("1m", "2023-05-19T23:59:00 00:00", id="1m"),
            pytest.param("1w2d", "2023-05-11T00:00:00 00:00", id="1w2d"),
            pytest.param("1w2d3h", "2023-05-10T21:00:00 00:00", id="1w2d3h"),
            pytest.param("1w2d3h4m", "2023-05-10T20:56:00 00:00", id="1w2d3h4m"),
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
        httpserver.expect_oneshot_request(path).respond_with_json(response_body)
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
        httpserver.assert_called_with(
            path=path,
            query={"page_size": ["10"], "start_time": [expected_start_time]},
        )

    def test_invalid_lookback(self):
        runner = CliRunner()
        result = runner.invoke(cli, ("history", "--lookback", "invalid"))

        assert result.exit_code == 2
        assert "Invalid value for '--lookback'" in result.output
