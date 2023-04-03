"""Test the Meltano Cloud API client."""

from __future__ import annotations

from pathlib import Path

import pytest

from meltano.cloud.api.config import MeltanoCloudConfig


class TestMeltanoCloudClient:
    """Test the Meltano Cloud API client."""

    @pytest.fixture()
    def config(self, tmp_path: Path):
        path = tmp_path / "meltano-cloud.json"
        path.touch()
        return MeltanoCloudConfig(config_path=path)
