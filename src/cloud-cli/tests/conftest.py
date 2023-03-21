from __future__ import annotations

import os
from pathlib import Path

import pytest
from pytest_structlog import StructuredLogCapture


@pytest.fixture(scope="session", autouse=True)
def config_path(tmpdir_factory: pytest.TempdirFactory) -> Path:
    """Return the path to the test configuration file."""
    directory = Path(tmpdir_factory.mktemp("test_config"))
    filepath = Path(directory).joinpath("config.json")
    filepath.touch()
    os.environ["MELTANO_CLOUD_CONFIG_PATH"] = str(filepath)
    return filepath


# Define this fixture to make all tests auto-use the structlog capture fixture.
# This ensures that log messages are not mixed with other output, yet can still
# be tested.
@pytest.fixture(autouse=True)
def log(log: StructuredLogCapture) -> StructuredLogCapture:
    return log
