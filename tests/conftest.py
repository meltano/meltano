import logging
import os
from http import HTTPStatus
from pathlib import Path
from typing import Any

import pytest
from _pytest.monkeypatch import MonkeyPatch  # noqa: WPS436 (protected module)
from requests import PreparedRequest

logging.basicConfig(level=logging.INFO)

PYTEST_BACKEND = os.getenv("PYTEST_BACKEND", "sqlite")

pytest_plugins = [
    "fixtures.db",
    "fixtures.fs",
    "fixtures.core",
    "fixtures.api",
    "fixtures.cli",
]

if PYTEST_BACKEND == "sqlite":
    pytest_plugins.append("fixtures.db.sqlite")
elif PYTEST_BACKEND == "postgresql":
    pytest_plugins.append("fixtures.db.postgresql")
else:
    raise Exception(f"Unsuported backend: {PYTEST_BACKEND}.")

BACKEND = ["sqlite", "postgresql"]


def pytest_runtest_setup(item):
    backend_marker = item.get_closest_marker("backend")

    # currently, there is no distinction between the SYSTEM database
    # and the WAREHOUSE database at the test level.
    # There is only one database used for the tests, and it serves
    # both as SYSTEM and WAREHOUSE.
    if backend_marker and backend_marker.args[0] != PYTEST_BACKEND:
        pytest.skip()


@pytest.fixture(scope="session")
def concurrency():
    return {
        "threads": int(os.getenv("PYTEST_CONCURRENCY_THREADS", 8)),
        "processes": int(os.getenv("PYTEST_CONCURRENCY_PROCESSES", 8)),
        "cases": int(os.getenv("PYTEST_CONCURRENCY_CASES", 64)),  # noqa: WPS432
    }


@pytest.fixture(scope="session", autouse=True)
def setup_env():
    monkeypatch = MonkeyPatch()
    monkeypatch.setenv("MELTANO_DISABLE_TRACKING", "True")

    yield

    monkeypatch.undo()


@pytest.fixture(scope="session")
def mock_hub_responses_dir():
    return Path(__file__).parent.joinpath("fixtures", "hub")


@pytest.fixture(scope="session")
def get_hub_response(mock_hub_responses_dir: Path):
    def _get_response(request: PreparedRequest) -> Any:
        endpoint_mapping = {
            "/plugins/extractors/index": "extractors.json",
            "/plugins/loaders/index": "loaders.json",
            "/plugins/extractors/tap-mock--meltano": "tap-mock--meltano.json",
        }

        _, endpoint = request.path_url.split("/meltano/api/v1")

        try:
            filename = endpoint_mapping[endpoint]
        except KeyError:
            return (HTTPStatus.NOT_FOUND, {}, '{"error": "not found"}')

        file_path = mock_hub_responses_dir / filename
        return (
            HTTPStatus.OK,
            {"Content-Type": "application/json"},
            file_path.read_text(),
        )

    return _get_response
