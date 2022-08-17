from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def engine_uri(tmp_path_factory) -> str:
    database_path = (
        tmp_path_factory.mktemp("fixture_db_sqlite_engine_uri") / "pytest_meltano.db"
    )
    return f"sqlite:///{database_path.as_posix()}"
