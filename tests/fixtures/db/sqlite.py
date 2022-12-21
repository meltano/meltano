from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def engine_uri(tmp_path_factory, worker_id: str) -> str:
    database_path = (
        tmp_path_factory.mktemp("fixture_db_sqlite_engine_uri")
        / f"pytest_meltano_{worker_id}.db"
    )
    return f"sqlite:///{database_path.as_posix()}"
