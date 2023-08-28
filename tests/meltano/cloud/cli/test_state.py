"""Test the state command."""

from __future__ import annotations

import json
import typing as t
from http import HTTPStatus
from pathlib import Path

import pytest
from click.testing import CliRunner

from meltano.cloud.cli import cloud as cli

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

    from meltano.cloud.api.config import MeltanoCloudConfig


class TestStateCommand:
    """Test cloud state command."""

    @pytest.fixture()
    def path(self, tenant_resource_key: str, internal_project_id: str) -> str:
        return f"/state/v1/{tenant_resource_key}/{internal_project_id}"

    @pytest.fixture()
    def state_ids(self):
        return [
            "dev:tap-github-to-target-jsonl",
            "prod:tap-hubspot-to-target-redshift",
        ]

    @pytest.fixture()
    def mock_s3_path(self):
        return "/some_trk/some_pid/STATE/env:some-state-id/state.json"

    @pytest.fixture()
    def mock_state(self):
        return {"completed": {"singer_state": {"bookmarks": [{"a": 1}, {"b": 2}]}}}

    @pytest.fixture()
    def mock_s3_url(self, httpserver: HTTPServer, mock_s3_path: str):
        return httpserver.url_for(mock_s3_path)

    def test_state_list(
        self,
        config: MeltanoCloudConfig,
        path: str,
        state_ids: list[str],
        httpserver: HTTPServer,
    ):
        httpserver.expect_oneshot_request(path).respond_with_json(state_ids)
        result = CliRunner().invoke(
            cli,
            ("--config-path", config.config_path, "state", "list"),
        )
        assert result.exit_code == 0, result.output
        for state_id in state_ids:
            assert state_id in result.output

    def test_state_get(
        self,
        config: MeltanoCloudConfig,
        path: str,
        mock_s3_path: str,
        mock_s3_url: str,
        mock_state,
        state_ids: list[str],
        httpserver: HTTPServer,
    ):
        for state_id in state_ids:
            httpserver.expect_oneshot_request(f"{path}/{state_id}").respond_with_data(
                mock_s3_url,
            )
            httpserver.expect_oneshot_request(mock_s3_path).respond_with_json(
                mock_state,
            )
            result = CliRunner().invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "state",
                    "get",
                    "--state-id",
                    state_id,
                ),
            )
            assert result.exit_code == 0, result.output
            assert mock_state == json.loads(result.output)

    def test_state_set(
        self,
        config: MeltanoCloudConfig,
        path: str,
        tmpdir_factory: pytest.TempdirFactory,
        mock_s3_path: str,
        mock_s3_url: str,
        mock_state,
        state_ids: list[str],
        httpserver: HTTPServer,
    ):
        directory = Path(tmpdir_factory.mktemp("test_state"))
        for state_id in state_ids:
            httpserver.expect_oneshot_request(f"{path}/{state_id}").respond_with_json(
                {"url": mock_s3_url, "fields": {"key": mock_s3_path}},
            )
            filepath = Path(directory).joinpath(f"{state_id}.json")
            with open(filepath, "w+") as state_file:
                json.dump(mock_state, state_file)
            result = CliRunner().invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "state",
                    "set",
                    "--state-id",
                    state_id,
                    "--file-path",
                    str(filepath),
                ),
            )
            assert result.exit_code == 0, result.output
            assert f"Successfully set state for {state_id}" in result.output

    def test_state_delete(
        self,
        config: MeltanoCloudConfig,
        path: str,
        state_ids: list[str],
        httpserver: HTTPServer,
    ):
        for state_id in state_ids:
            httpserver.expect_oneshot_request(
                f"{path}/{state_id}",
                method="DELETE",
            ).respond_with_json({}, HTTPStatus.NO_CONTENT)
            result = CliRunner().invoke(
                cli,
                (
                    "--config-path",
                    config.config_path,
                    "state",
                    "delete",
                    "--state-id",
                    state_id,
                ),
            )
            assert result.exit_code == 0, result.output
            assert f"Successfully deleted state for {state_id}" in result.output
