from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def _test_config_path(tmpdir_factory: pytest.TempdirFactory) -> str:
    """Return the path to the test configuration file."""
    directory = Path(tmpdir_factory.mktemp("test_config"))
    filepath = Path(directory).joinpath("config.json")
    filepath.touch()
    os.environ["MELTANO_CLOUD_CONFIG_PATH"] = str(filepath)
