import contextlib
import os

import pytest
import sqlalchemy


@pytest.fixture(scope="session")
def engine_uri(test_dir):
    database_path = test_dir.joinpath("pytest_meltano.db")

    try:
        database_path.unlink()
    except FileNotFoundError:
        pass

    return f"sqlite:///{database_path}"
