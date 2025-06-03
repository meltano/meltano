from __future__ import annotations

import typing as t
from unittest.mock import Mock

import pytest
import yaml
from sqlalchemy.exc import OperationalError

from meltano.core.db import NullConnectionStringError, connect, project_engine
from meltano.core.project import Project

if t.TYPE_CHECKING:
    from pathlib import Path


class TestConnectionRetries:
    def test_ping_failure(self) -> None:
        engine_mock = Mock()

        # check if OperationalError is raised if a connection can't be made
        engine_mock.connect.side_effect = OperationalError(
            "test_error",
            "test_error",
            "test_error",
        )
        with pytest.raises(OperationalError):
            connect(engine=engine_mock, max_retries=3, retry_timeout=0.1)

        assert engine_mock.connect.call_count == 4

        # check reconnect on second call to `engine.connect`
        engine_mock.reset_mock()
        engine_mock.connect.side_effect = [
            OperationalError("test_error", "test_error", "test_error"),
            None,
        ]

        connect(engine=engine_mock, max_retries=3, retry_timeout=0.1)
        assert engine_mock.connect.call_count == 2


class TestProjectEngine:
    def test_project_engine(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        with tmp_path.joinpath("meltano.yml").open("w") as meltano_yml:
            yaml.dump(
                {
                    "project_id": "test",
                    "send_anonymous_usage_stat": False,
                    "database_uri": "$DATABASE",
                },
                meltano_yml,
            )
        monkeypatch.delenv("MELTANO_DATABASE_URI")

        project = Project(tmp_path)
        with pytest.raises(NullConnectionStringError):
            project_engine(project)
